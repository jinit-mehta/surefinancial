from .base_parser import build_base
from ..utils.regex_library import find_first

def parse(text: str):
    issuer = "AXIS"
    last4 = find_first(text, r"Card Number[:\s]*.*(\d{4})", default=find_first(text, r"(\d{4})\b"))
    card_variant = find_first(text, r"(Vistara|MyZone|Magnus|Ace|Platinum)", default="Unknown")
    billing = find_first(text, r"Statement Period[:\s]*([0-9/.\- ]+to[0-9/.\- ]+)")
    billing_start = billing_end = None
    if billing:
        parts = billing.split("to")
        billing_start = parts[0].strip()
        billing_end = parts[1].strip() if len(parts) > 1 else None
    due_date = find_first(text, r"(?:Due Date|Payment Due Date|Last Date to Pay)[:\s]*([0-9/.\-]{6,12})")
    amount_due = find_first(text, r"(?:Amount Due|Total Due|Balance Due)[:\s]*₹?([\d,]+\.\d{2})")
    return build_base({
        "issuer": issuer,
        "card_variant": card_variant,
        "last4": last4,
        "billing_start": billing_start,
        "billing_end": billing_end,
        "due_date": due_date,
        "amount_due": amount_due
    })
