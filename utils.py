import pymupdf
import hashlib

def get_annot_hash(annotation, context, slide, typ):
    return hashlib.sha256(f"{annotation}|{context}|{slide}|{typ}".encode()).hexdigest()

def extract_highlighted_text(page, annot):
    quads = annot.vertices
    quad_count = int(len(quads) / 4)
    highlighted_chunks = []
    words = page.get_text("words")

    for i in range(quad_count):
        highlight_rect = pymupdf.Quad(quads[i*4:(i+1)*4]).rect
        chunk_words = []
        for word in words:
            word_rect = pymupdf.Rect(word[:4])
            intersect = word_rect & highlight_rect
            if intersect:
                word_area = word_rect.width * word_rect.height
                overlap_area = intersect.width * intersect.height
                if overlap_area / word_area > 0.5:
                    chunk_words.append(word[4])
        chunk = " ".join(chunk_words)
        if chunk and len(chunk) > 2:
            highlighted_chunks.append(chunk)
    return " / ".join(highlighted_chunks)
