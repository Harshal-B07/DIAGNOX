
import time
import io
import pytesseract
from PIL import Image
from document_intelligence.text_extractor import TextExtractor
from document_intelligence.document_classifier import validate_document_type
from agents.file_analysis_agent import FileAnalysisAgent
from agents.lab_interpretation_agent import LabInterpretationAgent
from agents.clinical_text_agent import ClinicalTextAgent
from agents.hypothesis_agent import ConditionHypothesisAgent
from agents.synthesizer_agent import SynthesizerAgent
from utils.logger import get_logger
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class Orchestrator:
    def __init__(self):
        self.logger = get_logger("Orchestrator")
        
        # Initialize the AI Team
        self.file_agent = FileAnalysisAgent()
        self.lab_agent = LabInterpretationAgent()
        self.clinical_agent = ClinicalTextAgent()
        self.hypothesis_agent = ConditionHypothesisAgent()
        self.synthesizer_agent = SynthesizerAgent()

    def _smart_extract(self, file_bytes):
        """
        Helper to extract text from either Image or PDF with an early return 
        to prevent PDF logic from crashing on image files.
        """
        # 1. Try to process as an Image first
        is_image = False
        try:
            image = Image.open(io.BytesIO(file_bytes))
            is_image = True
            self.logger.info("File detected as IMAGE. Running Tesseract OCR...")
            
            # Sharpen for medical text
            image = image.convert('L') 
            text = pytesseract.image_to_string(image)
            
            if len(text.strip()) > 10:
                self.logger.info("OCR Successful.")
                return text, [] 
            else:
                self.logger.warning("OCR found almost no text.")
                return "", [] # Return empty rather than crashing in PDF logic
            
        except Exception as e:
            if is_image:
                self.logger.error(f"Image processing failed: {str(e)}")
                return "", []
            # If not an image, it will fall through to PDF logic below
            self.logger.info("Not an image, attempting PDF extraction...")

        # 2. PDF Logic (Only reached if it's NOT an image)
        try:
            text = TextExtractor.extract_text_from_pdf(file_bytes)
            tables = TextExtractor.extract_tables_from_pdf(file_bytes)
            return text, tables
        except Exception as e:
            self.logger.error(f"PDF Extraction failure: {str(e)}")
            return "", []

    def run_pipeline(self, file_bytes, user_selected_type="LAB_REPORT"):
        """
        Runs the full analysis pipeline supporting both PDF and Images.
        """
        self.logger.info(f"--- Starting Analysis Pipeline (Type: {user_selected_type}) ---")
        
        # 1. SMART EXTRACTION (Added Image Support)
        pdf_text, pdf_tables = self._smart_extract(file_bytes)
        
        if not pdf_text or len(pdf_text.strip()) < 5:
            return {"error": "EXTRACTION_FAILED", "message": "Failed to extract text. If this is a scan, ensure it is clear and legible."}

        # 2. VALIDATION
        is_valid = validate_document_type(pdf_text, user_selected_type)
        
        if not is_valid:
            return {
                "error": "VALIDATION_FAILED", 
                "message": f"This does not look like a {user_selected_type}. Please check your file or select the correct category."
            }

        # 3. METADATA EXTRACTION
        file_analysis = self.file_agent.run(pdf_text)
        file_analysis["document_type"] = user_selected_type

        # --- BREATHER 1: Prevent Rate Limit ---
        time.sleep(2) 

        # 4. ROUTING LOGIC
        lab_data = {}
        hypotheses = {}

        if user_selected_type == "LAB_REPORT":
            self.logger.info("Route: Standard Lab Analysis")
            lab_data = self.lab_agent.run(pdf_text, pdf_tables)
            time.sleep(2)
            hypotheses = self.hypothesis_agent.run(lab_data)
        
        else:
            self.logger.info(f"Route: Unstructured Analysis ({user_selected_type})")
            clinical_output = self.clinical_agent.run(pdf_text)
            
            lab_data["critical_findings"] = clinical_output.get("clinical_findings", [])
            lab_data["recommendations"] = clinical_output.get("recommendations", [])
            
            hypotheses = {
                "hypotheses": [
                    {
                        "condition": item, 
                        "probability": "Reported", 
                        "reasoning": "Explicitly stated in the clinical impression."
                    }
                    for item in clinical_output.get("diagnosis_or_impression", [])
                ]
            }

        # --- BREATHER 3: Final Pause ---
        time.sleep(2)

        # 5. SYNTHESIS
        final_report = self.synthesizer_agent.run(
            file_metadata=file_analysis,
            lab_data=lab_data,
            hypotheses=hypotheses
        )

        return final_report