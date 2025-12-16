"""Job failure analyzer - main feature module."""
import os
from pathlib import Path
from typing import Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm.gemini import GeminiProvider


class FailureAnalyzer:
    """Analyzes MSSQL job failures using LLM."""
    
    def __init__(self):
        """Initialize failure analyzer."""
        self.llm_provider = GeminiProvider()
        self._load_prompt_template()
    
    def _load_prompt_template(self):
        """Load LLM prompt template."""
        prompt_file = Path(__file__).parent.parent / "prompts" / "llm_analysis.txt"
        try:
            with open(prompt_file, 'r') as f:
                self.prompt_template = f.read()
        except FileNotFoundError:
            self.prompt_template = """
Analyze this SQL Server job failure:
Job: {JobName}
Server: {ServerName}
Time: {FailedDateTime}
Error: {FailureMessage}

Provide analysis with solution steps.
"""
    
    async def analyze(self, job_data: Dict[str, Any]) -> str:
        """
        Analyze job failure data using LLM.
        
        Args:
            job_data: Dictionary with job failure information
            
        Returns:
            LLM analysis text with structured solution
        """
        # Format prompt with job data
        prompt = self.llm_provider.format_prompt(job_data, self.prompt_template)
        
        # Generate analysis
        print("🤖 Analyzing job failure with LLM...")
        analysis = await self.llm_provider.generate(prompt)
        print(f"✓ Analysis completed ({len(analysis)} characters)")
        
        return analysis
    
    def is_available(self) -> bool:
        """Check if analyzer is ready to use."""
        return self.llm_provider.is_available()
