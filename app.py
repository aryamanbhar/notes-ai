import streamlit as st
import pymupdf 
import openai

st.set_page_config(page_title="notes-ai PDF Annotation Explorer", layout="wide")
st.title("notes-ai PDF Annotation Explorer")
st.markdown(
    """
    Upload an annotated PDF. View slides, see your highlights/notes, and select which ones to send to the AI!
    """
)

uploaded_file = st.file_uploader("Upload an annotated PDF", type="pdf")

if uploaded_file:
    # Load PDF from uploaded file
    pdf_bytes = uploaded_file.read()
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    # Store annotation selections in session state
    if "selected_annots" not in st.session_state:
        st.session_state["selected_annots"] = {}

    st.sidebar.header("Extracted Annotations")
    found_any = False

    for page_number, page in enumerate(doc, start=1):
        # Render page image
        pix = page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5))
        img_bytes = pix.tobytes("png")
        st.image(img_bytes, caption=f"Page {page_number}", width=500)

        # Extract annotations
        annot = page.first_annot
        while annot:
            annot_type = annot.type[0]
            annot_label = None

            if annot_type == 1:
                annot_label = "Sticky Note"
            elif annot_type == 2:
                annot_label = "FreeText"
            elif annot_type == 8:
                # Try to extract highlighted text
                quads = annot.vertices
                quad_count = int(len(quads) / 4)
                highlighted_chunks = []
                for i in range(quad_count):
                    rect = pymupdf.Quad(quads[i*4:(i+1)*4]).rect
                    chunk = page.get_textbox(rect).strip()
                    if chunk and len(chunk) > 2:
                        highlighted_chunks.append(chunk)
                if highlighted_chunks:
                    content = " / ".join(highlighted_chunks)
                    annot_label = "Highlight"
                else:
                    annot_label = None
            else:
                annot_label = None

            # Show annotation in sidebar with checkbox
            if annot_label:
                found_any = True
                key = f"{page_number}-{annot.xref}"
                if annot_type == 8:
                    content = " / ".join(highlighted_chunks)
                else:
                    content = annot.info.get("content", "")
                st.sidebar.checkbox(
                    f"Page {page_number} | {annot_label}: {content}",
                    key=key,
                    value=True
                )
            annot = annot.next

    if not found_any:
        st.info("No extractable annotations found in this PDF.")

    st.sidebar.markdown("---")
    st.sidebar.button("Send selected to AI (coming soon!)")

else:
    st.info("Upload an annotated PDF to get started.")