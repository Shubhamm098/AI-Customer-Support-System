import sys, random
from datetime import datetime, timedelta
from faker import Faker

sys.path.insert(0, "src")
from common.db import (
    Base, engine, SessionLocal, Customer, Order, Ticket, TicketNote,
)

fake = Faker()
random.seed(42)  # reproducible data, useful for evals later

# Wipe and recreate so the script can be run any number of times
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

now = datetime.utcnow()

with SessionLocal() as s:
    customers = [
        Customer(
            name=fake.name(),
            email=fake.unique.email().lower(),
            tier=random.choice(["standard", "standard", "gold"]),
        )
        for _ in range(50)
    ]
    s.add_all(customers)
    s.flush()

    # Regular orders
    for i in range(200):
        s.add(Order(
            id=f"ORD-{10000 + i}",
            customer_id=random.choice(customers).id,
            item=fake.catch_phrase(),
            amount=round(random.uniform(10, 900), 2),
            status=random.choice(["delivered", "delivered", "shipped"]),
            placed_at=now - timedelta(days=random.randint(1, 90)),
        ))

    # Deliberate edge cases (stable IDs for tests and evals)
    gold = next(c for c in customers if c.tier == "gold")
    s.add_all([
        Order(id="ORD-90001", customer_id=customers[0].id, item="Already refunded item",
              amount=120.00, status="refunded", placed_at=now - timedelta(days=5)),
        Order(id="ORD-90002", customer_id=customers[1].id, item="High value laptop",
              amount=2499.00, status="delivered", placed_at=now - timedelta(days=3)),
        Order(id="ORD-90003", customer_id=gold.id, item="Gold tier order",
              amount=89.99, status="delivered", placed_at=now - timedelta(days=10)),
        Order(id="ORD-90004", customer_id=customers[2].id, item="Right at window edge",
              amount=45.00, status="delivered", placed_at=now - timedelta(days=30)),
        Order(id="ORD-90005", customer_id=customers[3].id, item="Long past window",
              amount=60.00, status="delivered", placed_at=now - timedelta(days=75)),
    ])

    # Tickets
    statuses = ["open", "resolved", "resolved", "escalated", "pending"]
    for c in random.sample(customers, 30):
        for _ in range(random.randint(1, 3)):
            st = random.choice(statuses)
            created = now - timedelta(days=random.randint(1, 60))
            t = Ticket(
                customer_id=c.id,
                subject=random.choice([
                    "Where is my order?", "Request refund", "Cannot log in",
                    "Wrong item received", "Update shipping address",
                ]),
                status=st,
                channel=random.choice(["chat", "email"]),
                created_at=created,
                resolution="Resolved by support" if st == "resolved" else None,
                resolved_at=created + timedelta(hours=4) if st == "resolved" else None,
            )
            s.add(t)
            s.flush()
            s.add(TicketNote(ticket_id=t.id, author="customer", body=t.subject))

    s.commit()

print("Seeded.")