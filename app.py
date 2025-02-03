import streamlit as st
from transformers import pipeline
from PyPDF2 import PdfReader
import docx
from PIL import Image
import pytesseract
import io
import re

# Helper function to replace gender-specific pronouns with neutral terms
def replace_gender_pronouns(text):
    # Replace gendered pronouns with neutral alternatives
    text = re.sub(r'\bhe\b', 'the candidate', text, flags=re.IGNORECASE)
    text = re.sub(r'\bshe\b', 'the candidate', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhim\b', 'the candidate', text, flags=re.IGNORECASE)
    text = re.sub(r'\bher\b', 'the candidate', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhis\b', 'the candidate\'s', text, flags=re.IGNORECASE)
    text = re.sub(r'\bher\'s\b', 'the candidate\'s', text, flags=re.IGNORECASE)
    return text

# Modify the summarizer function to replace pronouns
def summarize_and_replace(text):
    summarizer = load_summarizer()
    with st.spinner("Summarizing..."):
        summary = summarizer(text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
    
    # Replace gender pronouns in the summary
    summary = replace_gender_pronouns(summary)
    return summary

# Helper function to extract text from uploaded files
def extract_text(file):
    if file.type == "application/pdf":
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type.startswith("image/"):
        # Use OCR to extract text from images
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
        return text
    else:
        return None

# Load a summarization model
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

# Streamlit app
def main():
    st.title("Resume Summarizer")
    st.write("Upload your resume (PDF, Word, Text, or Image), and get a summarized version.")

    uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])

    if uploaded_file:
        text = extract_text(uploaded_file)
        if not text:
            st.error("Could not extract text from the uploaded file. Please try again.")
            return

        st.subheader("Extracted Text")
        st.text_area("Full Text", text, height=300)

        # Summarize the text
        summarizer = summarize_and_replace(text)
        with st.spinner("Summarizing..."):
            summary = summarizer(text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']

        st.subheader("Summary")
        st.write(summary)

if __name__ == "__main__":
    main()