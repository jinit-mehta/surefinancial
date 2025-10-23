from .base_parser import BaseParser
from typing import Dict

class ICICIParser(BaseParser):
    """Enhanced ICICI Bank parser with robust extraction"""
    
    def __init__(self, text: str):
        super().__init__(text)
        self.bank_name = "ICICI Bank"
    
    def parse(self) -> Dict:
        from utils.regex_library import (
            RegexPatterns, 
            extract_card_variant,
            extract_last_4,
            calculate_confidence
        )
        
        patterns = RegexPatterns.ICICI
        
        # Extract card variant
        card_variant = extract_card_variant(patterns["card_variant"], self.text)
        if not card_variant:
            card_variant = "ICICI Credit Card"
        
        # Extract last 4 digits
        last_4 = extract_last_4(patterns["last_4"], self.text)
        if not last_4:
            last_4 = "XXXX"
        
        # Extract billing cycle
        billing_start, billing_end = self.extract_billing_cycle(patterns["billing_cycle_keywords"])
        
        # Extract due date
        due_date = self.extract_date_near_keywords(patterns["due_date_keywords"])
        
        # Extract total amount due
        total_due = self.extract_amount_near_keywords(patterns["total_due_keywords"])
        if total_due is None or total_due == 0:
            total_due = 0.0
        
        extracted_data = {
            "bank_name": self.bank_name,
            "card_variant": card_variant,
            "last_4_digits": last_4,
            "billing_cycle_start": billing_start,
            "billing_cycle_end": billing_end,
            "due_date": due_date,
            "total_amount_due": total_due,
            "currency": "INR"
        }
        
        # Calculate confidence scores
        confidence = calculate_confidence(extracted_data)
        extracted_data['confidence_scores'] = confidence
        
        # Add warnings
        warnings = []
        if confidence['total_amount_due'] < 0.5:
            warnings.append("Amount extraction has low confidence - manual verification recommended")
        if not billing_start or not billing_end:
            warnings.append("Billing cycle dates may be incomplete")
        
        extracted_data['warnings'] = warnings
        
        return extracted_data