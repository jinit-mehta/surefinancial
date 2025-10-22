# provide helper functions for parsers (shared functions)
from ..utils.regex_library import find_first, find_date_range

def build_base(fields):
    # returns consistent structure
    return {
        "issuer": fields.get("issuer"),
        "card_variant": fields.get("card_variant"),
        "last4": fields.get("last4"),
        "billing_start": fields.get("billing_start"),
        "billing_end": fields.get("billing_end"),
        "due_date": fields.get("due_date"),
        "amount_due": fields.get("amount_due"),
    }
