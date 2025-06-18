import streamlit as st
import pymupdf
import os
from ai import generate_creative_outputs, generate_diagram_image_sdxl, load_model
from ocr import extract_handwritten_text, run_full_page_ocr
from utils import get_annot_hash
from export import export_notes_md, export_notes_md_images, get_diagrams_zip

os.environ["STREAMLIT_CONFIG_DIR"] = "/tmp/.streamlit"
os.environ["STREAMLIT_CACHE_DIR"] = "/tmp/.streamlit/cache"

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

if "selected_annots" not in st.session_state:
    st.session_state["selected_annots"] = {}
if "ai_outputs" not in st.session_state:
    st.session_state["ai_outputs"] = {}
if "diagram_images" not in st.session_state:
    st.session_state["diagram_images"] = {}


def get_annotations_from_pdf(doc):
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
                from utils import extract_highlighted_text
                content = extract_highlighted_text(page, annot)
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
                annotations_by_slide.setdefault(page_number, []).append(annotation_data)
            annot = annot.next
    return annotations_by_slide


uploaded_file = st.file_uploader("Upload an annotated PDF", type="pdf")

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    # Try extracting annotations with PyMuPDF first
    annotations_by_slide = get_annotations_from_pdf(doc)

    #Then Try OCR if fails PyMuPDF
    if not annotations_by_slide:
        st.warning("No standard annotations found in the PDF. Running full-page OCR, this might take some time...")
        annotations_by_slide = run_full_page_ocr(doc, st)

        #If OCR fails as well
        if not annotations_by_slide:
            st.error("No text detected via OCR either. Please try a different PDF or check your file.")
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
