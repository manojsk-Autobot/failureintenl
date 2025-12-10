"""Google Gemini LLM provider."""
import google.generativeai as genai
from .base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""
    
    def __init__(self, api_key: str, model: str = "gemini-flash-latest", **kwargs):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google API key
            model: Gemini model name (default: gemini-flash-latest)
            **kwargs: Additional configuration
        """
        super().__init__(api_key, model, **kwargs)
        if self.api_key:
            genai.configure(api_key=self.api_key)
    
    async def generate(self, prompt: str) -> str:
        """
        Generate text using Gemini API.
        
        Args:
            prompt: Input prompt text
            
        Returns:
            Generated text response
        """
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        return response.text
    
    def is_available(self) -> bool:
        """
        Check if Gemini provider is available.
        
        Returns:
            True if API key is configured
        """
        return self.api_key is not None and len(self.api_key) > 0
