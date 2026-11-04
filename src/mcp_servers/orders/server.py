import sys
sys.path.insert(0, "src")
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from common.db import SessionLocal, Order

mcp = FastMCP("orders-mcp")
RETURN_WINDOW_DAYS = 30

@mcp.tool()
def get_order(order_id: str) -> dict:
    """Fetch an order by ID."""
    with SessionLocal() as s:
        o = s.get(Order, order_id)
        if not o:
            return {"error": "order_not_found"}
        return {"id": o.id, "customer_id": o.customer_id, "item": o.item,
                "amount": o.amount, "status": o.status,
                "placed_at": o.placed_at.isoformat()}

@mcp.tool()
def check_refund_eligibility(order_id: str) -> dict:
    """Deterministic refund eligibility check (no LLM involved)."""
    with SessionLocal() as s:
        o = s.get(Order, order_id)
        if not o:
            return {"eligible": False, "reason": "order_not_found"}
        age = (datetime.utcnow() - o.placed_at).days
        if o.status == "refunded":
            return {"eligible": False, "reason": "already_refunded"}
        if age > RETURN_WINDOW_DAYS:
            return {"eligible": False, "reason": f"outside_return_window ({age} days)"}
        return {"eligible": True, "reason": "within_policy", "amount": o.amount}

if __name__ == "__main__":
    mcp.run()  # stdio transport for now