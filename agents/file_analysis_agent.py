from agents.base_agent import BaseAgent
import json

class FileAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="FileAnalysisAgent",
            description="Classifies the document type and extracts header metadata."
        )

    def run(self, pdf_text):
        self.logger.info("Starting File Analysis & Classification...")

        # INCREASED LIMIT: Give it more text to find headers (was 3000)
        truncated_text = pdf_text[:5000]

        system_prompt = """
        You are a Medical Document Classifier and Metadata Extractor.
        Your job is to look at the TOP section of the document to find patient details and classify the file type.

        --- INSTRUCTIONS FOR METADATA ---
        1.  **Patient Name:** Look for labels like "Patient Name:", "Name:", "Patient:", "For:", or names appearing at the very top left/right. If multiple names exist, try to identify the patient vs. the doctor. If absolutely no name is found, return "Unknown".
        2.  **Report Date:** Look for "Date:", "Report Date:", "Collected Date:", "DOS:" (Date of Service). Return in YYYY-MM-DD format if possible, otherwise use the text found. If none, return "Unknown".
        3.  **Provider:** Look for hospital logos, lab names, or doctor's names in the header/footer.

        --- JSON SCHEMA ---
        {
            "document_type": "CATEGORY_NAME (LAB_REPORT, RADIOLOGY, CLINICAL_NOTE, PRESCRIPTION, OTHER)",
            "metadata": {
                "patient_name": "Extracted Name or 'Unknown'",
                "report_date": "Extracted Date or 'Unknown'",
                "provider": "Extracted Provider or 'Unknown'"
            }
        }
        """

        response = self.call_gemini(system_prompt, truncated_text)
        
        return response