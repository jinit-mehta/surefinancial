# backend/cli/review_report.py
"""
Enhanced review script:
- Uses normalize.compare_dates for robust date comparison
- Computes per-field TP/FP/FN, precision, recall
- Produces confusion diagnostics for card_variant (and issuer)
- Outputs:
  reports/review_full.json
  reports/summary_by_bank.csv
  reports/metrics_by_field.json
  reports/confusion_card_variant.csv
  reports/confusion_issuer.csv
"""
import json
from pathlib import Path
import argparse
from ..utils.pdf_utils import extract_text
from ..parsers import hdfc, icici, sbi, axis, amex
from ..utils import regex_library
from ..utils import normalize
from collections import defaultdict, Counter
import csv

PARSERS = {
    "HDFC": hdfc.parse,
    "ICICI": icici.parse,
    "SBI": sbi.parse,
    "AXIS": axis.parse,
    "AMEX": amex.parse
}

FIELDS = ["issuer", "card_variant", "last4", "billing_start", "billing_end", "due_date", "amount_due"]

def detect_issuer(text):
    for k in PARSERS.keys():
        if k.lower() in (text or "").lower():
            return k
    return None

def cmp_field_metrics(label, parsed, field, bank_hint=None):
    """
    Return (is_tp, is_fp, is_fn, score, note)
    Basic rules:
     - If label empty and parsed empty -> no-op (not counted)
     - If label exists and parsed equals label (with normalization) -> TP
     - If label exists and parsed exists but mismatched -> FN + FP (parsed is false positive for that label)
     - If label exists and parsed missing -> FN
     - If label missing and parsed exists -> FP
    """
    lbl = label
    pr = parsed

    if field == "amount_due":
        ok = normalize.approx_equal_numbers(lbl, pr)
        if lbl and ok:
            return 1, 0, 0, 1.0, None
        if lbl and (pr is None or pr == ""):
            return 0, 0, 1, 0.0, f"amount missing parsed={pr}"
        if lbl and not ok:
            return 0, 1, 1, 0.0, f"amount mismatch label={lbl} parsed={pr}"
        if (not lbl) and pr:
            return 0, 1, 0, 0.0, f"false amount parsed={pr}"
        return 0, 0, 0, 0.0, None

    if field in ("billing_start", "billing_end", "due_date"):
        ok, ln, pn = normalize.compare_dates(lbl, pr, bank_hint)
        if lbl and ok:
            return 1, 0, 0, 1.0, None
        if lbl and (not pr):
            return 0, 0, 1, 0.0, f"date missing parsed={pr}"
        if lbl and (not ok):
            return 0, 1, 1, 0.0, f"date mismatch label_norm={ln} parsed_norm={pn}"
        if (not lbl) and pr:
            return 0, 1, 0, 0.0, f"false date parsed={pr}"
        return 0, 0, 0, 0.0, None

    if field == "last4":
        if lbl and pr and str(lbl).strip() == str(pr).strip():
            return 1, 0, 0, 1.0, None
        if lbl and (not pr):
            return 0, 0, 1, 0.0, f"last4 missing parsed={pr}"
        if lbl and pr and str(lbl).strip() != str(pr).strip():
            return 0, 1, 1, 0.0, f"last4 mismatch label={lbl} parsed={pr}"
        if (not lbl) and pr:
            return 0, 1, 0, 0.0, f"false last4 parsed={pr}"
        return 0, 0, 0, 0.0, None

    # categorical/fuzzy strings
    score = normalize.simple_str_sim(lbl, pr)
    ok = score >= 0.85  # stricter for metrics
    if lbl and ok:
        return 1, 0, 0, score, None
    if lbl and (not pr):
        return 0, 0, 1, score, f"{field} missing parsed={pr}"
    if lbl and (not ok):
        return 0, 1, 1, score, f"{field} mismatch score={score:.2f} label={lbl} parsed={pr}"
    if (not lbl) and pr:
        return 0, 1, 0, score, f"false {field} parsed={pr}"
    return 0, 0, 0, 0.0, None

def evaluate_all(labels, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    # counters for metrics
    metrics = {f: {"TP": 0, "FP": 0, "FN": 0} for f in FIELDS}
    # confusion counters for categorical fields
    confusion_card_variant = Counter()
    confusion_issuer = Counter()
    per_bank_scores = defaultdict(list)

    for entry in labels:
        filename = Path(entry["filename"])
        if not filename.exists():
            results.append({"file": str(filename), "error": "missing_file"})
            continue
        text = extract_text(str(filename))
        issuer_guess = detect_issuer(text)
        parser = PARSERS.get(issuer_guess)
        if parser:
            parsed = parser.parse(text)
        else:
            parsed = regex_library.generic_parse(text)
            parsed['issuer_guess'] = issuer_guess or parsed.get('issuer','UNKNOWN')
        parsed['raw_text_snippet'] = (text or "")[:1000]

        detail = {"file": str(filename), "label": entry, "parsed": parsed, "scores": {}, "comments": []}
        total_score = 0.0
        for f in FIELDS:
            lab = entry.get(f)
            par = parsed.get(f)
            bank_hint = entry.get("issuer")
            tp, fp, fn, score, note = cmp_field_metrics(lab, par, f, bank_hint)
            if tp:
                metrics[f]["TP"] += 1
            if fp:
                metrics[f]["FP"] += 1
            if fn:
                metrics[f]["FN"] += 1
            detail["scores"][f] = {"tp": bool(tp), "fp": bool(fp), "fn": bool(fn), "score": float(score), "note": note}
            if note:
                detail["comments"].append(note)
            total_score += float(score)
            # confusion tracking
            if f == "card_variant":
                confusion_card_variant[(str(lab or "NULL"), str(par or "NULL"))] += 1
            if f == "issuer":
                confusion_issuer[(str(lab or "NULL"), str(par or "NULL"))] += 1

        detail["aggregate_score"] = round(total_score / len(FIELDS), 4)
        per_bank_scores[entry.get("issuer","UNKNOWN")].append(detail["aggregate_score"])
        results.append(detail)

    # compute precision/recall per field
    metrics_summary = {}
    for f, cnts in metrics.items():
        tp = cnts["TP"]
        fp = cnts["FP"]
        fn = cnts["FN"]
        precision = tp / (tp + fp) if (tp + fp) > 0 else None
        recall = tp / (tp + fn) if (tp + fn) > 0 else None
        metrics_summary[f] = {"TP": tp, "FP": fp, "FN": fn, "precision": precision, "recall": recall}

    # bank summary like before
    bank_summary = []
    for bank, scores in per_bank_scores.items():
        if not scores:
            continue
        bank_summary.append({
            "bank": bank,
            "count": len(scores),
            "avg_score": round(sum(scores)/len(scores), 4),
            "pct_above_0_9": round(sum(1 for s in scores if s >= 0.9)/len(scores) * 100, 2),
            "pct_above_0_8": round(sum(1 for s in scores if s >= 0.8)/len(scores) * 100, 2)
        })

    # Save outputs
    (out_dir / "review_full.json").write_text(json.dumps(results, indent=2))
    (out_dir / "metrics_by_field.json").write_text(json.dumps(metrics_summary, indent=2))
    (out_dir / "summary_by_bank.json").write_text(json.dumps(bank_summary, indent=2))

    # Save confusion as CSV tables (rows: label, columns: parsed)
    def save_confusion(counter, out_csv):
        # build matrix keys
        pairs = list(counter.items())
        labels = sorted({p[0] for p,_ in pairs})
        parseds = sorted({p[1] for p,_ in pairs})
        # header
        with open(out_csv, "w", newline='') as fh:
            writer = csv.writer(fh)
            writer.writerow(["label\\parsed"] + parseds)
            for lab in labels:
                row = [lab]
                for par in parseds:
                    row.append(counter.get((lab, par), 0))
                writer.writerow(row)

    save_confusion(confusion_card_variant, out_dir / "confusion_card_variant.csv")
    save_confusion(confusion_issuer, out_dir / "confusion_issuer.csv")

    # Also produce a simple summary CSV for bank_summary
    with open(out_dir / "summary_by_bank.csv", "w", newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=["bank", "count", "avg_score", "pct_above_0_9", "pct_above_0_8"])
        writer.writeheader()
        for row in bank_summary:
            writer.writerow(row)

    print(f"Saved: {out_dir / 'review_full.json'}, {out_dir / 'metrics_by_field.json'}")
    print(f"Confusions -> {out_dir / 'confusion_card_variant.csv'}, {out_dir / 'confusion_issuer.csv'}")
    return {
        "full": str(out_dir / "review_full.json"),
        "metrics": str(out_dir / "metrics_by_field.json"),
        "confusion_card_variant": str(out_dir / "confusion_card_variant.csv"),
        "confusion_issuer": str(out_dir / "confusion_issuer.csv"),
        "bank_summary": str(out_dir / "summary_by_bank.csv")
    }

def run(labels_path="synthetic_data/labels.json", out_dir="reports"):
    labels = json.loads(Path(labels_path).read_text())
    return evaluate_all(labels, out_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", type=str, default="synthetic_data/labels.json")
    parser.add_argument("--out", type=str, default="reports")
    args = parser.parse_args()
    run(args.labels, args.out)
