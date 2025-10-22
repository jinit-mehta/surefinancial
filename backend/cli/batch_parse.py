"""
Batch parse all PDFs in synthetic_data/pdfs/, save results to SQLite.
Usage: python backend/cli/batch_parse.py --dir synthetic_data/pdfs --commit
"""
import argparse
from pathlib import Path
from ..utils.pdf_utils import extract_text
from ..parsers import hdfc, icici, sbi, axis, amex
from ..utils import regex_library
from ..utils.storage import init_db, save_result

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

def parse_file(path):
    text = extract_text(path)
    issuer = detect_issuer(text)
    if issuer:
        result = PARSERS[issuer].parse(text) if hasattr(PARSERS[issuer], "parse") else PARSERS[issuer](text)
    else:
        result = regex_library.generic_parse(text)
    result["raw_text_snippet"] = (text or "")[:1000]
    return result

def main(dir_path="synthetic_data/pdfs", commit=False):
    init_db()
    p = Path(dir_path)
    files = sorted(list(p.glob("*.pdf")))
    report = []
    for f in files:
        print("Parsing:", f)
        res = parse_file(str(f))
        if commit:
            save_id = save_result(str(f), res)
        else:
            save_id = None
        report.append({"file": str(f), "result": res, "saved_id": save_id})
    # write quick report
    import json
    with open("batch_report.json", "w") as fh:
        json.dump(report, fh, indent=2)
    print(f"Parsed {len(files)} files. Report -> batch_report.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, default="synthetic_data/pdfs")
    parser.add_argument("--commit", action="store_true", help="Save results to SQLite")
    args = parser.parse_args()
    main(args.dir, args.commit)
