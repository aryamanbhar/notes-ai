# 🧠 notes-ai: Your AI-Powered Lecture Companion

University students often annotate over lecture slides with highlights, questions, or typed notes — but when it comes to truly understanding difficult concepts, traditional AI tools fall short.

notes-ai bridges that gap.

## 🎯 Problem

- Students rarely write their own notes from scratch — they annotate slides using iPads, laptops, or styluses.
- When confused, they might:
  - Paste whole PDFs into ChatGPT (losing context)
  - Copy-paste specific lines (tedious, disconnected)
- GPT responses are often **generic**, unaware of the lecture context or the meaning behind annotations.

## 🧪 Solution: Context-Aware AI Study Aids

notes-ai processes **annotated lecture slides** and:
- Detects **highlights**, **typed notes**, and **handwritten annotations**
- Understands the **position**, **intent**, and **context**
- Generates **creative, personalized aids** for those parts:
  - 📘 ELI5 explanations
  - 💡 Mnemonics & analogies
  - 🖼️ Diagrams and visual aids *(Coming Soon)*

## 🚀 Overview

`notes-ai-assistant` integrates Optical Character Recognition (OCR) with Large Language Models (LLMs) from Hugging Face and vision models to transform annotated documents, handwritten notes, and images into structured, searchable, and actionable digital text.

- Uses **Easy OCR** and fallback handwritten text extraction pipelines.
- Utilizes **Hugging Face Inference API** for semantic understanding, summarization, and Q&A with state-of-the-art LLMs (e.g., `facebook/bart-large-cnn`, `google/flan-t5-xl`).
- Integrates **Stable Diffusion** for optional note image enhancements and visualization.
- Built with **Streamlit** for rapid interactive UI and prototyping.
- Containerized with **Docker** for portability and reproducible deployments.

---

## 🧰 Tech Stack & Tools

- **Languages:** Python 3.10+
- **OCR:** [Tesseract OCR](https://github.com/tesseract-ocr/tesseract), `pytesseract`
- **Text Generation:** Hugging Face Large Language Models (LLMs) via [Inference API](https://huggingface.co/inference-api)
- **Image Generation:** Stable Diffusion (Diffusion-based generative model)
- **Web UI:** Streamlit
- **Containerization:** Docker

---

## ⚙️ Features

- Multi-modal OCR pipeline combining typed and handwritten text extraction
- Contextual semantic parsing via Hugging Face LLMs for summaries, questions, and insights
- Real-time annotation recognition from images or PDF uploads
- Modular architecture enabling easy model swaps or upgrades
- Dockerized for local development and scalable cloud deployment



## 👩‍💻 How It Works

1. **Upload PDF slides** — with annotations (highlighted, handwritten, or typed).
2. notes-ai extracts:
   - Slide text
   - Highlighted text (via color detection)
   - Typed notes (via PyMuPDF)
   - Handwritten annotations (via OCR)
3. AI selects annotated content as "focus areas"
4. For each, it auto-generates:
   - Clear ELI5-style explanations
   - Mnemonics or analogies
   - Optional diagrams (text-to-image, planned)
5. User accepts, edits, or inserts AI output into an enhanced slide deck or study guide.

## 🚀 Features

- ✅ Highlight detection (yellow, blue, green, etc.)
- ✅ OCR for handwritten annotations
- ✅ Extraction of typed notes from PDFs
- ✅ Automatic prompt generation — no manual input needed
- ✅ Creative explanations, not just summaries
- 🔜 Reintegration into PDF slides or export as study guides (in development)

## 📸 Example Use Case

> Slide 3: "Gibbs Free Energy"
>
> Annotated question: "Still don’t get what this means for reactions?"
>
> AI Output:
> - 🧠 **ELI5**: Gibbs Free Energy tells you whether a reaction will happen on its own.
> - 🎯 **Mnemonic**: "Go Get Free Energy = G"
> - 🖼️ **Diagram**: [coming soon]

## 🧠 Why It's Better Than Just Using GPT

| GPT | notes-ai |
|-----|----------|
| Requires copy-pasting | Works on full PDFs |
| No awareness of highlights or notes | Understands context, annotations |
| Generic summaries | Tailored explanations |
| No diagrams by default | Generates visuals & mnemonics |
| No reintegration | Designed for slide enhancement |

## 👩‍💻 Access the service

You can use the live app here:

```bash
https://notes-ai-assistant.streamlit.app/



