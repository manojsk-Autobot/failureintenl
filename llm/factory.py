"""Factory for creating LLM providers."""
import os
from typing import Optional
from .base import BaseLLMProvider
from .gemini import GeminiProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .ollama import OllamaProvider


class LLMFactory:
    """Factory for creating LLM providers based on configuration."""
    
    @staticmethod
    def create_provider(
        provider_type: str = None,
        api_key: str = None,
        model: str = None,
        **kwargs
    ) -> BaseLLMProvider:
        """
        Create an LLM provider instance.
        
        Args:
            provider_type: Type of provider ('gemini', 'openai', 'anthropic', 'ollama')
                          If None, reads from LLM_PROVIDER env var (default: 'gemini')
            api_key: API key for the provider (if None, reads from provider-specific env var)
            model: Model name (if None, uses provider default or reads from LLM_MODEL env var)
            **kwargs: Additional provider-specific configuration
            
        Returns:
            Configured LLM provider instance
            
        Raises:
            ValueError: If provider type is unsupported or required config is missing
        """
        # Determine provider type
        if provider_type is None:
            provider_type = os.getenv('LLM_PROVIDER', 'gemini').lower()
        else:
            provider_type = provider_type.lower()
        
        # Get model from env if not provided
        if model is None:
            model = os.getenv('LLM_MODEL')
        
        # Create provider based on type
        if provider_type == 'gemini':
            api_key = api_key or os.getenv('GEMINI_API_KEY')
            model = model or os.getenv('GEMINI_MODEL', 'gemini-flash-latest')
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
            return GeminiProvider(api_key=api_key, model=model, **kwargs)
        
        elif provider_type == 'openai':
            api_key = api_key or os.getenv('OPENAI_API_KEY')
            model = model or 'gpt-4o-mini'
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            return OpenAIProvider(api_key=api_key, model=model, **kwargs)
        
        elif provider_type == 'anthropic':
            api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
            model = model or 'claude-3-5-sonnet-20241022'
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            return AnthropicProvider(api_key=api_key, model=model, **kwargs)
        
        elif provider_type == 'ollama':
            model = model or os.getenv('OLLAMA_MODEL', 'llama3.2')
            base_url = kwargs.get('base_url', os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'))
            return OllamaProvider(model=model, base_url=base_url, **kwargs)
        
        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider_type}. "
                f"Supported providers: gemini, openai, anthropic, ollama"
            )
    
    @staticmethod
    def get_available_providers() -> list[str]:
        """
        Get list of available LLM providers.
        
        Returns:
            List of provider names that are properly configured
        """
        available = []
        
        # Check Gemini
        if os.getenv('GEMINI_API_KEY'):
            available.append('gemini')
        
        # Check OpenAI
        if os.getenv('OPENAI_API_KEY'):
            try:
                import openai
                available.append('openai')
            except ImportError:
                pass
        
        # Check Anthropic
        if os.getenv('ANTHROPIC_API_KEY'):
            try:
                import anthropic
                available.append('anthropic')
            except ImportError:
                pass
        
        # Check Ollama
        try:
            provider = OllamaProvider()
            if provider.is_available():
                available.append('ollama')
        except Exception:
            pass
        
        return available
