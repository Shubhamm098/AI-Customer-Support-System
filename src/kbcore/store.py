import re
import sqlite3
from pathlib import Path

import numpy as np

from kbcore import embedder

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "kb.db"
KB_DIR = ROOT / "data" / "kb"

MAX_PER_ARTICLE = 1
RRF_K = 60
CANDIDATES = 20
STOPWORDS = {"the", "a", "an", "is", "are", "to", "of", "and", "or", "i", "my", "me",
             "do", "does", "can", "how", "what", "it", "in", "on", "for", "be", "have"}


def connect(db_path=None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        DROP TABLE IF EXISTS articles;
        DROP TABLE IF EXISTS chunks;
        DROP TABLE IF EXISTS chunks_fts;
        CREATE TABLE articles (id TEXT PRIMARY KEY, title TEXT, body TEXT);
        CREATE TABLE chunks (
            id INTEGER PRIMARY KEY, article_id TEXT, heading TEXT,
            text TEXT, embedding BLOB
        );
        CREATE VIRTUAL TABLE chunks_fts USING fts5(title, heading, text);
    """)


def parse_article(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0].lstrip("# ").strip()
    chunks, heading, buf = [], "Overview", []

    def flush():
        text = "\n".join(buf).strip()
        if text:
            chunks.append({"heading": heading, "text": text})

    for line in lines[1:]:
        if line.startswith("## "):
            flush()
            heading, buf = line[3:].strip(), []
        else:
            buf.append(line)
    flush()
    return {"id": path.stem, "title": title, "body": path.read_text(encoding="utf-8"),
            "chunks": chunks}


def ingest(kb_dir=None, db_path=None) -> dict:
    kb_dir = Path(kb_dir or KB_DIR)
    conn = connect(db_path)
    init_schema(conn)
    articles = [parse_article(p) for p in sorted(kb_dir.glob("*.md"))]

    all_chunks = [(a, c) for a in articles for c in a["chunks"]]
    vectors = embedder.embed([f"{a['title']}. {c['heading']}. {c['text']}" for a, c in all_chunks])

    for a in articles:
        conn.execute("INSERT INTO articles VALUES (?,?,?)", (a["id"], a["title"], a["body"]))
    for i, (a, c) in enumerate(all_chunks):
        blob = vectors[i].tobytes() if vectors is not None else None
        cur = conn.execute(
            "INSERT INTO chunks (article_id, heading, text, embedding) VALUES (?,?,?,?)",
            (a["id"], c["heading"], c["text"], blob))
        conn.execute("INSERT INTO chunks_fts (rowid, title, heading, text) VALUES (?,?,?,?)",
                     (cur.lastrowid, a["title"], c["heading"], c["text"]))
    conn.commit()
    conn.close()
    return {"articles": len(articles), "chunks": len(all_chunks),
            "embeddings": vectors is not None}


def _fts_query(q: str) -> str:
    tokens = [t for t in re.findall(r"[A-Za-z0-9]+", q.lower())
              if len(t) > 1 and t not in STOPWORDS]
    return " OR ".join(f'"{t}"' for t in tokens)


def _keyword_ranks(conn, query: str) -> list[int]:
    fts = _fts_query(query)
    if not fts:
        return []
    rows = conn.execute(
        "SELECT rowid FROM chunks_fts WHERE chunks_fts MATCH ? "
        "ORDER BY bm25(chunks_fts) LIMIT ?", (fts, CANDIDATES)).fetchall()
    return [r["rowid"] for r in rows]


def _vector_ranks(conn, query: str) -> list[int]:
    rows = conn.execute("SELECT id, embedding FROM chunks WHERE embedding IS NOT NULL").fetchall()
    if not rows:
        return []
    qv = embedder.embed([query])
    if qv is None:
        return []
    matrix = np.vstack([np.frombuffer(r["embedding"], dtype=np.float32) for r in rows])
    sims = matrix @ qv[0]
    order = np.argsort(-sims)[:CANDIDATES]
    return [rows[i]["id"] for i in order]


def search(query: str, top_k: int = 4, db_path=None) -> dict:
    conn = connect(db_path)
    kw = _keyword_ranks(conn, query)
    vec = _vector_ranks(conn, query)

    scores: dict[int, float] = {}
    for ranking in (kw, vec):
        for rank, chunk_id in enumerate(ranking):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank + 1)

    ranked = sorted(scores, key=scores.get, reverse=True)
    results, per_article = [], {}
    for cid in ranked:
        r = conn.execute(
            "SELECT c.article_id, c.heading, c.text, a.title FROM chunks c "
            "JOIN articles a ON a.id = c.article_id WHERE c.id = ?", (cid,)).fetchone()
        if per_article.get(r["article_id"], 0) >= MAX_PER_ARTICLE:
            continue
        per_article[r["article_id"]] = per_article.get(r["article_id"], 0) + 1
        results.append({"article_id": r["article_id"], "title": r["title"],
                        "heading": r["heading"], "score": round(scores[cid], 4),
                        "text": r["text"]})
        if len(results) == top_k:
            break
    conn.close()
    return {"query": query, "mode": "hybrid" if vec else "keyword_only", "results": results}





def get_article(article_id: str, db_path=None) -> dict:
    conn = connect(db_path)
    r = conn.execute("SELECT id, title, body FROM articles WHERE id = ?", (article_id,)).fetchone()
    conn.close()
    if not r:
        return {"error": "article_not_found"}
    return {"id": r["id"], "title": r["title"], "body": r["body"]}