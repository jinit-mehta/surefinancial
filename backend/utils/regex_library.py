import re
from typing import Optional, Tuple

class RegexPatterns:
    """Centralized regex patterns for all banks"""
    
    # Common patterns
    CARD_NUMBER = r"(?:XXXX|X{4}|\*{4})\s*(?:XXXX|X{4}|\*{4})\s*(?:XXXX|X{4}|\*{4})\s*(\d{4})"
    AMOUNT = r"₹?\s?([\d,]+\.?\d{0,2})"
    DATE_DMY = r"(\d{1,2}[\s\-/]\w{3}[\s\-/]\d{4})"
    DATE_MDY = r"(\w{3}[\s\-/]\d{1,2}[\s\-/]\d{4})"
    
    # HDFC patterns
    HDFC = {
        "card_variant": r"(?:Card Type|Card Name|Product)[\s:]+([A-Za-z\s]+(?:Credit Card|Card))",
        "last_4": r"(?:Card Number|Card ending|ending with)[\s:]*(?:XXXX|X{4}|\*{4})[\s\-]*(?:XXXX|X{4}|\*{4})[\s\-]*(?:XXXX|X{4}|\*{4})[\s\-]*(\d{4})",
        "billing_cycle": r"(?:Statement Date|Billing Period|Statement Period)[\s:]*(\d{1,2}[\s\-/]\w{3}[\s\-/]\d{4})[\s\-to]*(\d{1,2}[\s\-/]\w{3}[\s\-/]\d{4})",
        "due_date": r"(?:Payment Due Date|Due Date|Pay by)[\s:]*(\d{1,2}[\s\-/]\w{3}[\s\-/]\d{4})",
        "total_due": r"(?:Total Amount Due|Amount Due|Total Due|Payment Due)[\s:]*₹?\s?([\d,]+\.?\d{0,2})"
    }
    
    # ICICI patterns
    ICICI = {
        "card_variant": r"(?:Card Type|Product)[\s:]+([A-Za-z\s]+Card)",
        "last_4": r"(?:Card No\.|Card Number|ending)[\s:]*(?:XXXX|X{4})[\s\-]*(?:XXXX|X{4})[\s\-]*(?:XXXX|X{4})[\s\-]*(\d{4})",
        "billing_cycle": r"(?:Statement Date|Billing Cycle|Statement Period)[\s:]*(\d{1,2}[\s\-/]\w{3}[\s\-/]\d{4})[\s\-to]*(\d{1,2}[\s\-/]\w{3}[\s\-/]\d{4})",
        "due_date": r"(?:Payment Due Date|Payment due by|Due Date)[\s:]*(\d{1,2}[\s\-/]\w{3}[\s\-/]\d{4})",
        "total_due": r"(?:Total Amount Due|Minimum Amount Due|Total Due)[\s:]*Rs\.?\s?([\d,]+\.?\d{0,2})"
    }
    
    # SBI patterns
    SBI = {
        "card_variant": r"(?:Card Type|Card Product|Product Name)[\s:]+([A-Za-z\s]+Card)",
        "last_4": r"(?:Card Number|Card No)[\s:]*(?:XXXX|X{4})[\s\-]*(?:XXXX|X{4})[\s\-]*(?:XXXX|X{4})[\s\-]*(\d{4})",
        "billing_cycle": r"(?:Statement Date|Statement Period|Billing Period)[\s:]*(\d{1,2}[\s\-/]\w{3}[\s\-/]\d{4})[\s\-to]*(\d{1,2}[\s\-/]\w{3}[\s\-/]\d{4})",
        "due_date": r"(?:Payment Due Date|Due Date|Pay By)[\s:]*(\d{1,2}[\s\-/]\w{3}[\s\-/]\d{4})",
        "total_due": r"(?:Total Amount Due|Amount Payable|Total Due)[\s:]*Rs\.?\s?([\d,]+\.?\d{0,2})"
    }
    
    # Axis patterns
    AXIS = {
        "card_variant": r"(?:Card Name|Card Type|Product)[\s:]+([A-Za-z\s]+Credit Card)",
        "last_4": r"(?:Card Number|Card No\.)[\s:]*(?:XXXX|X{4})[\s\-]*(?:XXXX|X{4})[\s\-]*(?:XXXX|X{4})[\s\-]*(\d{4})",
        "billing_cycle": r"(?:Statement Date|Billing Period|Statement Period)[\s:]*(\d{1,2}[\s\-/]\w{3}[\s\-/]\d{4})[\s\-to]*(\d{1,2}[\s\-/]\w{3}[\s\-/]\d{4})",
        "due_date": r"(?:Payment Due Date|Due Date)[\s:]*(\d{1,2}[\s\-/]\w{3}[\s\-/]\d{4})",
        "total_due": r"(?:Total Amount Due|New Balance|Amount Due)[\s:]*INR\s?([\d,]+\.?\d{0,2})"
    }
    
    # AMEX patterns
    AMEX = {
        "card_variant": r"(?:Card Type|Product|Card Product)[\s:]+([A-Za-z\s]+Card)",
        "last_4": r"(?:Card Number|Account ending in|ending)[\s:]*(?:XXXXX|X{5})[\s\-]*(?:XXXXXX|X{6})[\s\-]*(\d{4})",
        "billing_cycle": r"(?:Statement Closing Date|Billing Period|Statement Period)[\s:]*(\w{3}[\s\-/]\d{1,2}[\s\-/]\d{4})[\s\-to]*(\w{3}[\s\-/]\d{1,2}[\s\-/]\d{4})",
        "due_date": r"(?:Payment Due Date|Please pay by)[\s:]*(\w{3}[\s\-/]\d{1,2}[\s\-/]\d{4})",
        "total_due": r"(?:Total Amount Due|New Balance|Payment Due)[\s:]*₹\s?([\d,]+\.?\d{0,2})"
    }

def extract_with_regex(pattern: str, text: str, group: int = 1) -> Optional[str]:
    """Extract data using regex pattern"""
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(group).strip() if match else None

def extract_billing_cycle(pattern: str, text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract billing cycle start and end dates"""
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None

def clean_amount(amount_str: str) -> float:
    """Convert amount string to float"""
    if not amount_str:
        return 0.0
    # Remove currency symbols and commas
    cleaned = re.sub(r'[₹Rs\.,INR\s]', '', amount_str)
    try:
        return float(cleaned)
    except:
        return 0.0