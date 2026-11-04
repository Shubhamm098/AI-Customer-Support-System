import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICIES_PATH = ROOT / "data" / "policies.json"


def load_policies() -> dict:
    return json.loads(POLICIES_PATH.read_text(encoding="utf-8"))


def get_policy(name: str) -> dict:
    return load_policies()[name]