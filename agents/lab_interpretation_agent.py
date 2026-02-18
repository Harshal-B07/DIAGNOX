from agents.base_agent import BaseAgent
import json

class LabInterpretationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="LabInterpretationAgent",
            description="Extracts lab results from any format using aggressive pattern matching."
        )

    def run(self, pdf_text, pdf_tables):
        self.logger.info("Starting Universal Lab Analysis...")

        # 1. Prepare Tables (as a backup context for the LLM)
        table_str = json.dumps(pdf_tables, indent=2) if pdf_tables else "[]"

        # 2. THE UNIVERSAL PROMPT
        # We give the AI permission to "hunt" for numbers anywhere near the test name.
        system_prompt = """
        You are a Universal Clinical Data Extractor.
        Your goal is to find Lab Results in messy, unstructured, or multi-page text.

        --- STRATEGY FOR MESSY REPORTS ---
        1. **Keyword Hunting:** Look for specific biomarkers (e.g., "HbA1c", "Glucose", "Creatinine", "TSH", "Hemoglobin").
        2. **Proximity Search:** Once you find a keyword, scan the text IMMEDIATELY AFTER it for numerical values.
        3. **The "Floating Number" Rule:** - In many PDFs, the result appears *lines below* the test name.
           - If you see "HbA1c" and then a list of reference ranges, keep reading until you hit a standalone number (e.g., "10.0"). That is likely the result.
        
        --- MANDATORY OUTPUT FORMAT ---
        You MUST infer the status (HIGH / LOW / NORMAL) based on the reference ranges found in the text.
        If no range is found, estimate based on standard medical knowledge.
        
        IMPORTANT: The 'status' field MUST be one of these exact UPPERCASE strings:
        - "HIGH"
        - "LOW"
        - "CRITICAL"
        - "NORMAL"
        
        Return ONLY valid JSON:
        {
            "lab_results": [
                {
                    "parameter": "Exact Test Name Found",
                    "value": "The Number",
                    "unit": "The Unit (e.g. mg/dL, %)",
                    "status": "HIGH" (or LOW / NORMAL)
                }
            ]
        }
        """

        # 3. USER CONTENT
        user_content = f"""
        --------------------------------------------------
        FULL DOCUMENT TEXT:
        {pdf_text}
        --------------------------------------------------
        
        TABLE DATA (If any):
        {table_str}
        --------------------------------------------------
        """

        # 4. CALL GEMINI
        response = self.call_gemini(system_prompt, user_content)
        
        # 5. VALIDATION & DEBUGGING
        if "lab_results" not in response:
            self.logger.warning("Agent returned no results.")
            return {"lab_results": []}

        count = len(response['lab_results'])
        self.logger.info(f"✅ Extracted {count} lab parameters.")
        
        return response