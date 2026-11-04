import json
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from kbcore import store

mcp = FastMCP("kb-mcp")
POLICIES_PATH = store.ROOT / "data" / "policies.json"


def _load_policies() -> dict:
    return json.loads(POLICIES_PATH.read_text(encoding="utf-8"))


@mcp.tool()
def search_articles(
    query: Annotated[str, Field(min_length=2, max_length=300)],
    top_k: Annotated[int, Field(ge=1, le=10)] = 4,
) -> dict:
    """Search support articles (hybrid keyword + semantic). Returns chunks with
    article IDs for citation. Use get_policy for exact rules, not this tool."""
    return store.search(query, top_k)


@mcp.tool()
def get_article(article_id: str) -> dict:
    """Fetch a full article by ID (as returned by search_articles)."""
    return store.get_article(article_id)


@mcp.tool()
def get_policy(policy_name: str) -> dict:
    """Exact, structured policy values (limits, windows). Deterministic: never
    goes through search. Use this for any rule the Policy Guard must enforce."""
    policies = _load_policies()
    if policy_name not in policies:
        return {"error": "policy_not_found", "available": sorted(policies)}
    return {"name": policy_name, "values": policies[policy_name]}


if __name__ == "__main__":
    mcp.run()