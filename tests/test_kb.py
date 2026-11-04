import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from kbcore import store


@pytest.fixture(scope="module")
def kb(tmp_path_factory):
    db = tmp_path_factory.mktemp("kb") / "test_kb.db"
    store.ingest(db_path=db)
    return db


CASES = [
    ("how long do I have to return something", "refund_policy"),
    ("I forgot my password", "password_reset"),
    ("my account is locked after failed logins", "account_locked"),
    ("where is my package", "order_tracking"),
    ("how many days does standard delivery take", "shipping_times"),
    ("received a broken item", "damaged_or_wrong_item"),
    ("I was charged twice", "payment_failed"),
    ("can I cancel my order", "cancel_order"),
    ("change delivery address", "address_change"),
    ("what is covered under warranty", "warranty_terms"),
    ("refund over 500 dollars", "refund_policy"),
]


@pytest.mark.parametrize("query,expected", CASES)
def test_expected_article_in_top3(kb, query, expected):
    out = store.search(query, top_k=3, db_path=kb)
    ids = [r["article_id"] for r in out["results"]]
    assert expected in ids, f"{query!r} -> {ids} (mode={out['mode']})"


def test_get_article(kb):
    assert store.get_article("refund_policy", db_path=kb)["title"] == "Refund Policy"
    assert store.get_article("nope", db_path=kb) == {"error": "article_not_found"}


def test_garbage_query_does_not_crash(kb):
    out = store.search('"; DROP TABLE chunks; --', top_k=3, db_path=kb)
    assert "results" in out