#!/usr/bin/env python3
"""
Generate 200 realistic credit card statement PDFs for testing
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime, timedelta
import random
import os
from pathlib import Path

# Configuration
OUTPUT_DIR = Path("test_statements")
NUM_FILES = 200

# Bank configurations
BANKS = {
    "HDFC": {
        "full_name": "HDFC Bank Ltd.",
        "colors": {"primary": "#004C8F", "secondary": "#ED1C24"},
        "card_types": ["Regalia Credit Card", "MoneyBack Credit Card", "Diners Club Black", "Infinia Credit Card"],
        "template": "hdfc"
    },
    "ICICI": {
        "full_name": "ICICI Bank Limited",
        "colors": {"primary": "#F37021", "secondary": "#522D6D"},
        "card_types": ["Coral Credit Card", "Platinum Chip Card", "Amazon Pay Card", "Sapphiro Credit Card"],
        "template": "icici"
    },
    "SBI": {
        "full_name": "SBI Card",
        "colors": {"primary": "#0066B3", "secondary": "#00A550"},
        "card_types": ["SimplyCLICK Card", "Prime Credit Card", "Elite Credit Card", "BPCL Card"],
        "template": "sbi"
    },
    "AXIS": {
        "full_name": "Axis Bank",
        "colors": {"primary": "#97144D", "secondary": "#800020"},
        "card_types": ["Flipkart Credit Card", "Vistara Credit Card", "Ace Credit Card", "Select Credit Card"],
        "template": "axis"
    },
    "AMEX": {
        "full_name": "American Express",
        "colors": {"primary": "#006FCF", "secondary": "#00175A"},
        "card_types": ["Platinum Card", "Gold Card", "Membership Rewards Card", "SmartEarn Credit Card"],
        "template": "amex"
    }
}

def generate_random_date():
    """Generate random billing cycle dates"""
    start = datetime.now() - timedelta(days=random.randint(1, 90))
    end = start + timedelta(days=30)
    due = end + timedelta(days=20)
    return start, end, due

def generate_card_number():
    """Generate last 4 digits"""
    return str(random.randint(1000, 9999))

def generate_amount():
    """Generate random amount due"""
    return round(random.uniform(5000, 150000), 2)

def create_hdfc_statement(pdf_path, data):
    """Create HDFC Bank style statement"""
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1*inch, height - 1*inch, "HDFC Bank Ltd.")
    
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 1.3*inch, "Credit Card Statement")
    
    # Card Details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, height - 2*inch, "Card Type:")
    c.setFont("Helvetica", 11)
    c.drawString(2.5*inch, height - 2*inch, data['card_type'])
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, height - 2.3*inch, "Card Number:")
    c.setFont("Helvetica", 11)
    c.drawString(2.5*inch, height - 2.3*inch, f"XXXX XXXX XXXX {data['last_4']}")
    
    # Billing Period
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, height - 2.9*inch, "Billing Period:")
    c.setFont("Helvetica", 11)
    c.drawString(2.5*inch, height - 2.9*inch, f"{data['start_date']} to {data['end_date']}")
    
    # Payment Due Date
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, height - 3.2*inch, "Payment Due Date:")
    c.setFont("Helvetica", 11)
    c.drawString(2.5*inch, height - 3.2*inch, data['due_date'])
    
    # Total Amount Due
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 3.7*inch, "Total Amount Due:")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2.5*inch, height - 3.7*inch, f"₹ {data['amount']:,.2f}")
    
    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(1*inch, 0.5*inch, "This is a computer generated statement")
    
    c.save()

def create_icici_statement(pdf_path, data):
    """Create ICICI Bank style statement"""
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    
    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(1*inch, height - 1*inch, "ICICI Bank Limited")
    
    c.setFont("Helvetica", 9)
    c.drawString(1*inch, height - 1.25*inch, "Credit Card Statement of Account")
    
    # Card Product
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 1.8*inch, "Product:")
    c.setFont("Helvetica", 10)
    c.drawString(2.2*inch, height - 1.8*inch, data['card_type'])
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 2.1*inch, "Card No.:")
    c.setFont("Helvetica", 10)
    c.drawString(2.2*inch, height - 2.1*inch, f"XXXX XXXX XXXX {data['last_4']}")
    
    # Statement Period
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 2.6*inch, "Statement Period:")
    c.setFont("Helvetica", 10)
    c.drawString(2.2*inch, height - 2.6*inch, f"{data['start_date']} to {data['end_date']}")
    
    # Payment due by
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 2.9*inch, "Payment due by:")
    c.setFont("Helvetica", 10)
    c.drawString(2.2*inch, height - 2.9*inch, data['due_date'])
    
    # Total Amount Due
    c.setFont("Helvetica-Bold", 13)
    c.drawString(1*inch, height - 3.5*inch, "Total Amount Due:")
    c.setFont("Helvetica-Bold", 13)
    c.drawString(2.2*inch, height - 3.5*inch, f"Rs. {data['amount']:,.2f}")
    
    c.save()

def create_sbi_statement(pdf_path, data):
    """Create SBI Card style statement"""
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 19)
    c.drawString(1*inch, height - 1*inch, "SBI Card")
    
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 1.3*inch, "Statement of Account")
    
    # Card Product Name
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 1.9*inch, "Card Product:")
    c.setFont("Helvetica", 10)
    c.drawString(2.3*inch, height - 1.9*inch, data['card_type'])
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 2.2*inch, "Card Number:")
    c.setFont("Helvetica", 10)
    c.drawString(2.3*inch, height - 2.2*inch, f"XXXX XXXX XXXX {data['last_4']}")
    
    # Statement Period
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 2.7*inch, "Statement Period:")
    c.setFont("Helvetica", 10)
    c.drawString(2.3*inch, height - 2.7*inch, f"{data['start_date']} to {data['end_date']}")
    
    # Payment Due Date
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 3.0*inch, "Pay By:")
    c.setFont("Helvetica", 10)
    c.drawString(2.3*inch, height - 3.0*inch, data['due_date'])
    
    # Total Amount Payable
    c.setFont("Helvetica-Bold", 13)
    c.drawString(1*inch, height - 3.6*inch, "Total Amount Payable:")
    c.setFont("Helvetica-Bold", 13)
    c.drawString(2.3*inch, height - 3.6*inch, f"Rs. {data['amount']:,.2f}")
    
    c.save()

def create_axis_statement(pdf_path, data):
    """Create Axis Bank style statement"""
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 19)
    c.drawString(1*inch, height - 1*inch, "Axis Bank")
    
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 1.3*inch, "Credit Card Statement")
    
    # Card Name
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 1.9*inch, "Card Name:")
    c.setFont("Helvetica", 10)
    c.drawString(2.2*inch, height - 1.9*inch, data['card_type'])
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 2.2*inch, "Card No.:")
    c.setFont("Helvetica", 10)
    c.drawString(2.2*inch, height - 2.2*inch, f"XXXX XXXX XXXX {data['last_4']}")
    
    # Billing Period
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 2.7*inch, "Billing Period:")
    c.setFont("Helvetica", 10)
    c.drawString(2.2*inch, height - 2.7*inch, f"{data['start_date']} to {data['end_date']}")
    
    # Payment Due Date
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 3.0*inch, "Payment Due Date:")
    c.setFont("Helvetica", 10)
    c.drawString(2.2*inch, height - 3.0*inch, data['due_date'])
    
    # New Balance
    c.setFont("Helvetica-Bold", 13)
    c.drawString(1*inch, height - 3.6*inch, "New Balance:")
    c.setFont("Helvetica-Bold", 13)
    c.drawString(2.2*inch, height - 3.6*inch, f"INR {data['amount']:,.2f}")
    
    c.save()

def create_amex_statement(pdf_path, data):
    """Create American Express style statement"""
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1*inch, height - 1*inch, "American Express")
    
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 1.3*inch, "Statement of Account")
    
    # Card Product
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 1.9*inch, "Card Product:")
    c.setFont("Helvetica", 10)
    c.drawString(2.4*inch, height - 1.9*inch, data['card_type'])
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 2.2*inch, "Account ending in:")
    c.setFont("Helvetica", 10)
    c.drawString(2.4*inch, height - 2.2*inch, data['last_4'])
    
    # Statement Closing Date
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 2.7*inch, "Statement Period:")
    c.setFont("Helvetica", 10)
    c.drawString(2.4*inch, height - 2.7*inch, f"{data['start_date']} to {data['end_date']}")
    
    # Please pay by
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 3.0*inch, "Please pay by:")
    c.setFont("Helvetica", 10)
    c.drawString(2.4*inch, height - 3.0*inch, data['due_date'])
    
    # Payment Due
    c.setFont("Helvetica-Bold", 13)
    c.drawString(1*inch, height - 3.6*inch, "Payment Due:")
    c.setFont("Helvetica-Bold", 13)
    c.drawString(2.4*inch, height - 3.6*inch, f"₹ {data['amount']:,.2f}")
    
    c.save()

def generate_statement(bank_code, index):
    """Generate a single statement"""
    bank_info = BANKS[bank_code]
    
    # Generate random data
    start_date, end_date, due_date = generate_random_date()
    
    data = {
        'card_type': random.choice(bank_info['card_types']),
        'last_4': generate_card_number(),
        'start_date': start_date.strftime("%d %b %Y"),
        'end_date': end_date.strftime("%d %b %Y"),
        'due_date': due_date.strftime("%d %b %Y"),
        'amount': generate_amount()
    }
    
    # Create filename
    filename = f"{bank_code}_{index:03d}_{data['last_4']}.pdf"
    pdf_path = OUTPUT_DIR / filename
    
    # Create PDF based on bank template
    if bank_code == "HDFC":
        create_hdfc_statement(pdf_path, data)
    elif bank_code == "ICICI":
        create_icici_statement(pdf_path, data)
    elif bank_code == "SBI":
        create_sbi_statement(pdf_path, data)
    elif bank_code == "AXIS":
        create_axis_statement(pdf_path, data)
    elif bank_code == "AMEX":
        create_amex_statement(pdf_path, data)
    
    return filename, data

def main():
    """Generate all test statements"""
    print("🏦 Credit Card Statement Generator")
    print("=" * 50)
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"📁 Output directory: {OUTPUT_DIR.absolute()}\n")
    
    # Distribute files across banks
    files_per_bank = NUM_FILES // len(BANKS)
    remaining = NUM_FILES % len(BANKS)
    
    total_generated = 0
    summary = {}
    
    for idx, (bank_code, bank_info) in enumerate(BANKS.items()):
        count = files_per_bank + (1 if idx < remaining else 0)
        summary[bank_code] = count
        
        print(f"📄 Generating {count} {bank_code} statements...")
        
        for i in range(count):
            filename, data = generate_statement(bank_code, total_generated + 1)
            total_generated += 1
            
            if (total_generated) % 20 == 0:
                print(f"   Generated {total_generated}/{NUM_FILES} files...")
    
    print(f"\n✅ Successfully generated {total_generated} PDF statements!")
    print("\n📊 Distribution:")
    for bank, count in summary.items():
        print(f"   {bank}: {count} files")
    
    print(f"\n📂 All files saved in: {OUTPUT_DIR.absolute()}")
    print(f"\n🚀 You can now upload these to test the parser!")

if __name__ == "__main__":
    main()