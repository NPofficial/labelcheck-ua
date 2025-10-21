"""Claude AI service for text generation and analysis"""

import anthropic
from typing import Optional, List, Dict
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for interacting with Claude API"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.claude_api_key)
        self.model = "claude-3-5-sonnet-20241022"
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """
        Generate text using Claude
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            max_tokens: Maximum tokens to generate
            temperature: Temperature for randomness
            
        Returns:
            Generated text
        """
        try:
            logger.info("Generating text with Claude")
            
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt if system_prompt else "",
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error generating text with Claude: {e}", exc_info=True)
            raise
    
    async def analyze_label(self, label_text: str) -> Dict:
        """
        Analyze pharmaceutical label text
        
        Args:
            label_text: Label text to analyze
            
        Returns:
            Analysis results
        """
        try:
            logger.info("Analyzing label with Claude")
            
            # TODO: Implement label analysis logic with structured prompts
            
            return {
                "analysis": "Label analysis placeholder",
                "issues_found": []
            }
            
        except Exception as e:
            logger.error(f"Error analyzing label: {e}", exc_info=True)
            raise
    
    async def validate_compliance(
        self,
        label_text: str,
        regulations: List[Dict]
    ) -> Dict:
        """
        Validate label compliance with regulations
        
        Args:
            label_text: Label text to validate
            regulations: List of regulatory requirements
            
        Returns:
            Validation results
        """
        try:
            logger.info("Validating compliance with Claude")
            
            # TODO: Implement compliance validation
            
            return {
                "is_compliant": True,
                "violations": []
            }
            
        except Exception as e:
            logger.error(f"Error validating compliance: {e}", exc_info=True)
            raise

