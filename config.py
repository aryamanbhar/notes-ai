import os
from dotenv import load_dotenv

load_dotenv()

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
HF_API_KEY = os.getenv("HF_API_KEY")
