import pdfplumber
import io

class TextExtractor:
    """
    Handles the extraction of text and tables from PDF documents.
    """

    @staticmethod
    def extract_text_from_pdf(file_bytes):
        """
        Extracts raw text from a PDF file (provided as bytes).
        
        Args:
            file_bytes (bytes): The PDF file content from Streamlit.
            
        Returns:
            str: The full extracted text from the document.
        """
        text_content = ""
        try:
            # Wrap bytes in BytesIO so pdfplumber can read it like a file
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    # Extract text from the page
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            
            return text_content.strip()
            
        except Exception as e:
            return f"Error extracting text: {str(e)}"

    @staticmethod
    def extract_tables_from_pdf(file_bytes):
        """
        Extracts structured tables from the PDF.
        CRITICAL for Lab Reports where data is in rows/columns.
        
        Returns:
            list: A list of tables, where each table is a list of rows.
        """
        tables = []
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    # extract_tables() finds grid-like structures
                    extracted = page.extract_tables()
                    
                    if extracted:
                        for table in extracted:
                            # Clean up: Replace None with empty strings, strip whitespace
                            clean_table = [
                                [cell.strip() if cell else "" for cell in row] 
                                for row in table
                            ]
                            # Only keep non-empty tables
                            if clean_table:
                                tables.append(clean_table)
                            
            return tables
            
        except Exception as e:
            print(f"Error extracting tables: {str(e)}")
            return []

# --- Quick Test Block ---
if __name__ == "__main__":
    print("TextExtractor module is ready.")