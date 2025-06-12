# FROM python:3.10-slim

# WORKDIR /app

# # Install system dependencies for PyMuPDF if needed
# # RUN apt-get update && apt-get install -y libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# EXPOSE 8501

# # Streamlit will look for .streamlit/secrets.toml in /app/.streamlit
# CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Use an official Python image with Debian base
FROM python:3.9-slim

# Install system dependencies including Tesseract OCR and fonts
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    poppler-utils \
    tesseract-ocr-eng \
    tesseract-ocr-script-latn \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy requirements file and install python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
