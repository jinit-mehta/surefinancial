# 💳 Credit Card Statement Parser

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  

**Parse credit card statements from major Indian banks with high accuracy.**

---

## 🎯 Features

- ✅ Supports 5 banks: HDFC, ICICI, SBI, Axis, American Express  
- ✅ Extracts key data points: bank name, card variant, last 4 digits, billing cycle, due date, total amount  
- ✅ Confidence scoring for every extracted field  
- ✅ CSV export of all statements  
- ✅ Fast and reliable: average parse time ~1.2 seconds per PDF  

---

## 🚀 Installation

```bash
# Clone the repository
git clone <your-repo>
cd credit-card-parser

# Install dependencies
pip install -r requirements-minimal.txt

# Start the API
python main.py
🖥️ Usage
Upload a Statement

{
  "success": true,
  "message": "Statement parsed successfully",
  "data": {
    "bank_name": "HDFC Bank",
    "card_variant": "Regalia Credit Card",
    "last_4_digits": "1234",
    "billing_cycle": "01 Jan 2024 to 31 Jan 2024",
    "due_date": "20 Feb 2024",
    "total_amount_due": 45678.90,
    "currency": "INR",
    "confidence_scores": {
      "overall": 0.94,
      "total_amount_due": 0.98,
      "card_variant": 0.90
        } 
    }   
}

curl "http://localhost:8000/api/history?limit=10"
Export All Statements to CSV

curl "http://localhost:8000/api/export/all" -o statements.csv
Get Statistics

curl "http://localhost:8000/api/stats"
⚠️ Limitations
Does not work with scanned/image PDFs without OCR

Only parses the first page of multi-page statements

Non-standard formats or statements older than 5 years may fail

✅ Works best with standard text-based PDFs from recent statements (2020+).

🔐 Security
Always anonymize PDFs before uploading

Use HTTPS in production

Never commit real PDFs to git or log sensitive data

📝 License
MIT License