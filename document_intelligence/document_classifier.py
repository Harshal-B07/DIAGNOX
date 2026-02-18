from utils.logger import get_logger

logger = get_logger("DocumentValidator")

def validate_document_type(text: str, user_selection: str) -> bool:
    """
    Validates if the uploaded document matches the user's selected category 
    by scanning for mandatory domain-specific keywords.
    
    Args:
        text (str): The full extracted text from the PDF.
        user_selection (str): The category selected by the user 
                              ("LAB_REPORT", "RADIOLOGY", "CLINICAL_NOTE", "PRESCRIPTION").
                              
    Returns:
        bool: True if the file looks valid, False if it looks wrong.
    """
    text_lower = text.lower()
    
    # --- 1. LAB REPORTS (Tables of Numbers) ---
    # Rule: Must contain at least 2 technical lab terms.
    if user_selection == "LAB_REPORT":
        keywords = ["reference range", "biological ref", "units", "method", "specimen", "collected"]
        matches = sum(1 for word in keywords if word in text_lower)
        
        if matches >= 2:
            return True
        else:
            logger.warning(f"Validation Failed: Selected LAB_REPORT but found only {matches} keywords.")
            return False

    # --- 2. RADIOLOGY (Imaging Narratives) ---
    # Rule: Must contain "findings" OR "impression" (The core of any X-Ray/MRI).
    elif user_selection == "RADIOLOGY":
        if "findings" in text_lower or "impression" in text_lower or "conclusion" in text_lower:
            return True
        else:
            logger.warning("Validation Failed: Selected RADIOLOGY but missing 'Findings' or 'Impression'.")
            return False

    # --- 3. CLINICAL NOTES (Doctor Narratives) ---
    # Rule: Must contain at least 2 standard note headers.
    elif user_selection == "CLINICAL_NOTE":
        keywords = ["diagnosis", "plan", "history", "chief complaint", "discharge summary", "consultation"]
        matches = sum(1 for word in keywords if word in text_lower)
        
        if matches >= 2:
            return True
        else:
            logger.warning(f"Validation Failed: Selected CLINICAL_NOTE but found only {matches} keywords.")
            return False

    # --- 4. PRESCRIPTIONS (Medication Lists) ---
    # Rule: Must contain specific pharmacy terminology.
    elif user_selection == "PRESCRIPTION":
        keywords = ["rx", "prescription", "dose", "dosage", "refill", "sig", "dispense", "tablet", "capsule", "mg"]
        matches = sum(1 for word in keywords if word in text_lower)
        
        if matches >= 1: 
            return True
        else:
            logger.warning("Validation Failed: Selected PRESCRIPTION but found no pharmacy keywords.")
            return False

    # Default safe fallback (if selection is unknown/other, let it pass)
    return True