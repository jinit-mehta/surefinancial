# frontend/streamlit_review.py
import streamlit as st
import json
from pathlib import Path
import pandas as pd

# Import parsing & storage functions directly for on-demand re-run
from backend.utils.pdf_utils import extract_text
from backend.parsers import hdfc, icici, sbi, axis, amex
from backend.utils import regex_library
from backend.utils.storage import save_result, init_db

st.set_page_config(page_title="Parser Review Dashboard", layout="wide")
st.title("Credit Card Statement Parser — Review Dashboard (Enhanced)")

reports_dir = Path("reports")
review_file = reports_dir / "review_full.json"
summary_file = reports_dir / "summary_by_bank.json"
metrics_file = reports_dir / "metrics_by_field.json"

if not review_file.exists():
    st.warning("No review report found. Run backend/cli/review_report.py first to generate reports.")
    # still allow direct parsing of synthetic PDFs below

with open(summary_file, "r") if summary_file.exists() else (None) as fh:
    bank_summary = json.load(fh) if fh else []

# Load reviews if available
reviews = []
if review_file.exists():
    with open(review_file, "r") as fh:
        reviews = json.load(fh)

st.sidebar.header("Filters")
# derive banks from reports or labels folder
labels_path = Path("synthetic_data/labels.json")
banks = []
if labels_path.exists():
    labels = json.loads(labels_path.read_text())
    banks = sorted({l.get("issuer","UNKNOWN") for l in labels})
else:
    banks = sorted({r.get("label",{}).get("issuer","UNKNOWN") for r in reviews if "label" in r})

sel_bank = st.sidebar.selectbox("Bank (filter)", options=["ALL"] + banks)
min_score = st.sidebar.slider("Min aggregate score", min_value=0.0, max_value=1.0, value=0.0, step=0.05)
commit_sqlite = st.sidebar.checkbox("Save re-parsed result to SQLite (when re-parsing)", value=False)

# List synthetic PDFs
pdfs = sorted([p for p in Path("synthetic_data/pdfs").glob("*.pdf")])
pdf_select = st.selectbox("Select PDF to inspect / re-run parser", options=[""] + [str(p) for p in pdfs])

col1, col2 = st.columns([2, 1])
with col2:
    st.header("Bank Summary")
    if Path("reports/summary_by_bank.json").exists():
        st.table(pd.DataFrame(json.loads(Path("reports/summary_by_bank.json").read_text())))
    else:
        st.info("Run review_report.py to create bank summary.")

with col1:
    st.header("Parsed Files (quick view)")
    # create df from reviews if available, else show labels
    rows = []
    for r in reviews:
        if "label" not in r:
            continue
        bank = r["label"].get("issuer","UNKNOWN")
        if sel_bank != "ALL" and bank != sel_bank:
            continue
        if r.get("aggregate_score",0.0) < min_score:
            continue
        rows.append({
            "file": r["file"],
            "issuer": bank,
            "aggregate_score": r.get("aggregate_score", 0.0),
            "comments": "; ".join(r.get("comments", []))[:200]
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

st.markdown("---")
st.header("Detailed File Review / Re-run Parser")

if pdf_select:
    pdf_path = Path(pdf_select)
    st.subheader(f"File: {pdf_path.name}")
    # show stored review if exists
    existing = next((r for r in reviews if r.get("file")==str(pdf_path)), None)
    if existing:
        st.write("Existing review (from reports):")
        st.json(existing.get("scores", {}))
        st.write("Comments:")
        for c in existing.get("comments", []):
            st.warning(c)

    # one-click re-run
    if st.button("Re-run parser for this PDF"):
        st.info("Re-parsing — this may take a few seconds...")
        txt = extract_text(str(pdf_path))
        # detect issuer and parse
        issuer_guess = None
        for k in ["HDFC","ICICI","SBI","AXIS","AMEX"]:
            if k.lower() in (txt or "").lower():
                issuer_guess = k
                break
        parser = None
        if issuer_guess == "HDFC":
            parser = hdfc
        elif issuer_guess == "ICICI":
            parser = icici
        elif issuer_guess == "SBI":
            parser = sbi
        elif issuer_guess == "AXIS":
            parser = axis
        elif issuer_guess == "AMEX":
            parser = amex
        if parser:
            parsed = parser.parse(txt)
        else:
            parsed = regex_library.generic_parse(txt)
            parsed['issuer_guess'] = issuer_guess or parsed.get('issuer','UNKNOWN')
        parsed['raw_text_snippet'] = (txt or "")[:1500]
        st.subheader("Parsed result (live)")
        st.json(parsed)

        # optionally save parsed result to SQLite
        if commit_sqlite:
            init_db()
            saved_id = save_result(str(pdf_path), parsed)
            st.success(f"Saved parsed result to SQLite id={saved_id}")

    # show raw text snippet and allow copying
    st.subheader("Raw text (snippet)")
    snippet = ""
    try:
        snippet = extract_text(str(pdf_path))[:5000]
    except Exception as e:
        snippet = f"(error extracting raw text) {e}"
    st.text_area("raw_text", value=snippet, height=300)
