import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

st.title("Universal Sports PDF Extractor")
st.markdown("Upload any sports match PDF to extract a summary and key highlights.")

def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        text = ""
    return text

def fallback_ocr(uploaded_file):
    uploaded_file.seek(0)
    images = []
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img)
            images.append(text)
    return "\n".join(images)

def summarize(text):
    lines = text.split("\n")
    summary = []
    highlights = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        lower = line.lower()
        if "won" in lower or "defeated" in lower or "beat" in lower:
            summary.append(f"🏆 Summary: {line}")
        if any(word in lower for word in ["goal", "score", "run", "minute", "shot", "assist"]):
            highlights.append(f"🔹 Highlight: {line}")
    return summary, highlights

pdf_file = st.file_uploader("Upload PDF", type="pdf")

if pdf_file:
    st.info("Extracting text from PDF...")
    raw_text = extract_text_from_pdf(pdf_file)

    if not raw_text.strip():
        st.warning("Text not detected. Trying OCR fallback...")
        raw_text = fallback_ocr(pdf_file)

    if raw_text.strip():
        st.success("Text extraction complete.")
        summary, highlights = summarize(raw_text)

        if summary:
            st.subheader("📄 Match Summary")
            for line in summary:
                st.write(line.replace("🏆 ", ""))  # Clean emoji
        if highlights:
            st.subheader("📌 Key Highlights")
            for line in highlights:
                st.write(line.replace("🔹 ", ""))  # Clean emoji
        st.download_button("Download Extracted Text", raw_text, file_name="summary.txt")
    else:
        st.error("Sorry, no text could be extracted from this PDF.")
