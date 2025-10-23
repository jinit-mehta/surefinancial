#!/usr/bin/env python3
"""
Generate REALISTIC credit card statement PDFs with variations
This creates PDFs that closely match real bank statement formats
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime, timedelta
import random
import os
from pathlib import Path

OUTPUT_DIR = Path("realistic_test_statements")
NUM_FILES_PER_BANK = 5  # Generate 5 per bank for quick testing

# Realistic amounts and variations
REALISTIC_AMOUNTS = [
    # Common ranges
    (5000, 15000, 0.4),      # 40% in low range
    (15000, 50000, 0.35),    # 35% in mid range
    (50000, 150000, 0.20),   # 20% in high range
    (150000, 500000, 0.05),  # 5% in very high range
]

def generate_realistic_amount():
    """Generate realistic credit card amounts"""
    rand = random.random()
    cumulative = 0
    
    for min_amt, max_amt, probability in REALISTIC_AMOUNTS:
        cumulative += probability
        if rand <= cumulative:
            return round(random.uniform(min_amt, max_amt), 2)
    
    return round(random.uniform(5000, 50000), 2)


def create_hdfc_realistic(pdf_path, data, variation=0):
    """Create realistic HDFC statement with variations"""
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    
    # Add variation in layout
    y_offset = height - (1 + variation * 0.1) * inch
    
    # Header - vary font sizes slightly
    c.setFont("Helvetica-Bold", 20 + variation)
    c.drawString(1*inch, y_offset, "HDFC Bank Ltd.")
    
    y_offset -= 0.3*inch
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, y_offset, "Credit Card Statement")
    
    # Card Details with varied spacing
    y_offset -= 0.7*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y_offset, "Card Type:")
    c.setFont("Helvetica", 11)
    c.drawString(2.5*inch, y_offset, data['card_type'])
    
    y_offset -= 0.3*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y_offset, "Card Number:")
    c.setFont("Helvetica", 11)
    # Vary the format slightly
    if variation % 2 == 0:
        card_format = f"XXXX XXXX XXXX {data['last_4']}"
    else:
        card_format = f"XXXX-XXXX-XXXX-{data['last_4']}"
    c.drawString(2.5*inch, y_offset, card_format)
    
    # Billing Period
    y_offset -= 0.6*inch
    c.setFont("Helvetica-Bold", 12)
    # Vary the label
    period_label = "Billing Period:" if variation % 3 != 0 else "Statement Period:"
    c.drawString(1*inch, y_offset, period_label)
    c.setFont("Helvetica", 11)
    c.drawString(2.5*inch, y_offset, f"{data['start_date']} to {data['end_date']}")
    
    # Payment Due Date
    y_offset -= 0.3*inch
    c.setFont("Helvetica-Bold", 12)
    due_label = "Payment Due Date:" if variation % 2 == 0 else "Pay by:"
    c.drawString(1*inch, y_offset, due_label)
    c.setFont("Helvetica", 11)
    c.drawString(2.5*inch, y_offset, data['due_date'])
    
    # Total Amount Due - CRITICAL FIELD with variations
    y_offset -= 0.5*inch
    c.setFont("Helvetica-Bold", 14)
    amount_label = "Total Amount Due:" if variation % 3 != 0 else "Amount Due:"
    c.drawString(1*inch, y_offset, amount_label)
    c.setFont("Helvetica-Bold", 14)
    
    # Vary currency format
    if variation % 3 == 0:
        amount_text = f"₹ {data['amount']:,.2f}"
    elif variation % 3 == 1:
        amount_text = f"Rs. {data['amount']:,.2f}"
    else:
        amount_text = f"INR {data['amount']:,.2f}"
    
    c.drawString(2.5*inch, y_offset, amount_text)
    
    # Add some realistic noise (page numbers, etc.)
    c.setFont("Helvetica", 8)
    c.drawString(1*inch, 0.5*inch, "This is a computer generated statement")
    c.drawString(width - 2*inch, 0.5*inch, f"Page 1 of 1")
    
    c.save()


def create_icici_realistic(pdf_path, data, variation=0):
    """Create realistic ICICI statement"""
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    
    y_offset = height - 1*inch
    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(1*inch, y_offset, "ICICI Bank Limited")
    
    y_offset -= 0.25*inch
    c.setFont("Helvetica", 9)
    c.drawString(1*inch, y_offset, "Credit Card Statement of Account")
    
    y_offset -= 0.55*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y_offset, "Product:")
    c.setFont("Helvetica", 10)
    c.drawString(2.2*inch, y_offset, data['card_type'])
    
    y_offset -= 0.3*inch
    c.setFont("Helvetica-Bold", 11)
    card_label = "Card No.:" if variation % 2 == 0 else "Card Number:"
    c.drawString(1*inch, y_offset, card_label)
    c.setFont("Helvetica", 10)
    c.drawString(2.2*inch, y_offset, f"XXXX XXXX XXXX {data['last_4']}")
    
    y_offset -= 0.5*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y_offset, "Statement Period:")
    c.setFont("Helvetica", 10)
    c.drawString(2.2*inch, y_offset, f"{data['start_date']} to {data['end_date']}")
    
    y_offset -= 0.3*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y_offset, "Payment due by:")
    c.setFont("Helvetica", 10)
    c.drawString(2.2*inch, y_offset, data['due_date'])
    
    y_offset -= 0.6*inch
    c.setFont("Helvetica-Bold", 13)
    c.drawString(1*inch, y_offset, "Total Amount Due:")
    c.setFont("Helvetica-Bold", 13)
    c.drawString(2.2*inch, y_offset, f"Rs. {data['amount']:,.2f}")
    
    c.setFont("Helvetica", 7)
    c.drawString(1*inch, 0.5*inch, "ICICI Bank Ltd. | Customer Care: 1860 120 7777")
    
    c.save()


def create_sbi_realistic(pdf_path, data, variation=0):
    """Create realistic SBI statement"""
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    
    y_offset = height - 1*inch
    
    c.setFont("Helvetica-Bold", 19)
    c.drawString(1*inch, y_offset, "SBI Card")
    
    y_offset -= 0.3*inch
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, y_offset, "Statement of Account")
    
    y_offset -= 0.6*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y_offset, "Card Product:")
    c.setFont("Helvetica", 10)
    c.drawString(2.3*inch, y_offset, data['card_type'])
    
    y_offset -= 0.3*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y_offset, "Card Number:")
    c.setFont("Helvetica", 10)
    c.drawString(2.3*inch, y_offset, f"XXXX XXXX XXXX {data['last_4']}")
    
    y_offset -= 0.5*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y_offset, "Statement Period:")
    c.setFont("Helvetica", 10)
    c.drawString(2.3*inch, y_offset, f"{data['start_date']} to {data['end_date']}")
    
    y_offset -= 0.3*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y_offset, "Pay By:")
    c.setFont("Helvetica", 10)
    c.drawString(2.3*inch, y_offset, data['due_date'])
    
    y_offset -= 0.6*inch
    c.setFont("Helvetica-Bold", 13)
    c.drawString(1*inch, y_offset, "Total Amount Payable:")
    c.setFont("Helvetica-Bold", 13)
    c.drawString(2.3*inch, y_offset, f"Rs. {data['amount']:,.2f}")
    
    c.save()


def create_axis_realistic(pdf_path, data, variation=0):
    """Create realistic Axis statement"""
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    
    y_offset = height - 1*inch
    
    c.setFont("Helvetica-Bold", 19)
    c.drawString(1*inch, y_offset, "Axis Bank")
    
    y_offset -= 0.3*inch
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, y_offset, "Credit Card Statement")
    
    y_offset -= 0.6*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y_offset, "Card Name:")
    c.setFont("Helvetica", 10)
    c.drawString(2.2*inch, y_offset, data['card_type'])
    
    y_offset -= 0.3*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y_offset, "Card No.:")
    c.setFont("Helvetica", 10)
    c.drawString(2.2*inch, y_offset, f"XXXX XXXX XXXX {data['last_4']}")
    
    y_offset -= 0.5*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y_offset, "Billing Period:")
    c.setFont("Helvetica", 10)
    c.drawString(2.2*inch, y_offset, f"{data['start_date']} to {data['end_date']}")
    
    y_offset -= 0.3*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y_offset, "Payment Due Date:")
    c.setFont("Helvetica", 10)
    c.drawString(2.2*inch, y_offset, data['due_date'])
    
    y_offset -= 0.6*inch
    c.setFont("Helvetica-Bold", 13)
    c.drawString(1*inch, y_offset, "New Balance:")
    c.setFont("Helvetica-Bold", 13)
    c.drawString(2.2*inch, y_offset, f"INR {data['amount']:,.2f}")
    
    c.save()


def create_amex_realistic(pdf_path, data, variation=0):
    """Create realistic AMEX statement"""
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    
    y_offset = height - 1*inch
    
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1*inch, y_offset, "American Express")
    
    y_offset -= 0.3*inch
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, y_offset, "Statement of Account")
    
    y_offset -= 0.6*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y_offset, "Card Product:")
    c.setFont("Helvetica", 10)
    c.drawString(2.4*inch, y_offset, data['card_type'])
    
    y_offset -= 0.3*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y_offset, "Account ending in:")
    c.setFont("Helvetica", 10)
    c.drawString(2.4*inch, y_offset, data['last_4'])
    
    y_offset -= 0.5*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y_offset, "Statement Period:")
    c.setFont("Helvetica", 10)
    c.drawString(2.4*inch, y_offset, f"{data['start_date']} to {data['end_date']}")
    
    y_offset -= 0.3*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y_offset, "Please pay by:")
    c.setFont("Helvetica", 10)
    c.drawString(2.4*inch, y_offset, data['due_date'])
    
    y_offset -= 0.6*inch
    c.setFont("Helvetica-Bold", 13)
    c.drawString(1*inch, y_offset, "Payment Due:")
    c.setFont("Helvetica-Bold", 13)
    c.drawString(2.4*inch, y_offset, f"₹ {data['amount']:,.2f}")
    
    c.save()


BANK_CONFIGS = {
    "HDFC": {
        "cards": ["Regalia Credit Card", "MoneyBack Credit Card", "Diners Club Black", "Infinia Credit Card"],
        "generator": create_hdfc_realistic
    },
    "ICICI": {
        "cards": ["Coral Credit Card", "Platinum Chip Card", "Amazon Pay Card", "Sapphiro Credit Card"],
        "generator": create_icici_realistic
    },
    "SBI": {
        "cards": ["SimplyCLICK Card", "Prime Credit Card", "Elite Credit Card", "BPCL Card"],
        "generator": create_sbi_realistic
    },
    "AXIS": {
        "cards": ["Flipkart Credit Card", "Vistara Credit Card", "Ace Credit Card", "Select Credit Card"],
        "generator": create_axis_realistic
    },
    "AMEX": {
        "cards": ["Platinum Card", "Gold Card", "Membership Rewards Card", "SmartEarn Credit Card"],
        "generator": create_amex_realistic
    }
}


def generate_dates():
    """Generate realistic billing dates"""
    # Random date within last 90 days
    start = datetime.now() - timedelta(days=random.randint(1, 90))
    end = start + timedelta(days=30)
    due = end + timedelta(days=20)
    
    return (
        start.strftime("%d %b %Y"),
        end.strftime("%d %b %Y"),
        due.strftime("%d %b %Y")
    )


def main():
    """Generate realistic test PDFs"""
    print("=" * 70)
    print("🎯 REALISTIC CREDIT CARD STATEMENT GENERATOR")
    print("=" * 70)
    print()
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    total_generated = 0
    summary = {}
    
    for bank_code, config in BANK_CONFIGS.items():
        bank_dir = OUTPUT_DIR / bank_code.lower()
        bank_dir.mkdir(exist_ok=True)
        
        print(f"📄 Generating {NUM_FILES_PER_BANK} {bank_code} statements...")
        
        for i in range(NUM_FILES_PER_BANK):
            # Generate varied data
            card_type = random.choice(config["cards"])
            last_4 = str(random.randint(1000, 9999))
            start_date, end_date, due_date = generate_dates()
            amount = generate_realistic_amount()
            
            data = {
                'card_type': card_type,
                'last_4': last_4,
                'start_date': start_date,
                'end_date': end_date,
                'due_date': due_date,
                'amount': amount
            }
            
            filename = f"{bank_code.lower()}_{i+1:02d}_{last_4}.pdf"
            pdf_path = bank_dir / filename
            
            # Generate with variation
            config["generator"](pdf_path, data, variation=i)
            
            total_generated += 1
        
        summary[bank_code] = NUM_FILES_PER_BANK
    
    print(f"\n✅ Successfully generated {total_generated} realistic PDFs!")
    print("\n📊 Distribution:")
    for bank, count in summary.items():
        print(f"   {bank}: {count} files in {OUTPUT_DIR}/{bank.lower()}/")
    
    print(f"\n📁 All files saved in: {OUTPUT_DIR.absolute()}")
    print(f"\n🧪 Run tests with: python test_parser.py")
    print()


if __name__ == "__main__":
    main()