from .base_parser import BaseParser
from .hdfc_parser import HDFCParser
from .icici_parser import ICICIParser
from .sbi_parser import SBIParser
from .axis_parser import AxisParser
from .amex_parser import AMEXParser

def get_parser(bank: str, text: str) -> BaseParser:
    """
    Factory function to get appropriate parser based on bank name
    
    Args:
        bank: Bank identifier (hdfc, icici, sbi, axis, amex)
        text: Extracted PDF text
        
    Returns:
        Appropriate parser instance or None
    """
    bank_lower = bank.lower()
    
    parser_map = {
        "hdfc": HDFCParser,
        "icici": ICICIParser,
        "sbi": SBIParser,
        "axis": AxisParser,
        "amex": AMEXParser
    }
    
    parser_class = parser_map.get(bank_lower)
    if parser_class:
        return parser_class(text)
    return None

__all__ = [
    'BaseParser',
    'HDFCParser',
    'ICICIParser',
    'SBIParser',
    'AxisParser',
    'AMEXParser',
    'get_parser'
]