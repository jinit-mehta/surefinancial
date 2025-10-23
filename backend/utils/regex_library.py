import re
from typing import Optional, Tuple, Dict, List

class RegexPatterns:
    """Enhanced regex patterns with multiple fallback strategies"""
    
    # Multiple amount patterns to handle different formats
    AMOUNT_PATTERNS = [
        r"₹\s*([\d,]+\.?\d{0,2})",  # ₹ 12,345.67
        r"Rs\.?\s*([\d,]+\.?\d{0,2})",  # Rs. 12,345.67 or Rs 12345.67
        r"INR\s*([\d,]+\.?\d{0,2})",  # INR 12,345.67
        r"([\d,]+\.?\d{2})\s*(?:₹|Rs\.?|INR)",  # 12,345.67 ₹
        r"(?:^|\s)([\d,]+\.?\d{0,2})(?:\s|$)",  # Plain number with context
    ]
    
    # Multiple date patterns
    DATE_PATTERNS = [
        r"(\d{1,2}[\s\-/]\w{3,9}[\s\-/]\d{4})",  # 15 Jan 2024 or 15-Jan-2024
        r"(\d{1,2}[\s\-/]\d{1,2}[\s\-/]\d{4})",  # 15/01/2024 or 15-01-2024
        r"(\w{3,9}[\s\-/]\d{1,2}[\s\-/]\d{4})",  # Jan 15 2024
        r"(\d{4}[\s\-/]\d{1,2}[\s\-/]\d{1,2})",  # 2024-01-15
    ]
    
    # Card number patterns
    CARD_PATTERNS = [
        r"(?:XXXX|X{4}|\*{4})[\s\-]*(?:XXXX|X{4}|\*{4})[\s\-]*(?:XXXX|X{4}|\*{4})[\s\-]*(\d{4})",
        r"(?:ending|ends)\s+(?:in|with)[\s:]*(\d{4})",
        r"Card\s+(?:No\.?|Number)[\s:]*\*+[\s\-]*(\d{4})",
    ]
    
    # HDFC patterns with multiple variations
    HDFC = {
        "card_variant": [
            r"(?:Card\s+Type|Card\s+Name|Product)[\s:]+([A-Za-z\s]+(?:Credit\s+Card|Card))",
            r"(Regalia|MoneyBack|Diners\s+Club|Infinia)[\s\w]*(?:Credit\s+)?Card",
        ],
        "last_4": CARD_PATTERNS,
        "billing_cycle_keywords": ["Statement Period", "Billing Period", "Statement Date"],
        "due_date_keywords": ["Payment Due Date", "Due Date", "Pay by", "Pay By"],
        "total_due_keywords": ["Total Amount Due", "Amount Due", "Total Due", "Payment Due"],
    }
    
    # ICICI patterns
    ICICI = {
        "card_variant": [
            r"(?:Product|Card\s+Type)[\s:]+([A-Za-z\s]+Card)",
            r"(Coral|Platinum|Amazon\s+Pay|Sapphiro)[\s\w]*Card",
        ],
        "last_4": CARD_PATTERNS,
        "billing_cycle_keywords": ["Statement Period", "Billing Cycle", "Statement Date"],
        "due_date_keywords": ["Payment due by", "Payment Due Date", "Due Date"],
        "total_due_keywords": ["Total Amount Due", "Minimum Amount Due", "Total Due"],
    }
    
    # SBI patterns
    SBI = {
        "card_variant": [
            r"(?:Card\s+Product|Card\s+Type|Product\s+Name)[\s:]+([A-Za-z\s]+Card)",
            r"(SimplyCLICK|Prime|Elite|BPCL)[\s\w]*Card",
        ],
        "last_4": CARD_PATTERNS,
        "billing_cycle_keywords": ["Statement Period", "Billing Period", "Statement Date"],
        "due_date_keywords": ["Payment Due Date", "Due Date", "Pay By"],
        "total_due_keywords": ["Total Amount Payable", "Amount Payable", "Total Due"],
    }
    
    # Axis patterns
    AXIS = {
        "card_variant": [
            r"(?:Card\s+Name|Card\s+Type|Product)[\s:]+([A-Za-z\s]+Credit\s+Card)",
            r"(Flipkart|Vistara|Ace|Select)[\s\w]*Credit\s+Card",
        ],
        "last_4": CARD_PATTERNS,
        "billing_cycle_keywords": ["Billing Period", "Statement Period", "Statement Date"],
        "due_date_keywords": ["Payment Due Date", "Due Date"],
        "total_due_keywords": ["New Balance", "Total Amount Due", "Amount Due"],
    }
    
    # AMEX patterns
    AMEX = {
        "card_variant": [
            r"(?:Card\s+Product|Product|Card\s+Type)[\s:]+([A-Za-z\s]+Card)",
            r"(Platinum|Gold|Membership\s+Rewards|SmartEarn)[\s\w]*Card",
        ],
        "last_4": [
            r"(?:Account\s+ending\s+in|ending)[\s:]*(\d{4,5})",
            r"Card[\s:]*\*+[\s\-]*(\d{4,5})",
        ] + CARD_PATTERNS,
        "billing_cycle_keywords": ["Statement Period", "Billing Period", "Statement Closing Date"],
        "due_date_keywords": ["Please pay by", "Payment Due Date", "Due Date"],
        "total_due_keywords": ["Payment Due", "Total Amount Due", "New Balance"],
    }


def extract_with_multiple_patterns(patterns: List[str], text: str, context_window: int = 50) -> Optional[str]:
    """Try multiple patterns and return first match"""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def extract_amount_near_keyword(text: str, keywords: List[str]) -> Optional[float]:
    """Extract amount near specified keywords with confidence scoring"""
    text_lower = text.lower()
    
    for keyword in keywords:
        # Find keyword position
        keyword_pos = text_lower.find(keyword.lower())
        if keyword_pos == -1:
            continue
        
        # Extract context around keyword (200 chars forward)
        context = text[keyword_pos:keyword_pos + 200]
        
        # Try all amount patterns
        for pattern in RegexPatterns.AMOUNT_PATTERNS:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                amount_str = match.group(1)
                amount = clean_amount(amount_str)
                if amount > 0:  # Valid amount
                    return amount
    
    return None


def extract_date_near_keyword(text: str, keywords: List[str]) -> Optional[str]:
    """Extract date near specified keywords"""
    text_lower = text.lower()
    
    for keyword in keywords:
        keyword_pos = text_lower.find(keyword.lower())
        if keyword_pos == -1:
            continue
        
        # Extract context around keyword
        context = text[keyword_pos:keyword_pos + 150]
        
        # Try all date patterns
        for pattern in RegexPatterns.DATE_PATTERNS:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1).strip()
    
    return None


def extract_billing_cycle_smart(text: str, keywords: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """Extract billing cycle with improved logic"""
    text_lower = text.lower()
    
    for keyword in keywords:
        keyword_pos = text_lower.find(keyword.lower())
        if keyword_pos == -1:
            continue
        
        context = text[keyword_pos:keyword_pos + 200]
        
        # Look for "date to date" pattern
        date_range_pattern = r"(\d{1,2}[\s\-/]\w{3,9}[\s\-/]\d{4})[\s\-to]+(\d{1,2}[\s\-/]\w{3,9}[\s\-/]\d{4})"
        match = re.search(date_range_pattern, context, re.IGNORECASE)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        
        # Try alternate format
        alt_pattern = r"(\d{1,2}[\s\-/]\d{1,2}[\s\-/]\d{4})[\s\-to]+(\d{1,2}[\s\-/]\d{1,2}[\s\-/]\d{4})"
        match = re.search(alt_pattern, context, re.IGNORECASE)
        if match:
            return match.group(1).strip(), match.group(2).strip()
    
    return None, None


def clean_amount(amount_str: str) -> float:
    """Convert amount string to float with better error handling"""
    if not amount_str:
        return 0.0
    
    # Remove all non-numeric characters except decimal point
    cleaned = re.sub(r'[^\d.]', '', amount_str)
    
    try:
        amount = float(cleaned)
        # Sanity check - credit card amounts typically between 100 and 10,000,000
        if 100 <= amount <= 10000000:
            return round(amount, 2)
        return 0.0
    except (ValueError, AttributeError):
        return 0.0


def extract_card_variant(patterns: List[str], text: str) -> Optional[str]:
    """Extract card variant with fallback"""
    result = extract_with_multiple_patterns(patterns, text)
    if result:
        # Clean up extra whitespace
        return ' '.join(result.split())
    return None


def extract_last_4(patterns: List[str], text: str) -> Optional[str]:
    """Extract last 4 digits with validation"""
    result = extract_with_multiple_patterns(patterns, text)
    if result and result.isdigit() and len(result) >= 4:
        return result[-4:]  # Take last 4 digits
    return None


def calculate_confidence(extracted_data: Dict) -> Dict[str, float]:
    """Calculate confidence scores for extracted fields"""
    confidence = {}
    
    # Bank name - high confidence if detected
    confidence['bank_name'] = 1.0 if extracted_data.get('bank_name') else 0.0
    
    # Card variant
    confidence['card_variant'] = 0.9 if extracted_data.get('card_variant') else 0.0
    
    # Last 4 digits
    last_4 = extracted_data.get('last_4_digits', '')
    confidence['last_4_digits'] = 1.0 if last_4 and last_4.isdigit() else 0.0
    
    # Billing cycle
    has_billing = extracted_data.get('billing_cycle_start') and extracted_data.get('billing_cycle_end')
    confidence['billing_cycle'] = 0.95 if has_billing else 0.0
    
    # Due date
    confidence['due_date'] = 0.95 if extracted_data.get('due_date') else 0.0
    
    # Amount - critical field
    amount = extracted_data.get('total_amount_due', 0)
    if amount > 100:
        confidence['total_amount_due'] = 0.98
    elif amount > 0:
        confidence['total_amount_due'] = 0.5  # Low confidence for small amounts
    else:
        confidence['total_amount_due'] = 0.0
    
    # Overall confidence
    total_confidence = sum(confidence.values()) / len(confidence)
    confidence['overall'] = round(total_confidence, 2)
    
    return confidence