import io
import base64
import zipfile
import streamlit as st

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
