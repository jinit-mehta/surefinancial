"""
Validate parsed outputs against synthetic labels.json.
Usage: python backend/cli/validate_labels.py --labels synthetic_data/labels.json
"""
import json
from pathlib import Path
from ..utils.pdf_utils import extract_text
from ..parsers import hdfc, icici, sbi, axis, amex
from ..utils import regex_library
from difflib import SequenceMatcher
import argparse

PARSERS = {
    "HDFC": hdfc.parse,
    "ICICI": icici.parse,
    "SBI": sbi.parse,
    "AXIS": axis.parse,
    "AMEX": amex.parse
}

def detect_issuer(text):
    for k in PARSERS.keys():
        if k.lower() in text.lower():
            return k
    return None

def similar(a, b):
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()

def evaluate_one(meta, parsed):
    score = {}
    # compare issuer exact
    score['issuer_ok'] = (meta['issuer'].lower() == (parsed.get('issuer') or parsed.get('issuer_guess','')).lower())
    # last4 exact
    score['last4_ok'] = (meta.get('last4') == parsed.get('last4'))
    # amount fuzzy numeric compare (normalize numbers)
    def norm_num(s):
        if not s: return None
        return ''.join(ch for ch in s if (ch.isdigit() or ch=='.'))
    score['amount_ok'] = norm_num(meta.get('amount_due')) == norm_num(parsed.get('amount_due'))
    # billing period compare by similarity
    score['billing_sim'] = similar(meta.get('billing_start','') + meta.get('billing_end',''),
                                  (parsed.get('billing_start','') + parsed.get('billing_end','')))
    # due date exact-ish
    score['due_ok'] = meta.get('due_date') == parsed.get('due_date')
    return score

def parse_file(path):
    text = extract_text(path)
    issuer = detect_issuer(text)
    if issuer:
        res = PARSERS[issuer].parse(text)
    else:
        res = regex_library.generic_parse(text)
    res['raw_text_snippet'] = (text or "")[:1000]
    res['issuer_guess'] = issuer or res.get('issuer','UNKNOWN')
    return res

def main(labels_path="synthetic_data/labels.json"):
    labels = json.load(open(labels_path, "r"))
    summary = {"total": len(labels), "details": []}
    for entry in labels:
        filename = Path(entry['filename'])
        if not filename.exists():
            summary["details"].append({"file": str(filename), "error": "missing"})
            continue
        parsed = parse_file(str(filename))
        scores = evaluate_one(entry, parsed)
        summary["details"].append({"file": str(filename), "scores": scores, "parsed": parsed, "label": entry})
    # write summary
    out = "validation_report.json"
    with open(out, "w") as fh:
        json.dump(summary, fh, indent=2)
    print("Validation complete ->", out)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", type=str, default="synthetic_data/labels.json")
    args = parser.parse_args()
    main(args.labels)
