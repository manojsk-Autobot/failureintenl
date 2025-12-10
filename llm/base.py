"""Base class for LLM providers."""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        """
        Initialize LLM provider.
        
        Args:
            api_key: API key for the provider (if needed)
            model: Model name to use
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.model = model
        self.config = kwargs
    
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """
        Generate text from prompt.
        
        Args:
            prompt: Input prompt text
            
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if provider is available and properly configured.
        
        Returns:
            True if provider is ready to use
        """
        pass
    
    def format_prompt(self, log_data: Dict[str, Any], template: str) -> str:
        """
        Format prompt template with log data.
        
        Args:
            log_data: Dictionary containing log entry data
            template: Prompt template string
            
        Returns:
            Formatted prompt string
        """
        return template.format(
            JobName=log_data.get('JobName', 'N/A'),
            ServerName=log_data.get('ServerName', 'N/A'),
            FailedDateTime=log_data.get('FailedDateTime', 'N/A'),
            FailureMessage=log_data.get('FailureMessage', 'N/A'),
            log_data="\n".join([f"{key}: {value}" for key, value in log_data.items()])
        )
