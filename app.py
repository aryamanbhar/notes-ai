import streamlit as st
import pymupdf 
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

if not api_key:
    st.error("OpenAI API key not found. Please set it in your .env file.")
    st.stop()

st.set_page_config(page_title="notes-ai PDF Annotation Explorer", layout="wide")
st.title("notes-ai PDF Annotation Explorer")
st.markdown(
    """
    Upload an annotated PDF. View slides, see your highlights/notes, and select which ones to send to the AI!
    """
)

uploaded_file = st.file_uploader("Upload an annotated PDF", type="pdf")

#ASK LLM
def ask_llm(annotation, context):
    prompt = f"Explain this annotation for a student: '{annotation}'\n\nSlide context: '{context}'\n\nKeep it concise and beginner-friendly."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    # return response['choices'][0]['message']['content'].strip()
    return response.choices[0].message.content.strip()


if uploaded_file:
    # Load PDF from uploaded file
    pdf_bytes = uploaded_file.read()
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    # Store annotation selections in session state
    if "selected_annots" not in st.session_state:
        st.session_state["selected_annots"] = {}
    
    #Store explanation in session state
    if "ai_explanations" not in st.session_state:
        st.session_state["ai_explanations"] = {}

    st.sidebar.header("Extracted Annotations")
    found_any = False
    annotations_list = []

    for page_number, page in enumerate(doc, start=1):
        # Render page image
        pix = page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5))
        img_bytes = pix.tobytes("png")
        st.image(img_bytes, caption=f"Page {page_number}", width=500)

        # Get all text on the page for context
        slide_context = page.get_text().strip().replace('\n', ' ')

        # Extract annotations
        annot = page.first_annot
        while annot:
            annot_type = annot.type[0]
            annot_label = None
            content = annot.info.get("content", "")

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

            if annot_label and content:
                found_any = True
                key = f"{page_number}-{annot.xref}"
                checked = st.sidebar.checkbox(
                    f"Page {page_number} | {annot_label}: {content}",
                    key=key,
                    value=True
                )
                if checked:
                    annotations_list.append({
                        "page": page_number,
                        "type": annot_label,
                        "text": content,
                        "context": slide_context,
                        "key": key
                    })
            annot = annot.next

    if not found_any:
        st.info("No extractable annotations found in this PDF.")
    else:
        st.sidebar.markdown("---")
        if st.sidebar.button("Send selected to AI"):
            st.session_state["ai_explanations"] = {}  # Reset explanations
            with st.spinner("Contacting OpenAI..."):
                for annot in annotations_list:
                    try:
                        explanation = ask_llm(annot["text"], annot["context"])
                        st.session_state["ai_explanations"][annot["key"]] = explanation
                    except Exception as e:
                        st.session_state["ai_explanations"][annot["key"]] = f"Error: {e}"

    # Display AI explanations below each page
    if st.session_state.get("ai_explanations"):
        st.header("AI Explanations")
        for annot in annotations_list:
            key = annot["key"]
            if key in st.session_state["ai_explanations"]:
                st.markdown(f"**Page {annot['page']} | {annot['type']}:** {annot['text']}")
                st.success(st.session_state["ai_explanations"][key])

else:
    st.info("Upload an annotated PDF to get started.")