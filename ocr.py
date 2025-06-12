from PIL import Image
import io
import pytesseract
import pymupdf
import cv2
import numpy as np

# Set Tesseract path (adjust this if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_handwritten_text(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        return f"⚠️ OCR Error: {str(e)}"

def detect_highlighted_text_from_pil_image(pil_image):
    """
    Given a PIL image, detect yellow highlight areas, extract text via OCR.
    Returns a list of extracted highlighted text snippets.
    """
    # Convert PIL Image to OpenCV BGR format
    img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Convert to HSV for color detection
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define yellow highlight color range - tweak if needed
    lower_yellow = np.array([15, 50, 150])
    upper_yellow = np.array([45, 255, 255])

    # Mask only yellow colors
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Optional: remove small noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    mask = cv2.erode(mask, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    highlighted_texts = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h < 500:  # ignore tiny boxes
            continue
        roi = img[y:y+h, x:x+w]
        roi_pil = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
        text = pytesseract.image_to_string(roi_pil, config='--psm 6')
        if text.strip():
            highlighted_texts.append((y, text.strip()))

    # Sort by vertical position (top to bottom)
    highlighted_texts.sort(key=lambda x: x[0])
    final_texts = []
    seen = set()
    for _, txt in highlighted_texts:
        if txt not in seen:
            final_texts.append(txt)
            seen.add(txt)

    return final_texts

    # # Find contours of highlighted areas
    # contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # highlighted_texts = []

    # for cnt in contours:
    #     x, y, w, h = cv2.boundingRect(cnt)
    #     # Crop ROI from original PIL image
    #     roi = pil_image.crop((x, y, x + w, y + h))
    #     text = pytesseract.image_to_string(roi)
    #     if text.strip():
    #         highlighted_texts.append(text.strip())

    # return highlighted_texts

def run_full_page_ocr(doc, st):
    annotations_by_slide = {}
    for page_number, page in enumerate(doc, start=1):
        st.write(f"🔍 Running OCR on Slide {page_number}...")

        try:
            pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
            img_bytes = pix.tobytes("png")
            st.image(img_bytes, caption=f"Slide {page_number} - Rendered Image")

            image = Image.open(io.BytesIO(img_bytes))

            # Run full page OCR
            text = pytesseract.image_to_string(image)
            st.write("✅ Tesseract output:")
            # st.code(text)

            if not text.strip():
                text = "(No readable OCR text found on this page.)"

            # Detect highlighted text snippets in the image
            highlighted_texts = detect_highlighted_text_from_pil_image(image)
            if highlighted_texts:
                st.write("Detected highlighted text snippets via color detection + OCR:")
                for i, snippet in enumerate(highlighted_texts, 1):
                    st.write(f"{i}. {snippet}")

            key = f"{page_number}-ocr"
            annotation_data = {
                "page": page_number,
                "type": "OCR",
                "text": text,
                "context": text,
                "key": key,
                "priority": 0
            }
            annotations_by_slide[page_number] = [annotation_data]

        except Exception as e:
            st.error(f"❌ Error on slide {page_number}: {e}")
    return annotations_by_slide
