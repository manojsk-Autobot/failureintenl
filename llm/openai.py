"""OpenAI LLM provider."""
from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", **kwargs):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4o-mini)
            **kwargs: Additional configuration
        """
        super().__init__(api_key, model, **kwargs)
    
    async def generate(self, prompt: str) -> str:
        """
        Generate text using OpenAI API.
        
        Args:
            prompt: Input prompt text
            
        Returns:
            Generated text response
        """
        try:
            import openai
            
            client = openai.AsyncOpenAI(api_key=self.api_key)
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('temperature', 0.7),
                max_tokens=self.config.get('max_tokens', 2000)
            )
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")
    
    def is_available(self) -> bool:
        """
        Check if OpenAI provider is available.
        
        Returns:
            True if API key is configured and package is installed
        """
        try:
            import openai
            return self.api_key is not None and len(self.api_key) > 0
        except ImportError:
            return False
