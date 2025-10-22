import re

def find_first(text, pattern, group=1, default=None, flags=re.I|re.M):
    try:
        m = re.search(pattern, text, flags)
        if m:
            return m.group(group).strip()
    except Exception:
        pass
    return default

def generic_parse(text):
    issuer = find_first(text, r"(HDFC|ICICI|SBI|AXIS|AMEX)", default="UNKNOWN")
    last4 = find_first(text, r"(\d{4})\b", default=None)
    billing = find_first(text, r"Statement Period[:\s]*([0-9/ -]+to[0-9/ -]+)")
    billing_start, billing_end = (None, None)
    if billing:
        parts = billing.split("to")
        billing_start = parts[0].strip()
        billing_end = parts[1].strip() if len(parts) > 1 else None
    due_date = find_first(text, r"(?:Payment Due Date|Due Date)[:\s]*([0-9/.\-]{6,12})")
    amount = find_first(text, r"(?:Total Amount Due|Amount Due|New Balance)[:\s]*₹?([\d,]+\.\d{2})")
    return {
        "issuer": issuer,
        "last4": last4,
        "billing_start": billing_start,
        "billing_end": billing_end,
        "due_date": due_date,
        "amount_due": amount
    }
