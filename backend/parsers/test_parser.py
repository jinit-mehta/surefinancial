"""
Comprehensive Test Suite for Credit Card Parser
Run: python test_parser.py
"""

import sys
import os
from pathlib import Path
from typing import Dict, List
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.hdfc_parser import HDFCParser
from parsers.icici_parser import ICICIParser
from parsers.sbi_parser import SBIParser
from parsers.axis_parser import AxisParser
from parsers.amex_parser import AMEXParser


class TestCase:
    """Test case structure"""
    def __init__(self, name: str, text: str, expected: Dict):
        self.name = name
        self.text = text
        self.expected = expected


# Test cases based on the generated PDF patterns
TEST_CASES = {
    "HDFC": [
        TestCase(
            name="HDFC Regalia Standard",
            text="""
            HDFC Bank Ltd.
            Credit Card Statement
            
            Card Type: Regalia Credit Card
            Card Number: XXXX XXXX XXXX 1234
            
            Billing Period: 01 Jan 2024 to 31 Jan 2024
            Payment Due Date: 20 Feb 2024
            
            Total Amount Due: ₹ 45,678.90
            
            This is a computer generated statement
            """,
            expected={
                "bank_name": "HDFC Bank",
                "card_variant": "Regalia Credit Card",
                "last_4_digits": "1234",
                "total_amount_due": 45678.90,
                "min_confidence": 0.8
            }
        ),
        TestCase(
            name="HDFC MoneyBack Alternate Format",
            text="""
            HDFC Bank Ltd.
            
            Card Type: MoneyBack Credit Card
            Card ending XXXX XXXX XXXX 5678
            
            Statement Period: 15 Feb 2024 - 14 Mar 2024
            Pay by: 03 Apr 2024
            
            Amount Due: Rs. 1,23,456.00
            """,
            expected={
                "bank_name": "HDFC Bank",
                "card_variant": "MoneyBack Credit Card",
                "last_4_digits": "5678",
                "total_amount_due": 123456.00,
                "min_confidence": 0.7
            }
        ),
    ],
    "ICICI": [
        TestCase(
            name="ICICI Coral Standard",
            text="""
            ICICI Bank Limited
            Credit Card Statement of Account
            
            Product: Coral Credit Card
            Card No.: XXXX XXXX XXXX 9876
            
            Statement Period: 05 Jan 2024 to 04 Feb 2024
            Payment due by: 24 Feb 2024
            
            Total Amount Due: Rs. 67,890.50
            """,
            expected={
                "bank_name": "ICICI Bank",
                "card_variant": "Coral Credit Card",
                "last_4_digits": "9876",
                "total_amount_due": 67890.50,
                "min_confidence": 0.8
            }
        ),
    ],
    "SBI": [
        TestCase(
            name="SBI SimplyCLICK Standard",
            text="""
            SBI Card
            Statement of Account
            
            Card Product: SimplyCLICK Card
            Card Number: XXXX XXXX XXXX 4321
            
            Statement Period: 10 Jan 2024 to 09 Feb 2024
            Pay By: 29 Feb 2024
            
            Total Amount Payable: Rs. 34,567.80
            """,
            expected={
                "bank_name": "SBI Card",
                "card_variant": "SimplyCLICK Card",
                "last_4_digits": "4321",
                "total_amount_due": 34567.80,
                "min_confidence": 0.8
            }
        ),
    ],
    "AXIS": [
        TestCase(
            name="Axis Flipkart Standard",
            text="""
            Axis Bank
            Credit Card Statement
            
            Card Name: Flipkart Credit Card
            Card No.: XXXX XXXX XXXX 8765
            
            Billing Period: 12 Jan 2024 to 11 Feb 2024
            Payment Due Date: 01 Mar 2024
            
            New Balance: INR 56,789.00
            """,
            expected={
                "bank_name": "Axis Bank",
                "card_variant": "Flipkart Credit Card",
                "last_4_digits": "8765",
                "total_amount_due": 56789.00,
                "min_confidence": 0.8
            }
        ),
    ],
    "AMEX": [
        TestCase(
            name="AMEX Platinum Standard",
            text="""
            American Express
            Statement of Account
            
            Card Product: Platinum Card
            Account ending in: 3456
            
            Statement Period: 08 Jan 2024 to 07 Feb 2024
            Please pay by: 27 Feb 2024
            
            Payment Due: ₹ 89,012.45
            """,
            expected={
                "bank_name": "American Express",
                "card_variant": "Platinum Card",
                "last_4_digits": "3456",
                "total_amount_due": 89012.45,
                "min_confidence": 0.8
            }
        ),
    ],
}


def run_test(parser_class, test_case: TestCase) -> Dict:
    """Run a single test case"""
    parser = parser_class(test_case.text)
    result = parser.parse()
    
    # Check assertions
    passed = True
    errors = []
    
    # Check bank name
    if result.get('bank_name') != test_case.expected['bank_name']:
        passed = False
        errors.append(f"Bank name mismatch: {result.get('bank_name')} != {test_case.expected['bank_name']}")
    
    # Check card variant (partial match OK)
    expected_variant = test_case.expected['card_variant']
    actual_variant = result.get('card_variant', '')
    if expected_variant.split()[0] not in actual_variant:
        passed = False
        errors.append(f"Card variant mismatch: {actual_variant} != {expected_variant}")
    
    # Check last 4 digits
    if result.get('last_4_digits') != test_case.expected['last_4_digits']:
        passed = False
        errors.append(f"Last 4 digits mismatch: {result.get('last_4_digits')} != {test_case.expected['last_4_digits']}")
    
    # Check amount (critical!)
    expected_amount = test_case.expected['total_amount_due']
    actual_amount = result.get('total_amount_due', 0)
    if abs(actual_amount - expected_amount) > 0.01:
        passed = False
        errors.append(f"Amount mismatch: {actual_amount} != {expected_amount}")
    
    # Check confidence
    overall_confidence = result.get('confidence_scores', {}).get('overall', 0)
    min_confidence = test_case.expected.get('min_confidence', 0.7)
    if overall_confidence < min_confidence:
        passed = False
        errors.append(f"Low confidence: {overall_confidence} < {min_confidence}")
    
    return {
        "test_name": test_case.name,
        "passed": passed,
        "errors": errors,
        "result": result,
        "confidence": overall_confidence
    }


def run_all_tests():
    """Run all test cases"""
    print("=" * 70)
    print("🧪 CREDIT CARD PARSER - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()
    
    parsers = {
        "HDFC": HDFCParser,
        "ICICI": ICICIParser,
        "SBI": SBIParser,
        "AXIS": AxisParser,
        "AMEX": AMEXParser
    }
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    results_by_bank = {}
    
    for bank, test_cases in TEST_CASES.items():
        print(f"\n📋 Testing {bank} Parser ({len(test_cases)} tests)")
        print("-" * 70)
        
        bank_results = []
        
        for test_case in test_cases:
            total_tests += 1
            result = run_test(parsers[bank], test_case)
            bank_results.append(result)
            
            if result['passed']:
                passed_tests += 1
                status = "✅ PASS"
            else:
                failed_tests += 1
                status = "❌ FAIL"
            
            print(f"{status} | {result['test_name']}")
            print(f"    Confidence: {result['confidence']:.2f}")
            
            if not result['passed']:
                for error in result['errors']:
                    print(f"    ⚠️  {error}")
            
            # Show extracted data
            r = result['result']
            print(f"    Extracted: {r.get('card_variant')} | "
                  f"****{r.get('last_4_digits')} | "
                  f"₹{r.get('total_amount_due', 0):,.2f}")
        
        results_by_bank[bank] = bank_results
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests:  {total_tests}")
    print(f"✅ Passed:    {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"❌ Failed:    {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
    print()
    
    # Bank-wise accuracy
    print("🏦 Accuracy by Bank:")
    for bank, results in results_by_bank.items():
        bank_passed = sum(1 for r in results if r['passed'])
        bank_total = len(results)
        accuracy = bank_passed / bank_total * 100 if bank_total > 0 else 0
        print(f"  {bank:10} : {bank_passed}/{bank_total} ({accuracy:.1f}%)")
    
    print("\n" + "=" * 70)
    
    # Save results
    output_file = "test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "accuracy": passed_tests / total_tests * 100
            },
            "by_bank": {
                bank: [
                    {
                        "name": r['test_name'],
                        "passed": r['passed'],
                        "confidence": r['confidence'],
                        "errors": r['errors']
                    }
                    for r in results
                ]
                for bank, results in results_by_bank.items()
            }
        }, f, indent=2)
    
    print(f"📄 Detailed results saved to: {output_file}")
    print()
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)