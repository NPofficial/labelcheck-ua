"""Text processing utilities"""

import re
import logging
from typing import List

logger = logging.getLogger(__name__)


class TextProcessor:
    """Utility for processing text"""
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        try:
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove special characters (keep Ukrainian characters)
            text = re.sub(r'[^\w\s\u0400-\u04FF.,;:!?()\-]', '', text)
            
            # Strip leading/trailing whitespace
            text = text.strip()
            
            return text
            
        except Exception as e:
            logger.error(f"Error cleaning text: {e}", exc_info=True)
            raise
    
    def extract_sections(self, text: str) -> dict:
        """Extract different sections from label text"""
        try:
            # TODO: Implement section extraction logic
            sections = {
                "product_info": "",
                "ingredients": "",
                "dosage": "",
                "warnings": "",
                "manufacturer": ""
            }
            
            return sections
            
        except Exception as e:
            logger.error(f"Error extracting sections: {e}", exc_info=True)
            raise
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        return text.lower().split()
    
    def find_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Find keywords in text"""
        found = []
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found.append(keyword)
        
        return found

