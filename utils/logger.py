import logging
import sys
from pathlib import Path
from datetime import datetime

# Define where logs get saved
# We resolve the path relative to this file: utils/logger.py -> utils/ -> root/ -> outputs/logs
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "outputs" / "logs"

# Ensure the log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)

def get_logger(name):
    """
    Creates a standardized logger for agents.
    Logs are saved to outputs/logs/session_YYYY-MM-DD.log
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Check if handlers already exist to avoid duplicate logs (Streamlit reload issue)
    if not logger.handlers:
        # 1. File Handler (Daily log file)
        log_filename = LOG_DIR / f"session_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # 2. Console Handler (To see logs in your terminal with colors)
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter('%(name)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # Prevent propagation to root logger to avoid double printing in Streamlit
        logger.propagate = False
        
    return logger