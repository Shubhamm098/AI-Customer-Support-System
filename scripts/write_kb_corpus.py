from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "kb"
OUT.mkdir(parents=True, exist_ok=True)

ARTICLES = {
"refund_policy": """# Refund Policy
## Eligibility
## Return window
You can return an item and request a refund within 30 days of delivery. Orders older than 30 days are not eligible. Gold members have an extended 45-day return window.
## Amount limits
Refunds up to $500 are processed automatically after verification. Refunds above $500 require approval from a human support agent.
## One refund per order
Each order can be refunded only once. Orders already marked as refunded cannot be refunded again.
## Timing
Approved refunds reach the original payment method within 5 to 7 business days.
""",
"return_process": """# How to Return an Item
## Steps
Request a return from the support chat, receive a prepaid return label by email, and ship the item within 7 days of receiving the label.
## Condition
Items must be unused and in original packaging. Opened software and personal care items cannot be returned.
## After we receive it
Once the warehouse inspects the item, the refund is issued to the original payment method.
""",
"shipping_times": """# Shipping Times
## Standard shipping
Standard shipping takes 3 to 5 business days after the order ships.
## Express shipping
Express shipping takes 1 to 2 business days and costs extra.
## Delays
Public holidays and severe weather can delay delivery by several days. Orders are marked shipped once handed to the carrier.
""",
"order_tracking": """# Tracking Your Order
## Finding your tracking number
A tracking number is emailed when your order ships. You can also find it in the order details page.
## Status meanings
Placed means payment is confirmed. Shipped means the carrier has the package. Delivered means the carrier reports drop-off.
## Package marked delivered but missing
Check with neighbours and the building front desk, wait 24 hours, then contact support to open an investigation with the carrier.
""",
"damaged_or_wrong_item": """# Damaged or Wrong Item Received
## Report it quickly
Report damaged items or wrong items within 14 days of delivery. Include a photo of the item and the shipping label.
## Resolution
We offer a replacement or a full refund. Refunds for damaged items follow the standard refund policy limits for automatic approval.
## Evidence
Photos help verify the claim. Our system may read order numbers from photos or screenshots you upload.
""",
"password_reset": """# Resetting Your Password
## Self-service reset
Choose Forgot password on the login page. A reset link is sent to the verified email on the account and expires after 30 minutes.
## Limits
For security, a maximum of 3 password resets are allowed per day per account.
## No access to email
If you can no longer access your registered email, support must verify your identity before changing it.
""",
"account_locked": """# Account Locked
## Why it happens
Accounts lock after 5 failed login attempts or when unusual activity is detected.
## Unlocking
Locks clear automatically after 30 minutes. You can also unlock immediately by resetting your password.
## Suspicious activity
If you did not attempt those logins, change your password and enable two-factor authentication.
""",
"warranty_terms": """# Warranty Terms
## Coverage period
Electronics carry a 12-month limited warranty from the delivery date.
## What is covered
Manufacturing defects are covered. Accidental damage, water damage, and normal wear are not covered.
## Claims
Contact support with your order number. Warranty replacements are separate from the 30-day refund window.
""",
"payment_failed": """# Payment Failed or Charged Twice
## Payment declined
Check card details, available balance, and whether your bank blocked the transaction, then retry.
## Charged twice
A duplicate pending authorization usually disappears within 3 to 5 business days. If both charges settle, contact support for a refund of the duplicate.
## Refund timing
Refunds for duplicate charges follow the standard 5 to 7 business day timeline.
""",
"address_change": """# Changing Your Shipping Address
## Before shipping
The address can be changed free of charge until the order is marked as shipped.
## After shipping
Once shipped, the address cannot be changed. You can refuse delivery or arrange a redirect with the carrier.
""",
"cancel_order": """# Cancelling an Order
## Before shipping
Orders can be cancelled at no cost until they are marked shipped. The payment is reversed within 3 business days.
## After shipping
Shipped orders cannot be cancelled. Once delivered, use the return process and refund policy instead.
""",
"gold_membership": """# Gold Membership Benefits
## Benefits
Gold members get a 45-day return window, free express shipping, and priority support.
## Escalations
Gold members are routed to a human agent faster when a refund request is denied.
""",
}

for name, body in ARTICLES.items():
    (OUT / f"{name}.md").write_text(body, encoding="utf-8")
print(f"Wrote {len(ARTICLES)} articles to {OUT}")