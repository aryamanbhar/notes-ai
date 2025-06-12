import os
from dotenv import load_dotenv
import streamlit as st

try:
    HF_API_KEY = st.secrets["HUGGINGFACE_API_KEY"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    HF_API_KEY = os.getenv("HF_API_KEY")

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
