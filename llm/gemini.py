"""Gemini LLM provider."""
import os
import google.generativeai as genai
from typing import Dict, Any


class GeminiProvider:
    """Google Gemini AI provider."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            model: Model name (defaults to GEMINI_MODEL env var or gemini-flash-latest)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = model or os.getenv('GEMINI_MODEL', 'gemini-flash-latest')
        
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)
    
    def format_prompt(self, job_data: Dict[str, Any], template: str) -> str:
        """Format prompt template with job failure data."""
        return template.format(
            JobName=job_data.get('JobName', 'N/A'),
            ServerName=job_data.get('ServerName', 'N/A'),
            FailedDateTime=job_data.get('FailedDateTime', 'N/A'),
            FailureMessage=job_data.get('FailureMessage', 'N/A')
        )
    
    async def generate(self, prompt: str) -> str:
        """
        Generate text using Gemini.
        
        Args:
            prompt: Input prompt text
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"✗ Gemini generation error: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        return bool(self.api_key)
