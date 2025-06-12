# 🧠 notes-ai: Your AI Creative Study Companion

**Turn your annotated lecture slides into personalized study aids — with zero copy-pasting.**

> “Students don’t write fresh notes. They annotate slides. What if AI could read those annotations and *help exactly where you’re confused* — with mnemonics, analogies, and diagrams? That’s what `notes-ai` does.”

---

## 🎯 Problem

Current AI tools (like ChatGPT) require you to:

- Copy-paste from lecture slides
- Manually write prompts
- Parse generic responses
- Repeat this over and over

But most students just highlight, doodle, or question things **directly on slides**. They don’t want to leave their slides behind.

---

## 🚀 Solution: This App

### 📥 Upload PDF slides (with highlights or handwritten notes)
- Detect **annotations**, **highlights**, and **handwritten questions**

### 🧠 Understand what's confusing
- Auto-select annotated content as "priority targets"
- Generate context-aware prompts *without you typing*

### 🎨 Generate creative study aids:
- ✏️ **ELI5 explanations**
- 💡 **Mnemonics & analogies**
- 🖼️ **Diagrams** (via image generation)

### 📤 Export a study guide or enhanced slides

---

## 🧪 Tech Stack

| Area | Tools |
|------|-------|
| Frontend | Streamlit |
| AI/LLMs | OpenAI API |
| OCR | Tesseract, pytesseract |
| PDF Parsing | PyMuPDF |
| Image Processing | OpenCV |
| Diagram Generation | Stable Diffusion XL |
| Deployment | Docker (in progress) |

---

## 🖼️ User Flow

1. **Upload** your annotated PDF (e.g. Samsung Notes or GoodNotes export)
2. **Detect annotations** – both typed highlights & handwritten notes
3. **Auto-select targets** – or uncheck the ones you don’t want help with
4. **AI explains** each one:
   - ELI5 explanation
   - Mnemonic or analogy
   - Optional diagram
5. **Review + Export** as:
   - Study guide (Markdown or ZIP)
   - Enhanced slides (coming soon)

---

## 📌 Why Not Just Use GPT?

| Feature | GPT | `notes-ai` |
|--------|-----|------------|
| Input | Manual text | Full annotated PDFs |
| Annotation-aware | ❌ | ✅ |
| Tailored explanations | ❌ | ✅ |
| Mnemonics & diagrams | ❌ | ✅ |
| Export & reuse | ❌ | ✅ |
| Prompting | Manual | Automated |

---

## 📸 Sample (Coming Soon)

![demo](./screenshots/demo.gif)

---

## 🧰 Setup (Local Dev)

```bash
git clone https://github.com/aryamanbhar/notes-ai.git
cd notes-ai
pip install -r requirements.txt
streamlit run app.py
