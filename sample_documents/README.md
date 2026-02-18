# 🩺 DIAGNOX – Multimodal Clinical Intelligence

**DIAGNOX** is an advanced AI-driven medical document analysis system that transforms complex, unstructured clinical data—including lab reports, radiology findings, prescriptions, and discharge summaries—into actionable, patient-friendly dashboards.

## 🚀 Key Features
* **Multimodal Processing**: Seamlessly handles text-based PDFs and image formats (JPG, PNG) using integrated OCR (Tesseract).
* **Narrative Synthesis**: Specifically designed to extract "Hospital Course" and "Transition of Care" details from dense Clinical Notes.
* **Medication Reconciliation**: Automatically identifies new vs. pre-existing medications and generates medical "Use Cases" for each drug.
* **Intelligent Severity Scoring**: Assigns dynamic risk scores (0-100) to lab markers and clinical findings to highlight urgent issues.

## 🧠 Agentic Architecture
DIAGNOX utilizes a specialized 3-agent pipeline:
1. **File Analysis Agent**: Identifies the document type and handles initial data extraction.
2. **Clinical Text Agent**: Parses unstructured narratives for diagnoses, plans, and observations.
3. **Synthesizer Agent**: Aggregates all findings into a unified JSON structure for the UI dashboard.

## 🛠️ Technical Stack
* **Frontend**: Streamlit
* **Core Model**: Google Gemini 1.5 Flash
* **OCR Engine**: Tesseract OCR
* **Data Parsing**: `pdfplumber`, `Pillow`, `Pandas`
* **Audio**: `gTTS` (for patient summary playback)

## 📦 Deployment Configuration
To ensure the OCR engine works in cloud environments, this project includes a specific `packages.txt` for Debian-based system dependencies.

```text
tesseract-ocr
libtesseract-dev

## 📋 Installation & Local Setup

1. Clone the repository:
git clone [https://github.com/YOUR_USERNAME/DIAGNOX.git](https://github.com/YOUR_USERNAME/DIAGNOX.git)

2. Install dependencies:
pip install -r requirements.txt

3. Set up your .env file:
GEMINI_API_KEY=your_api_key_here

4. Run the app
streamlit run app.py 