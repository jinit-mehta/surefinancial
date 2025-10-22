from fastapi import APIRouter
from pathlib import Path
from ..utils.pdf_utils import extract_text
from ..parsers import hdfc, icici, sbi, axis, amex

router = APIRouter()

PARSERS = {
    "HDFC": hdfc.parse,
    "ICICI": icici.parse,
    "SBI": sbi.parse,
    "AXIS": axis.parse,
    "AMEX": amex.parse,
}

@router.post("/file")
def parse_file(path: str):
    p = Path(path)
    if not p.exists():
        return {"error": "File not found"}
    text = extract_text(str(p))
    # simple issuer detection
    issuer = "UNKNOWN"
    for key in PARSERS.keys():
        if key.lower() in text.lower():
            issuer = key
            break
    parser = PARSERS.get(issuer, None)
    if parser:
        result = parser(text)
    else:
        # fallback generic parsing using regex library
        from ..utils.regex_library import generic_parse
        result = generic_parse(text)
    result["raw_text_snippet"] = text[:300]
    result["issuer_guess"] = issuer
    return result
