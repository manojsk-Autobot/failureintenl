"""Anthropic Claude LLM provider."""
from .base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key
            model: Model name (default: claude-3-5-sonnet-20241022)
            **kwargs: Additional configuration
        """
        super().__init__(api_key, model, **kwargs)
    
    async def generate(self, prompt: str) -> str:
        """
        Generate text using Anthropic API.
        
        Args:
            prompt: Input prompt text
            
        Returns:
            Generated text response
        """
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(api_key=self.api_key)
            response = await client.messages.create(
                model=self.model,
                max_tokens=self.config.get('max_tokens', 2000),
                temperature=self.config.get('temperature', 0.7),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except ImportError:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")
    
    def is_available(self) -> bool:
        """
        Check if Anthropic provider is available.
        
        Returns:
            True if API key is configured and package is installed
        """
        try:
            import anthropic
            return self.api_key is not None and len(self.api_key) > 0
        except ImportError:
            return False
