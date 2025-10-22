from .base_parser import BaseParser
from utils.regex_library import RegexPatterns, extract_with_regex, extract_billing_cycle, clean_amount
from typing import Dict

class AxisParser(BaseParser):
    def __init__(self, text: str):
        super().__init__(text)
        self.bank_name = "Axis Bank"
    
    def parse(self) -> Dict:
        patterns = RegexPatterns.AXIS
        
        card_variant = extract_with_regex(patterns["card_variant"], self.text) or "Axis Credit Card"
        last_4 = extract_with_regex(patterns["last_4"], self.text) or "XXXX"
        
        billing_start, billing_end = extract_billing_cycle(patterns["billing_cycle"], self.text)
        due_date = extract_with_regex(patterns["due_date"], self.text)
        total_due_str = extract_with_regex(patterns["total_due"], self.text)
        total_due = clean_amount(total_due_str) if total_due_str else 0.0
        
        return {
            "bank_name": self.bank_name,
            "card_variant": card_variant,
            "last_4_digits": last_4,
            "billing_cycle_start": billing_start,
            "billing_cycle_end": billing_end,
            "due_date": due_date,
            "total_amount_due": total_due,
            "currency": "INR"
        }