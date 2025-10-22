from .hdfc_parser import HDFCParser
from .icici_parser import ICICIParser
from .sbi_parser import SBIParser
from .axis_parser import AxisParser
from .amex_parser import AMEXParser

PARSER_MAP = {
    "hdfc": HDFCParser,
    "icici": ICICIParser,
    "sbi": SBIParser,
    "axis": AxisParser,
    "amex": AMEXParser
}

def get_parser(bank: str, text: str):
    """Factory function to get appropriate parser"""
    parser_class = PARSER_MAP.get(bank.lower())
    if parser_class:
        return parser_class(text)
    return None