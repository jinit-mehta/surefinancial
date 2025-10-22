"""
Generates synthetic credit card PDFs and metadata JSON.
Run: python backend/synth/dataset_generator.py --count 100
"""
import argparse
import random
from pathlib import Path
from faker import Faker
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import json
from datetime import datetime, timedelta

fake = Faker("en_IN")
OUTPUT_DIR = Path("synthetic_data/pdfs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
META_FILE = Path("synthetic_data/labels.json")

ISSUERS = ["HDFC", "ICICI", "SBI", "AXIS", "AMEX"]
CARD_VARIANTS = ["Regalia", "Platinum", "Titanium", "Infinia", "Gold"]

def make_statement_pdf(idx, issuer):
    filename = OUTPUT_DIR / f"{idx:03d}_{issuer.lower()}.pdf"
    c = canvas.Canvas(str(filename), pagesize=A4)
    width, height = A4
    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 40, f"{issuer} Bank Credit Card Statement")
    c.setFont("Helvetica", 10)
    variant = random.choice(CARD_VARIANTS)
    last4 = f"{random.randint(1000, 9999)}"
    c.drawString(40, height - 60, f"Card: {variant} • **** **** **** {last4}")
    # Billing period
    start = fake.date_between(start_date='-90d', end_date='-31d')
    end = start + timedelta(days=29)
    due_date = end + timedelta(days=20)
    c.drawString(40, height - 80, f"Statement Period: {start.strftime('%m/%d/%Y')} to {end.strftime('%m/%d/%Y')}")
    c.drawString(40, height - 100, f"Payment Due Date: {due_date.strftime('%m/%d/%Y')}")
    # Transactions table (simple)
    y = height - 140
    num_tx = random.randint(10, 25)
    total = 0.0
    c.setFont("Helvetica", 9)
    for i in range(num_tx):
        date = start + timedelta(days=random.randint(0, 28))
        merchant = fake.company()[:28]
        amount = round(random.uniform(50, 5000), 2)
        total += amount
        c.drawString(40, y, f"{date.strftime('%m/%d/%Y')}")
        c.drawString(120, y, merchant)
        c.drawRightString(520, y, f"₹{amount:,.2f}")
        y -= 14
        if y < 100:
            c.showPage()
            y = height - 60
    gst = round(total * 0.18, 2)
    late_fee = random.choice([0.0, 100.0, 200.0])
    amount_due = round(total + gst + late_fee, 2)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, 80, f"Subtotal: ₹{total:,.2f}")
    c.drawString(40, 64, f"GST (18%): ₹{gst:,.2f}")
    c.drawString(40, 48, f"Late Fee: ₹{late_fee:,.2f}")
    c.drawString(40, 32, f"Total Amount Due: ₹{amount_due:,.2f}")
    c.save()
    meta = {
        "filename": str(filename),
        "issuer": issuer,
        "card_variant": variant,
        "last4": last4,
        "billing_start": start.strftime("%m/%d/%Y"),
        "billing_end": end.strftime("%m/%d/%Y"),
        "due_date": due_date.strftime("%m/%d/%Y"),
        "amount_due": f"{amount_due:.2f}",
        "transactions": num_tx
    }
    return meta

def main(count=100):
    metas = []
    for i in range(1, count + 1):
        issuer = random.choice(ISSUERS)
        meta = make_statement_pdf(i, issuer)
        metas.append(meta)
    META_FILE.write_text(json.dumps(metas, indent=2))
    print(f"Generated {count} PDFs in {OUTPUT_DIR}. Metadata saved to {META_FILE}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100)
    args = parser.parse_args()
    main(args.count)
