from agents.base_agent import BaseAgent
import json

class ClinicalTextAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ClinicalTextAgent",
            description="Analyzes unstructured narrative text (Radiology, Clinical Notes, Discharge Summaries)."
        )

    def run(self, pdf_text):
        self.logger.info("Starting Clinical Text Extraction...")

        # 1. Truncate very long documents to fit context (approx 15k chars)
        # Clinical notes can be long, but usually the findings are in the first few pages.
        analyzable_text = pdf_text[:15000]

        system_prompt = """
        You are an Expert Medical Documentation Analyst.
        Your goal is to extract structured clinical data from unstructured narrative text.
        
        This agent handles:
        1. RADIOLOGY REPORTS (X-Ray, CT, MRI, Ultrasound)
        2. CLINICAL NOTES (Discharge Summaries, H&P, Consultations)
        3. PRESCRIPTIONS (Medication lists)
        4. LAB REPORTS (Contextual text or summaries)

        --- INSTRUCTIONS ---
        - Ignore headers, footers, disclaimers, and administrative info.
        - If the document is a PRESCRIPTION:
            * Extract medications into 'clinical_findings' using the format: "Drug Name | Dosage | Duration".
            * Identify the medical "Use Case" for each drug (e.g., 'Antibiotic for infection') and list it in 'diagnosis_or_impression'.
            * Extract "Advice Given" (e.g., 'AVOID OILY AND SPICY FOOD') into 'recommendations'.
        - If the document is RADIOLOGY, extract the 'Impression' or 'Conclusion' verbatim.
        - If the document is a CLINICAL NOTE:
            * Extract the 'Discharge Diagnosis' into 'diagnosis_or_impression'. [cite: 8]
            * Extract the 'Hospital Course' (Summary of issues addressed) into 'clinical_findings'. [cite: 39]
            * Extract 'Allergies', 'Follow-up Instructions', and 'Warning Signs' into 'recommendations'. [cite: 137, 157, 160]
            * For any discharge medications found, use the format: "NEW/CONTINUE: Drug Name | Dosage". [cite: 140, 153]
        - If the document is a LAB REPORT, extract the high-level summary of findings.

        --- JSON SCHEMA (STRICT) ---
        {
            "clinical_findings": [
                "Summary of hospital course, observations, or 'Drug | Dosage | Duration' for prescriptions."
            ],
            "diagnosis_or_impression": [
                "The primary conclusion, discharge diagnosis, or 'Medicine Use Case' for prescriptions."
            ],
            "recommendations": [
                "List of actionable steps, allergies, follow-up plans, or warning signs found in the text."
            ],
            "report_type_detected": "RADIOLOGY / CLINICAL_NOTE / PRESCRIPTION / LAB_REPORT / UNKNOWN"
        }
        """

        # 2. Call Gemini
        response = self.call_gemini(system_prompt, analyzable_text)
        
        return response