import pdfplumber
from typing import Optional

def extract_text_pdfplumber(pdf_path: str) -> str:
    """Extract text using pdfplumber"""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"pdfplumber error: {e}")
        return ""

def extract_text_hybrid(pdf_path: str) -> str:
    """Extract text - simplified to use pdfplumber only"""
    return extract_text_pdfplumber(pdf_path)

def detect_bank(text: str) -> Optional[str]:
    """Detect bank from PDF text"""
    text_lower = text.lower()
    
    bank_keywords = {
        "hdfc": ["hdfc", "hdfc bank"],
        "icici": ["icici", "icici bank"],
        "sbi": ["sbi card", "state bank", "sbi"],
        "axis": ["axis", "axis bank"],
        "amex": ["american express", "amex", "americanexpress"]
    }
    
    for bank, keywords in bank_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return bank
    
    return None