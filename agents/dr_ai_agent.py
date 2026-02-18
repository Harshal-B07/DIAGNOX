from agents.base_agent import BaseAgent

class DrDiagnaAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Dr. Diagna", description="Interactive Medical Assistant")
    
    def ask(self, user_question, analysis_context, chat_history, language="English"):
        """
        Answers user questions based on the analysis result OR general medical knowledge.
        """
        system_prompt = f"""
        You are Dr. Diagna, a compassionate and highly knowledgeable AI medical assistant for DIAGNOX.
        
        CONTEXT:
        The user has uploaded a medical document. Here is the AI analysis of that document:
        {analysis_context}
        
        USER SETTINGS:
        Selected Language: {language}
        
        YOUR INSTRUCTIONS:
        1. **Context-Aware:** If the user asks about their specific results (e.g., "Is my iron low?"), look at the analysis context above and answer based on those facts.
        2. **General Knowledge:** If the user asks general medical questions (e.g., "What is anemia?", "Side effects of aspirin?"), answer using your general medical knowledge, even if it's not in the report.
        3. **Explain Like I'm 5 (ELI5):** Avoid medical jargon. Explain complex terms simply.
        4. **Polyglot:** Answer in the '{language}' language. If the medical term is standard in English (like "Hemoglobin"), you may keep it in English but explain it in {language}.
        5. **Lifestyle Coaching:** If relevant, suggest simple dietary or lifestyle changes.
        
        CRITICAL GUARDRAILS:
        - NEVER give a definitive diagnosis (e.g., "You have cancer"). Instead say "This suggests..." or "It is consistent with..."
        - ALWAYS advise the user to consult a doctor for treatment.
        
        CHAT HISTORY:
        {chat_history}
        """
        
        # We construct a prompt that asks for a direct string response (not JSON) for natural chat
        prompt = f"User Question: {user_question}\n\nPlease answer in {language}."
        
        response = self.call_gemini(system_prompt, prompt)
        
        # If the base agent returns a dict (JSON), try to extract text. 
        # If it returns a string, use it directly.
        if isinstance(response, dict):
            return response.get("answer", response.get("response", "I'm having trouble thinking right now. Please try again."))
        return response