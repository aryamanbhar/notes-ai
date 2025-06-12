import streamlit as st
import pymupdf
from PIL import Image
import io
import pytesseract
import os
import requests
import json
from dotenv import load_dotenv
import logging
import base64
import zipfile
import hashlib


# Suppress Streamlit-Torch warnings
logging.getLogger("streamlit").setLevel(logging.ERROR)

# Set Tesseract path (change if you're on Linux/Mac)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="notes-ai PDF Annotation Explorer",
    layout="wide"
)
st.title("notes-ai PDF Annotation Explorer")
st.markdown(
    """
    Upload an annotated PDF to view slides and get AI-generated ELI5 explanations, mnemonics, analogies, and diagrams for each annotation, including handwritten notes, organized by slide!
    """
)

@st.cache_resource
def load_model():
    api_key = os.getenv("HF_API_KEY")
    if not api_key:
        raise ValueError("HF_API_KEY not found in .env file")
    return api_key

def get_annot_hash(annotation, context, slide, typ):
    return hashlib.sha256(f"{annotation}|{context}|{slide}|{typ}".encode()).hexdigest()

def extract_handwritten_text(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        return f"⚠️ OCR Error: {str(e)}"

def generate_creative_outputs(annotation, slide_context, slide_number, annot_type):
    try:
        api_key = load_model()
        headers = {"Authorization": f"Bearer {api_key}"}
        prompt = (
            f"You are an expert tutor creating engaging study aids for a student. "
            f"Slide {slide_number} content: '{slide_context[:500]}'.\n"
            f"Annotation ({annot_type}): '{annotation}'.\n"
            f"Return a JSON object with:\n"
            f"- 'el5': A concise, beginner-friendly explanation (max 100 words, simple language).\n"
            f"- 'mnemonic': A short, memorable phrase to recall the concept.\n"
            f"- 'analogy': A relatable analogy connecting the concept to daily life (max 100 words).\n"
            f"- 'diagram_prompt': A short, clear prompt for an AI image generator to create a diagram that visually explains the annotation and its context (max 30 words).\n"
            f"Ensure the JSON is valid and outputs are clear, creative, and accurate."
        )
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 350, "temperature": 0.7}
        }
        response = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1",
            headers=headers,
            json=payload
        )
        if response.status_code == 403:
            return {"error": "⚠️ API access denied. Check HF_API_KEY or rate limits."}
        elif response.status_code != 200:
            return {"error": f"⚠️ API error: {response.status_code} - {response.text}"}
        try:
            output = response.json()[0]["generated_text"]
            # Extract JSON from output
            json_start = output.find("{")
            json_end = output.rfind("}") + 1
            if json_start != -1 and json_end != -1:
                outputs = json.loads(output[json_start:json_end])
            else:
                outputs = {
                    "el5": "Failed to generate ELI5",
                    "mnemonic": "Failed to generate mnemonic",
                    "analogy": "Failed to generate analogy",
                    "diagram_prompt": ""
                }
        except (json.JSONDecodeError, KeyError):
            outputs = {
                "el5": "Failed to generate ELI5",
                "mnemonic": "Failed to generate mnemonic",
                "analogy": "Failed to generate analogy",
                "diagram_prompt": ""
            }
        return outputs
    except Exception as e:
        return {"error": f"⚠️ Error: {str(e)}"}

def generate_diagram_image_sdxl(diagram_prompt):
    try:
        api_key = load_model()
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"inputs": diagram_prompt}
        response = requests.post(
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
            headers=headers,
            json=payload,
            timeout=120,
        )
        if response.status_code == 200 and response.headers.get("content-type", "").startswith("image"):
            return response.content
        else:
            # Print error for debugging
            st.warning(f"Stable Diffusion API error ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        st.error(f"Stable Diffusion error: {e}")
        return None

def export_notes_md(annotations_by_slide):
    notes = []
    for page_number in annotations_by_slide:
        notes.append(f"# Slide {page_number}\n")
        for annot in annotations_by_slide[page_number]:
            key = annot["key"]
            notes.append(f"**{annot['type']}**: {annot['text']}\n")
            if f"accepted_{key}" in st.session_state:
                ai = st.session_state[f"accepted_{key}"]
            elif f"ai_{key}" in st.session_state:
                ai = st.session_state[f"ai_{key}"]
            else:
                ai = {}
            notes.append(f"- **ELI5:** {ai.get('el5','')}")
            notes.append(f"- **Mnemonic:** {ai.get('mnemonic','')}")
            notes.append(f"- **Analogy:** {ai.get('analogy','')}")
            notes.append("\n")
    return "\n".join(notes)


def export_notes_md_images(annotations_by_slide):
    notes = []
    for page_number in annotations_by_slide:
        notes.append(f"# Slide {page_number}\n")
        for annot in annotations_by_slide[page_number]:
            key = annot["key"]
            notes.append(f"**{annot['type']}**: {annot['text']}\n")
            if f"accepted_{key}" in st.session_state:
                ai = st.session_state[f"accepted_{key}"]
            elif f"ai_{key}" in st.session_state:
                ai = st.session_state[f"ai_{key}"]
            else:
                ai = {}
            notes.append(f"- **ELI5:** {ai.get('el5','')}")
            notes.append(f"- **Mnemonic:** {ai.get('mnemonic','')}")
            notes.append(f"- **Analogy:** {ai.get('analogy','')}")
            img_bytes = st.session_state["diagram_images"].get(key)
            if img_bytes:
                b64img = base64.b64encode(img_bytes).decode()
                notes.append(f"![diagram_{key}](data:image/png;base64,{b64img})")
            notes.append("\n")
    return "\n".join(notes)

def get_diagrams_zip(diagram_images_dict):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for key, img_bytes in diagram_images_dict.items():
            if img_bytes:
                zf.writestr(f"diagram_{key}.png", img_bytes)
    zip_buffer.seek(0)
    return zip_buffer



if "selected_annots" not in st.session_state:
    st.session_state["selected_annots"] = {}
if "ai_outputs" not in st.session_state:
    st.session_state["ai_outputs"] = {}
if "diagram_images" not in st.session_state:
    st.session_state["diagram_images"] = {}

uploaded_file = st.file_uploader("Upload an annotated PDF", type="pdf")

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    annotations_by_slide = {}
    for page_number, page in enumerate(doc, start=1):
        slide_context = page.get_text().strip().replace('\n', ' ')
        annot = page.first_annot
        while annot:
            annot_type = annot.type[0]
            content = annot.info.get("content", "")
            annot_label = None

            if annot_type == 1:
                annot_label = "Sticky Note"
            elif annot_type == 2:
                annot_label = "FreeText"
            elif annot_type == 8:
                quads = annot.vertices
                quad_count = int(len(quads) / 4)
                highlighted_chunks = []
                words = page.get_text("words")
                
                for i in range(quad_count):
                    highlight_rect = pymupdf.Quad(quads[i*4:(i+1)*4]).rect
                    
                    # Get words that significantly overlap with the highlight
                    chunk_words = []
                    for word in words:
                        word_rect = pymupdf.Rect(word[:4])
                        # Calculate overlap area
                        intersect = word_rect & highlight_rect
                        if intersect:
                            # Only include if at least 50% of word is in highlight
                            word_area = word_rect.width * word_rect.height
                            overlap_area = intersect.width * intersect.height
                            if overlap_area / word_area > 0.5:
                                chunk_words.append(word[4])
                    
                    chunk = " ".join(chunk_words)
                    if chunk and len(chunk) > 2:
                        highlighted_chunks.append(chunk)
                
                if highlighted_chunks:
                    content = " / ".join(highlighted_chunks)
                    annot_label = "Highlight"
 
            elif annot_type == 9:
                annot_label = "Handwritten"
                rect = annot.rect
                clip = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), clip=rect)
                content = extract_handwritten_text(clip.tobytes("png"))
            else:
                annot_label = None

            if annot_label and content:
                key = f"{page_number}-{annot.xref}"
                priority = 2 if "?" in content else 1
                annotation_data = {
                    "page": page_number,
                    "type": annot_label,
                    "text": content,
                    "context": slide_context,
                    "key": key,
                    "priority": priority
                }
                if page_number not in annotations_by_slide:
                    annotations_by_slide[page_number] = []
                annotations_by_slide[page_number].append(annotation_data)
            annot = annot.next

    if not annotations_by_slide:
        st.info("No extractable annotations found in this PDF.")
    else:
        slide_numbers = list(annotations_by_slide.keys())
        selected_slide = st.sidebar.selectbox("Select Slide", slide_numbers)

        slide = doc[selected_slide - 1]
        st.image(
            slide.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).tobytes("png"),
            caption=f"Slide {selected_slide}",
            width=600
        )
        st.subheader(f"Annotations for Slide {selected_slide}")

        # # --- Batch AI Output Generation ---
        # if st.button("Generate All AI Outputs for This Slide", key="gen-all-ai"):
        #     with st.spinner("Generating AI outputs for all annotations on this slide..."):
        #         for annot in annotations_by_slide[selected_slide]:
        #             key = annot["key"]
        #             annot_hash = get_annot_hash(annot["text"], annot["context"], annot["page"], annot["type"])
        #             if f"ai_{key}" not in st.session_state:
        #                 ai_outputs = generate_creative_outputs(
        #                     annot["text"], annot["context"], annot["page"], annot["type"]
        #                 )
        #                 st.session_state[f"ai_{key}"] = ai_outputs
        #     st.success("All AI outputs generated for this slide!")


        # # --- Batch Diagram Generation ---
        # if st.button("Generate Diagrams for All Annotations", key="gen-all-diagrams"):
        #     with st.spinner("Generating diagrams..."):
        #         for annot in annotations_by_slide[selected_slide]:
        #             key = annot["key"]
        #             ai_outputs = st.session_state.get(f"ai_{key}")
        #             if ai_outputs:
        #                 diagram_prompt = ai_outputs.get('diagram_prompt', '')
        #                 if diagram_prompt:
        #                     image_bytes = generate_diagram_image_sdxl(diagram_prompt)
        #                     if image_bytes:
        #                         st.session_state["diagram_images"][key] = image_bytes
        #     st.success("All diagrams generated for this slide!")


        #Annotation loop
        for annot in sorted(annotations_by_slide[selected_slide], key=lambda x: x["priority"], reverse=True):
            key = annot["key"]
            with st.expander(f"{annot['type']}: {annot['text'][:60]}"):
                st.markdown(f"**Annotation:** {annot['text']}")
                if st.button(f"Generate AI for slide {key}", key=f"gen-{key}"):
                    ai_outputs = generate_creative_outputs(
                        annot["text"], annot["context"], annot["page"], annot["type"]
                    )
                    st.session_state[f"ai_{key}"] = ai_outputs

                if f"ai_{key}" in st.session_state:
                    ai_outputs = st.session_state[f"ai_{key}"]
                    if "error" in ai_outputs:
                        st.error(ai_outputs["error"])
                    else:
                        st.markdown("**AI Suggestions:**")
                        el5 = st.text_area("ELI5 Explanation", ai_outputs.get('el5', ''), key=f"el5_{key}")
                        mnemonic = st.text_area("Mnemonic", ai_outputs.get('mnemonic', ''), key=f"mnemonic_{key}")
                        analogy = st.text_area("Analogy", ai_outputs.get('analogy', ''), key=f"analogy_{key}")

                        # Always show editable diagram prompt
                        default_prompt = ai_outputs.get('diagram_prompt', '')
                        diagram_prompt = st.text_input(
                            "Diagram Prompt (edit or write your own):",
                            value=default_prompt if default_prompt else "",
                            key=f"diagram_prompt_{key}"
                        )

                        if st.button(f"Generate Diagram for {key}", key=f"diagram-{key}"):
                            with st.spinner("Generating diagram..."):
                                image_bytes = generate_diagram_image_sdxl(diagram_prompt)
                                if image_bytes:
                                    st.session_state["diagram_images"][key] = image_bytes
                                else:
                                    st.session_state["diagram_images"][key] = None

                        img_bytes = st.session_state["diagram_images"].get(key)
                        if img_bytes:
                            st.image(img_bytes, caption="AI-Generated Diagram")

        # --- Export Buttons ---
        md_notes = export_notes_md(annotations_by_slide)
        st.download_button(
            "Download Study Guide as Markdown",
            data=md_notes,
            file_name="study_notes.md",
            mime="text/markdown"
        )

        md_notes_img = export_notes_md_images(annotations_by_slide)
        st.download_button(
            "Download Study Guide (Markdown + Diagrams)",
            data=md_notes_img,
            file_name="study_notes_with_diagrams.md",
            mime="text/markdown"
        )

        if st.session_state["diagram_images"]:
            zip_buffer = get_diagrams_zip(st.session_state["diagram_images"])
            st.download_button(
                "Download All Diagrams as ZIP",
                data=zip_buffer,
                file_name="diagrams.zip",
                mime="application/zip"
            )

else:
    st.info("Upload an annotated PDF to get started.")

st.markdown("---")
st.caption("Powered by Mixtral-8x7B-Instruct-v0.1 & SDXL via Hugging Face | Built with Streamlit")