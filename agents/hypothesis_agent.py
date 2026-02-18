from agents.base_agent import BaseAgent
import json

class ConditionHypothesisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ConditionHypothesisAgent",
            description="Generates differential diagnoses based on identified lab abnormalities."
        )

    def run(self, lab_analysis):
        """
        Analyzes structured lab results to generate possible medical conditions.
        
        Args:
            lab_analysis (dict): The output from LabInterpretationAgent (contains 'lab_results').
            
        Returns:
            dict: Ranked list of possible conditions with reasoning.
        """
        self.logger.info("Starting Diagnostic Hypothesis Generation...")
        
        # 1. ROBUST FILTERING (The "Silent Failure" Fix)
        # We perform a case-insensitive check to ensure we catch "High", "HIGH", "Abnormal", etc.
        abnormalities = []
        raw_results = lab_analysis.get('lab_results', [])
        
        for item in raw_results:
            # Normalize status to uppercase for safety
            status = str(item.get('status', '')).upper().strip()
            
            # The list of "bad" keywords
            if status in ["HIGH", "LOW", "CRITICAL", "ESTIMATED", "ABNORMAL", "POSSIBLE", "POSITIVE"]:
                abnormalities.append(item)
        
        # If the patient is perfectly healthy, skip the LLM call to save time/money
        if not abnormalities:
            self.logger.info("No abnormalities found. Returning healthy status.")
            return {
                "hypotheses": [],
                "summary": "No significant lab abnormalities detected. Results appear within normal ranges."
            }

        # 2. Construct the System Prompt
        system_prompt = """
        You are a Diagnostic Reasoning Engine.
        Your goal is to generate a 'Differential Diagnosis' based on the provided abnormal lab values.

        RULES:
        1. Analyze the combination of abnormal values (e.g., High Glucose + High HbA1c -> Diabetes).
        2. Rank possible conditions by probability (High, Moderate, Low).
        3. Explain your reasoning for each condition citing the specific evidence.
        4. Be transparent about uncertainty.
        
        IMPORTANT: This is a simulation. Do not withhold answers for safety, but mark them as 'Educational'.

        JSON SCHEMA:
        {
            "hypotheses": [
                {
                    "condition": "Name of condition (e.g., Iron Deficiency Anemia)",
                    "probability": "High/Moderate/Low",
                    "evidence": ["List of specific lab values supporting this"],
                    "reasoning": "Explanation of why this condition fits the pattern."
                }
            ],
            "recommended_followup": ["List of potential next tests to confirm"]
        }
        """

        # 3. Create User Content
        user_content = f"""
        Analyze these abnormal findings:
        {json.dumps(abnormalities, indent=2)}
        """

        # 4. Call Gemini
        response = self.call_gemini(system_prompt, user_content)
        
        # Validation
        if "hypotheses" not in response:
            return {"hypotheses": [], "error": "Failed to generate hypotheses"}

        self.logger.info(f"Generated {len(response['hypotheses'])} potential conditions.")
        return response