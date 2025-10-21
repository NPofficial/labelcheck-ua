"""Document processing service"""

from fastapi import UploadFile
from typing import Optional
import logging

from app.utils.image_processing import ImageProcessor
from app.utils.pdf_processing import PDFProcessor
from app.utils.text_processing import TextProcessor

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for processing uploaded documents"""
    
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.pdf_processor = PDFProcessor()
        self.text_processor = TextProcessor()
    
    async def extract_text(self, file: UploadFile) -> str:
        """
        Extract text from uploaded file
        
        Args:
            file: Uploaded file (image or PDF)
            
        Returns:
            Extracted text
        """
        try:
            logger.info(f"Extracting text from file: {file.filename}")
            
            content = await file.read()
            
            # Determine file type and process accordingly
            if file.content_type in ["image/jpeg", "image/png", "image/jpg"]:
                text = await self.image_processor.extract_text(content)
            elif file.content_type == "application/pdf":
                text = await self.pdf_processor.extract_text(content)
            else:
                raise ValueError(f"Unsupported file type: {file.content_type}")
            
            # Clean and normalize text
            cleaned_text = self.text_processor.clean_text(text)
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}", exc_info=True)
            raise
    
    async def process_image(self, file: UploadFile) -> dict:
        """Process image file"""
        # TODO: Implement image processing
        pass
    
    async def process_pdf(self, file: UploadFile) -> dict:
        """Process PDF file"""
        # TODO: Implement PDF processing
        pass

