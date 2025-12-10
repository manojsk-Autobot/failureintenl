"""Analysis service for orchestrating LLM analysis."""
from pathlib import Path
from typing import Dict, Any
from llm.factory import LLMFactory


class AnalysisService:
    """Service for analyzing log data using LLM."""
    
    def __init__(self, prompt_template_path: str = None):
        """
        Initialize analysis service.
        
        Args:
            prompt_template_path: Path to prompt template file
        """
        self.prompt_template_path = prompt_template_path
        self._load_prompt_template()
    
    def _load_prompt_template(self):
        """Load prompt template from file."""
        if self.prompt_template_path:
            prompt_file = Path(self.prompt_template_path)
        else:
            # Default to prompts/sql_failure_analysis.txt
            prompt_file = Path(__file__).parent.parent / "prompts" / "sql_failure_analysis.txt"
        
        try:
            with open(prompt_file, 'r') as f:
                self.prompt_template = f.read()
        except FileNotFoundError:
            # Fallback template
            self.prompt_template = """Analyze the following failed SQL Server Agent job and provide:
1. Root cause analysis
2. Recommended solution
3. Prevention steps

Job Details:
{log_data}

Please provide a clear, structured response."""
    
    async def analyze(self, log_data: Dict[str, Any], provider_type: str = None) -> str:
        """
        Analyze log data using LLM.
        
        Args:
            log_data: Dictionary containing the log entry from database
            provider_type: Optional LLM provider type (gemini, openai, anthropic, ollama)
            
        Returns:
            Analysis text from LLM
        """
        # Create LLM provider
        llm_provider = LLMFactory.create_provider(provider_type=provider_type)
        
        # Format prompt with log data
        prompt = llm_provider.format_prompt(log_data, self.prompt_template)
        
        # Generate analysis
        response = await llm_provider.generate(prompt)
        return response
    
    def is_available(self, provider_type: str = None) -> bool:
        """
        Check if analysis service is available.
        
        Args:
            provider_type: Optional provider type to check
            
        Returns:
            True if LLM provider is available
        """
        try:
            provider = LLMFactory.create_provider(provider_type=provider_type)
            return provider.is_available()
        except Exception:
            return False
