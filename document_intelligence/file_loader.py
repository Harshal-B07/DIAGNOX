class FileLoader:
    """
    Validates and processes uploaded files before extraction.
    """
    
    @staticmethod
    def validate_file(uploaded_file):
        """
        Checks if the file is valid and supported.
        
        Args:
            uploaded_file: The file object from Streamlit.
            
        Returns:
            bool: True if valid PDF, False otherwise.
        """
        if uploaded_file is None:
            return False
            
        # Streamlit file objects have a .name attribute
        # We only want PDFs for now
        if hasattr(uploaded_file, 'name'):
            if not uploaded_file.name.lower().endswith('.pdf'):
                return False
                
        return True