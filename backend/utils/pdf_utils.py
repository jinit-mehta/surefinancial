import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

def extract_text(path: str) -> str:
    # Try pdfplumber first
    try:
        with pdfplumber.open(path) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
            text = "\n".join(pages).strip()
            if text:
                return text
    except Exception as e:
        # continue to fallback
        pass

    # fallback: render pages to images via fitz and OCR with pytesseract
    text_chunks = []
    try:
        doc = fitz.open(path)
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes()))
            page_text = pytesseract.image_to_string(img)
            text_chunks.append(page_text)
        return "\n".join(text_chunks)
    except Exception as e:
        return ""  # return blank if everything fails
