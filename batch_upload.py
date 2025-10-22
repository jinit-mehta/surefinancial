#!/usr/bin/env python3
"""
Batch upload test statements to the API
"""

import requests
from pathlib import Path
import time

API_URL = "http://localhost:8000/api"
TEST_DIR = Path("test_statements")

def upload_statement(pdf_path):
    """Upload a single statement"""
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path.name, f, 'application/pdf')}
            response = requests.post(f"{API_URL}/upload", files=files)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                return True, data
            else:
                return False, response.json().get('detail', 'Unknown error')
    except Exception as e:
        return False, str(e)

def main():
    print("🚀 Batch Upload Test Statements")
    print("=" * 50)
    
    pdf_files = list(TEST_DIR.glob("*.pdf"))
    print(f"📁 Found {len(pdf_files)} PDF files\n")
    
    success_count = 0
    fail_count = 0
    
    for idx, pdf_path in enumerate(pdf_files, 1):
        print(f"[{idx}/{len(pdf_files)}] Uploading {pdf_path.name}...", end=" ")
        
        success, result = upload_statement(pdf_path)
        
        if success:
            bank = result.get('bank_name', 'Unknown')
            amount = result.get('total_amount_due', 0)
            print(f"✅ {bank} - ₹{amount:,.2f}")
            success_count += 1
        else:
            print(f"❌ Failed: {result}")
            fail_count += 1
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)
    
    print(f"\n📊 Results:")
    print(f"   Success: {success_count}")
    print(f"   Failed: {fail_count}")
    print(f"   Total: {len(pdf_files)}")

if __name__ == "__main__":
    main()