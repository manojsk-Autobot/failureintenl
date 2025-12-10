"""Ollama local LLM provider."""
import httpx
from .base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, api_key: str = None, model: str = "llama3.2", **kwargs):
        """
        Initialize Ollama provider.
        
        Args:
            api_key: Not used for Ollama (kept for interface compatibility)
            model: Model name (default: llama3.2)
            **kwargs: Additional configuration (base_url, timeout)
        """
        super().__init__(api_key, model, **kwargs)
        self.base_url = kwargs.get('base_url', 'http://localhost:11434')
        self.timeout = kwargs.get('timeout', 60.0)
    
    async def generate(self, prompt: str) -> str:
        """
        Generate text using Ollama API.
        
        Args:
            prompt: Input prompt text
            
        Returns:
            Generated text response
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config.get('temperature', 0.7),
                        "num_predict": self.config.get('max_tokens', 2000)
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
    
    def is_available(self) -> bool:
        """
        Check if Ollama provider is available.
        
        Returns:
            True if Ollama server is reachable
        """
        try:
            import httpx
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False
