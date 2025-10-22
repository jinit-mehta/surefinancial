import streamlit as st
import requests
from pathlib import Path

API_BASE = "http://localhost:8000"
st.set_page_config(page_title="Credit Card Statement Parser", layout="wide")

st.title("Credit Card Statement Parser — Demo")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Upload or Choose")
    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded:
        files = {"file": (uploaded.name, uploaded.getvalue(), "application/pdf")}
        res = requests.post(f"{API_BASE}/upload/", files=files)
        st.write(res.json())
        filepath = res.json().get("filename")
        if st.button("Parse uploaded PDF"):
            parse_res = requests.post(f"{API_BASE}/parse/file", json={"path": filepath})
            st.json(parse_res.json())

    st.markdown("**Or** choose from synthetic data")
    # show first 10 synthetic PDFs if exist
    from glob import glob
    pdfs = sorted(glob("synthetic_data/pdfs/*.pdf"))[:20]
    choice = st.selectbox("Choose synthetic PDF", [""] + pdfs)
    if st.button("Parse selected PDF") and choice:
        parse_res = requests.post(f"{API_BASE}/parse/file", json={"path": choice})
        st.json(parse_res.json())

with col2:
    st.header("Example Output (preview)")
    st.write("Parsed results will appear here as JSON and a small table")
    st.empty()
