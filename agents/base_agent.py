import google.generativeai as genai
import os
import time
import json
from dotenv import load_dotenv
from utils.logger import get_logger

# 1. Load the environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env file!")

genai.configure(api_key=API_KEY)

class BaseAgent:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.logger = get_logger(name)
        
        # --- 2026 CONFIGURATION: HIGH VOLUME MODE ---
        # Primary: The "Lite" model gives us 1,000 requests/day (vs 20 for standard)
        self.primary_model = "gemini-2.5-flash-lite" 
        
        # Backup: If Lite fails, use the standard Flash (20/day limit)
        self.backup_model = "gemini-2.5-flash" 
        
        self.current_model_name = self.primary_model
        self.model = genai.GenerativeModel(self.current_model_name)

    def call_gemini(self, system_prompt, user_content):
        """
        Sends a prompt to Gemini with Rate Limit Hopping.
        """
        retries = 3
        # Fast wait times because we prefer switching models over waiting
        wait_times = [2, 4, 8] 

        for attempt in range(retries):
            try:
                # self.logger.info(f"Sending request to {self.current_model_name} (Attempt {attempt + 1})...")
                response = self.model.generate_content([system_prompt, user_content])
                
                raw_text = response.text.strip()
                # Clean up JSON markdown if present
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:-3].strip()
                elif raw_text.startswith("```"):
                     raw_text = raw_text[3:-3].strip()
                
                try:
                    return json.loads(raw_text)
                except:
                    return {"response": raw_text, "answer": raw_text}

            except Exception as e:
                error_msg = str(e)
                self.logger.warning(f"⚠️ Attempt {attempt+1} failed on {self.current_model_name}: {error_msg}")

                # --- 429 / 503 ERROR HANDLER (The "Traffic Jam" Fix) ---
                if "429" in error_msg or "quota" in error_msg.lower() or "503" in error_msg:
                    
                    # If we are on Primary (Lite), switch to Backup (Standard)
                    if self.current_model_name == self.primary_model:
                        self.logger.warning(f"🚦 Rate Limit Hit on Primary. Hopping to Backup: {self.backup_model}")
                        self.current_model_name = self.backup_model
                        self.model = genai.GenerativeModel(self.current_model_name)
                        time.sleep(1) 
                        continue 
                    
                    # If we are on Backup and STILL hitting limits, switch back to Primary
                    elif self.current_model_name == self.backup_model:
                         self.logger.warning(f"🚦 Rate Limit Hit on Backup. Hopping back to Primary: {self.primary_model}")
                         self.current_model_name = self.primary_model
                         self.model = genai.GenerativeModel(self.current_model_name)
                         time.sleep(2)
                         continue

                # For other errors, just wait and retry
                if attempt < retries - 1:
                    time.sleep(wait_times[attempt])
                else:
                    return {"error": "API_FAILURE", "details": error_msg}
        
        return {"error": "UNKNOWN_FAILURE"}