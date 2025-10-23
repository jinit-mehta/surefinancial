from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple

class BaseParser(ABC):
    """Base class for all bank parsers with shared utilities"""
    
    def __init__(self, text: str):
        self.text = text
        self.bank_name = ""
        self.raw_text = text
    
    @abstractmethod
    def parse(self) -> Dict:
        """Parse the statement and return structured data"""
        pass
    
    def get_bank_name(self) -> str:
        return self.bank_name
    
    def extract_with_patterns(self, patterns, text=None):
        """Try multiple patterns and return first match"""
        from utils.regex_library import extract_with_multiple_patterns
        if text is None:
            text = self.text
        return extract_with_multiple_patterns(patterns, text)
    
    def extract_amount_near_keywords(self, keywords):
        """Extract amount using keyword proximity"""
        from utils.regex_library import extract_amount_near_keyword
        return extract_amount_near_keyword(self.text, keywords)
    
    def extract_date_near_keywords(self, keywords):
        """Extract date using keyword proximity"""
        from utils.regex_library import extract_date_near_keyword
        return extract_date_near_keyword(self.text, keywords)
    
    def extract_billing_cycle(self, keywords):
        """Extract billing cycle dates"""
        from utils.regex_library import extract_billing_cycle_smart
        return extract_billing_cycle_smart(self.text, keywords)