from agents.base_agent import BaseAgent
import json
from datetime import datetime

class SynthesizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SynthesizerAgent",
            description="Aggregates all analysis into a final, readable diagnostic report."
        )

    def run(self, file_metadata, lab_data, hypotheses):
        self.logger.info("Synthesizing final diagnostic report...")

        # 1. Prepare Data
        context_str = f"""
        METADATA: {json.dumps(file_metadata)}
        FINDINGS/RESULTS: {json.dumps(lab_data)}
        DIAGNOSIS/HYPOTHESES: {json.dumps(hypotheses)}
        """

        # 2. System Prompt (UPDATED FOR CLINICAL NOTES INTEGRATION)
        system_prompt = """
        You are an Empathetic Medical AI Assistant.
        Your task is to synthesize clinical data into a clear report for a PATIENT.
        
        --- CRITICAL: METADATA EXTRACTION ---
        You MUST attempt to find the **Patient Name** in the provided text. [cite: 5]
        If found, put it in the metadata field. If not, use "Unknown".

        --- INSTRUCTION: GROUPING & SCORING ---
        1. **Categorize** findings based on report type:
           - For LAB_REPORTS: Group by Body System (e.g., "Metabolic Health").
           - For PRESCRIPTIONS: Group under "Current Medications". Use 'value' for Dosage and 'reference_range' for Duration.
           - For CLINICAL_NOTES: Group by "Hospital Course" and "Discharge Medications". [cite: 29, 140]
           - For RADIOLOGY: Group by Anatomy (e.g., "Dental Findings"). [cite: 133]
        2. **Assign a Severity Score** (0-100):
           - Clinical Notes: Use higher scores for "Developed Conditions" (e.g., Sepsis, AKI) or critical allergies. [cite: 22, 137, 138]
           - Prescriptions: Use 0 (Green) for standard meds, higher only for interactions.
           - Lab/Radiology: Use standard 0-20 (Normal), 21-60 (Abnormal), 61-100 (Critical).
        3. **Reference Ranges / Usage**: 
           - For Lab Reports, include medical reference ranges. [cite: 65, 68, 69]
           - For Clinical Notes, use this field to specify if a medication is "NEW" or "CONTINUED". 
        4. **Explain Use Case**: In the 'explanation' field, explain the "Why" (e.g., 'Ciprofloxacin: Started to treat kidney infection found during stay'). [cite: 40, 47]

        --- JSON SCHEMA ---
        {
            "metadata": {
                "patient_name": "string (Extract from text or 'Unknown')",
                "report_date": "string (Extract from text or 'Unknown')"
            },
            "patient_summary": "string (3-4 sentences summarizing the stay or the health findings)",
            "critical_findings": ["List of urgent issues, new diagnoses, or 'Red Flags'"],
            "warnings": ["List of allergies, side effects, or non-urgent issues"],
            "grouped_findings": {
                "System or Category Name": [
                    {
                        "name": "Biomarker / Medicine / Hospital Issue", 
                        "value": "Result / Dosage / Status", 
                        "reference_range": "Range / Duration / Change Status", 
                        "status": "HIGH/LOW / PRESCRIBED / RESOLVED", 
                        "explanation": "Clinical meaning or Treatment goal", 
                        "severity_score": number
                    }
                ]
            },
            "diagnosis_section": [
                {
                    "condition": "Discharge Diagnosis or Condition Name",
                    "likelihood": "Reported / High",
                    "explanation": "Summary of the clinical story or reasoning."
                }
            ],
            "recommendations": {
                "medical_next_steps": ["Follow-up appointments and future lab work"],
                "lifestyle_actions": ["Dietary or activity restrictions mentioned"]
            }
        }
        """

        # 3. Call Gemini
        response = self.call_gemini(system_prompt, context_str)
        
        if isinstance(response, dict):
            response["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        return response