import pymupdf

pdf_path = r"C:\Users\Aryaman\Desktop\notes-ai\samples\annotated_example.pdf"
doc = pymupdf.open(pdf_path)

for page_number, page in enumerate(doc, start=1):
    annot = page.first_annot
    while annot:
        annot_type = annot.type[0]
        info = annot.info
        content = info.get("content", "")
        # 1: Sticky note, 2: FreeText, 8: Highlight
        if annot_type == 1:
            print(f"Page {page_number} | Sticky Note: {content}")
        elif annot_type == 2:
            print(f"Page {page_number} | FreeText: {content}")
        elif annot_type == 8:
            # For highlights, extract the highlighted text
            quads = annot.vertices
            quad_count = int(len(quads) / 4)
            highlighted_text = ""
            for i in range(quad_count):
                rect = pymupdf.Quad(quads[i*4:(i+1)*4]).rect
                highlighted_text += page.get_textbox(rect) + " "
            print(f"Page {page_number} | Highlighted: {highlighted_text.strip()}")
        annot = annot.next