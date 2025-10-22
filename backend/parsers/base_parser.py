from abc import ABC, abstractmethod
from typing import Dict, Optional

class BaseParser(ABC):
    """Base class for all bank parsers"""
    
    def __init__(self, text: str):
        self.text = text
        self.bank_name = ""
    
    @abstractmethod
    def parse(self) -> Dict:
        """Parse the statement and return structured data"""
        pass
    
    def get_bank_name(self) -> str:
        return self.bank_name