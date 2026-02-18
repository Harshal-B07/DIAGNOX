import google.generativeai as genai
from config.settings import MODEL_NAME
import json

class IntentClassifier:
    """
    Decides if the user is giving a COMMAND or asking a QUESTION.
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel(MODEL_NAME)

    def classify_intent(self, user_text):
        """
        Classifies the user's spoken text.
        
        Returns:
            dict: {"type": "COMMAND" or "QUESTION", "details": ...}
        """
        prompt = f"""
        Analyze the following user input spoken to a medical AI:
        "{user_text}"
        
        Classify it into one of two categories:
        1. COMMAND (e.g., "Analyze this file", "Read the report", "Start diagnosis")
        2. QUESTION (e.g., "What is the hemoglobin?", "Is 10.5 high?", "Explain the risk")
        
        Output ONLY valid JSON:
        {{
            "type": "COMMAND" or "QUESTION",
            "confidence": float (0-1)
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Simple cleanup to ensure we get pure JSON
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as e:
            return {"type": "UNKNOWN", "error": str(e)}