import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# --- 1. ROBUST PATH SETUP ---
# Defines the root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# --- 2. LOAD ENVIRONMENT VARIABLES ---
# Loads .env file. override=True ensures changes to .env are picked up.
load_success = load_dotenv(dotenv_path=ENV_PATH, override=True)

if not load_success:
    print(f"⚠️ WARNING: Could not load .env file at: {ENV_PATH}")

# --- 3. API KEY CONFIGURATION ---
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    # We raise a clear error if the key is missing to prevent silent failures later
    raise ValueError(
        f"\n❌ CRITICAL ERROR: API Key missing.\n"
        f"Please ensure you have a file named '.env' at: {ENV_PATH}\n"
        f"And it contains the line: GOOGLE_API_KEY=your_key_here"
    )

# Configure the Gemini library globally
genai.configure(api_key=API_KEY)

# --- 4. MODEL SELECTION ---
# We use the Flash model for high speed and low latency
MODEL_NAME = "gemini-2.5-flash-lite" 

# --- 5. LOGGING CONFIGURATION ---
LOG_DIR = BASE_DIR / "outputs" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)