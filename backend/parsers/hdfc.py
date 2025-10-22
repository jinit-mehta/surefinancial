from .base_parser import build_base
from ..utils.regex_library import find_first

def parse(text: str):
    issuer = "HDFC"
    last4 = find_first(text, r"(\d{4})\s*(?:\)|$)", group=1)
    card_variant = find_first(text, r"(Regalia|Platinum|Titanium|Infinia)", default="Unknown")
    billing = find_first(text, r"Statement Period[:\s]*([0-9/ -]+to[0-9/ -]+)", default=None)
    billing_start, billing_end = (None, None)
    if billing:
        parts = billing.split("to")
        billing_start = parts[0].strip()
        billing_end = parts[1].strip() if len(parts) > 1 else None
    due_date = find_first(text, r"Payment Due Date[:\s]*([0-9/.-]{6,12})", default=None)
    amount_due = find_first(text, r"Total Amount Due[:\s]*₹?([\d,]+\.\d{2})", default=None)
    return build_base({
        "issuer": issuer,
        "card_variant": card_variant,
        "last4": last4,
        "billing_start": billing_start,
        "billing_end": billing_end,
        "due_date": due_date,
        "amount_due": amount_due
    })
