# import streamlit as st
# import pymupdf
# from dotenv import load_dotenv
# import os
# import requests
# import json
# from PIL import Image
# import io
# import base64
# import pytesseract
# import logging

# # Suppress Streamlit-Torch warnings
# logging.getLogger("streamlit").setLevel(logging.ERROR)

# # Set Tesseract path
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# # Load environment variables
# load_dotenv()

# # Streamlit page config
# st.set_page_config(page_title="notes-ai PDF Annotation Explorer", layout="wide")
# st.title("notes-ai PDF Annotation Explorer")
# st.markdown(
#     """
#     Upload an annotated PDF to view slides and get AI-generated ELI5 explanations, mnemonics, and analogies for each annotation, including handwritten notes, organized by slide!
#     """
# )

# # Cache the Hugging Face API key
# @st.cache_resource
# def load_model():
#     api_key = os.getenv("HF_API_KEY")
#     if not api_key:
#         raise ValueError("HF_API_KEY not found in .env file")
#     return api_key

# # Extract text from image for handwritten notes
# def extract_handwritten_text(image_bytes):
#     try:
#         img = Image.open(io.BytesIO(image_bytes))
#         text = pytesseract.image_to_string(img)
#         return text.strip()
#     except Exception as e:
#         return f"⚠️ OCR Error: {str(e)}"

# # Generate ELI5 explanation, mnemonic, and analogy using Grok-3.1-8b-128k
# def generate_creative_outputs(annotation, slide_context, slide_number, annot_type):
#     try:
#         api_key = load_model()
#         headers = {"Authorization": f"Bearer {api_key}"}
#         prompt = (
#             f"You are an expert tutor creating engaging study aids for a student. "
#             f"Slide {slide_number} content: '{slide_context[:500]}'.\n"
#             f"Annotation ({annot_type}): '{annotation}'.\n"
#             f"Return a JSON object with:\n"
#             f"- 'el5': A concise, beginner-friendly explanation (max 100 words, simple language).\n"
#             f"- 'mnemonic': A short, memorable phrase to recall the concept.\n"
#             f"- 'analogy': A relatable analogy connecting the concept to daily life (max 100 words).\n"
#             f"Ensure the JSON is valid and outputs are clear, creative, and accurate."
#         )
#         payload = {
#             "inputs": prompt,
#             "parameters": {"max_new_tokens": 300, "temperature": 0.7}
#         }
#         response = requests.post(
#             "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1",
#             headers=headers,
#             json=payload
#         )
#         if response.status_code == 403:
#             return {"error": "⚠️ API access denied. Check HF_API_KEY or rate limits."}
#         elif response.status_code != 200:
#             return {"error": f"⚠️ API error: {response.status_code} - {response.text}"}
#         try:
#             output = response.json()[0]["generated_text"]
#             # Extract JSON from output
#             json_start = output.find("{")
#             json_end = output.rfind("}") + 1
#             if json_start != -1 and json_end != -1:
#                 outputs = json.loads(output[json_start:json_end])
#             else:
#                 outputs = {
#                     "el5": "Failed to generate ELI5",
#                     "mnemonic": "Failed to generate mnemonic",
#                     "analogy": "Failed to generate analogy"
#                 }
#         except (json.JSONDecodeError, KeyError):
#             outputs = {
#                 "el5": "Failed to generate ELI5",
#                 "mnemonic": "Failed to generate mnemonic",
#                 "analogy": "Failed to generate analogy"
#             }
#         return outputs
#     except Exception as e:
#         return {"error": f"⚠️ Error: {str(e)}"}

# # Initialize session state
# if "selected_annots" not in st.session_state:
#     st.session_state["selected_annots"] = {}
# if "ai_outputs" not in st.session_state:
#     st.session_state["ai_outputs"] = {}

# # File uploader
# uploaded_file = st.file_uploader("Upload an annotated PDF", type="pdf")


# if uploaded_file:
#     pdf_bytes = uploaded_file.read()
#     doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

#     # Layout: Two columns
#     col1, col2 = st.columns([3, 2])

#     with col1:
#         annotations_by_slide = {}
#         found_any = False

#         for page_number, page in enumerate(doc, start=1):
#             # Render page image
#             pix = page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5))
#             img_bytes = pix.tobytes("png")
#             st.image(img_bytes, caption=f"Slide {page_number}", width=500)

#             # Get slide context
#             slide_context = page.get_text().strip().replace('\n', ' ')

#             # Extract annotations
#             annot = page.first_annot
#             while annot:
#                 annot_type = annot.type[0]
#                 annot_label = None
#                 content = annot.info.get("content", "")

#                 if annot_type == 1:
#                     annot_label = "Sticky Note"
#                 elif annot_type == 2:
#                     annot_label = "FreeText"
#                 elif annot_type == 8:
#                     quads = annot.vertices
#                     quad_count = int(len(quads) / 4)
#                     highlighted_chunks = []
#                     for i in range(quad_count):
#                         rect = pymupdf.Quad(quads[i*4:(i+1)*4]).rect
#                         chunk = page.get_textbox(rect).strip()
#                         if chunk and len(chunk) > 2:
#                             highlighted_chunks.append(chunk)
#                     if highlighted_chunks:
#                         content = " / ".join(highlighted_chunks)
#                         annot_label = "Highlight"
#                 elif annot_type == 9:  # Handwritten note (Ink)
#                     annot_label = "Handwritten"
#                     rect = annot.rect
#                     clip = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), clip=rect)
#                     content = extract_handwritten_text(clip.tobytes("png"))

#                 if annot_label and content:
#                     found_any = True
#                     key = f"{page_number}-{annot.xref}"
#                     priority = 2 if "?" in content else 1
#                     annotation_data = {
#                         "page": page_number,
#                         "type": annot_label,
#                         "text": content,
#                         "context": slide_context,
#                         "key": key,
#                         "priority": priority
#                     }
#                     if page_number not in annotations_by_slide:
#                         annotations_by_slide[page_number] = []
#                     annotations_by_slide[page_number].append(annotation_data)
#                 annot = annot.next

#         if not found_any:
#             st.info("No extractable annotations found in this PDF.")

#     # Sidebar: Display annotations
#     st.sidebar.header("Extracted Annotations")
#     for page_number in annotations_by_slide:
#         for annot in sorted(annotations_by_slide[page_number], key=lambda x: x["priority"], reverse=True):
#             key = annot["key"]
#             checked = st.sidebar.checkbox(
#                 f"Slide {annot['page']} | {annot['type']} | Priority: {annot['priority']}: {annot['text']}",
#                 key=key,
#                 value=True
#             )
#             if checked:
#                 st.session_state["selected_annots"][key] = annot

#     if st.sidebar.button("Generate AI Outputs"):
#         st.session_state["ai_outputs"] = {}
#         with st.spinner("Generating AI outputs..."):
#             for page_number in annotations_by_slide:
#                 for annot in annotations_by_slide[page_number]:
#                     if annot["key"] in st.session_state["selected_annots"]:
#                         try:
#                             outputs = generate_creative_outputs(
#                                 annot["text"], annot["context"], annot["page"], annot["type"]
#                             )
#                             st.session_state["ai_outputs"][annot["key"]] = outputs
#                         except Exception as e:
#                             st.session_state["ai_outputs"][annot["key"]] = {"error": f"Error: {e}"}

#     # Display AI outputs on RHS, grouped by slide
#     with col2:
#         st.header("AI-Generated Outputs")
#         for page_number in sorted(annotations_by_slide.keys()):
#             st.subheader(f"Slide {page_number}")
#             for annot in annotations_by_slide[page_number]:
#                 key = annot["key"]
#                 if key in st.session_state["selected_annots"] and key in st.session_state["ai_outputs"]:
#                     outputs = st.session_state["ai_outputs"][key]
#                     if "error" in outputs:
#                         st.error(outputs["error"])
#                     else:
#                         st.markdown(f"**{annot['type']}:** {annot['text']}")
#                         with st.expander("AI Suggestions"):
#                             st.markdown(f"**ELI5 Explanation**: {outputs['el5']}")
#                             st.markdown(f"**Mnemonic**: {outputs['mnemonic']}")
#                             st.markdown(f"**Analogy**: {outputs['analogy']}")

# else:
#     st.info("Upload an annotated PDF to get started.")

# # Footer
# st.markdown("---")
# st.caption("Powered by Mixtral-8x7B-Instruct-v0.1 via Hugging Face | Built with Streamlit")