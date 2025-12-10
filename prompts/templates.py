"""Prompt template management."""
from pathlib import Path
from typing import Dict


class PromptManager:
    """Manager for loading and managing prompt templates."""
    
    def __init__(self, templates_dir: str = None): # type: ignore
        """
        Initialize prompt manager.
        
        Args:
            templates_dir: Directory containing prompt templates
        """
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            self.templates_dir = Path(__file__).parent
    
    def load_template(self, template_name: str) -> str:
        """
        Load a prompt template by name.
        
        Args:
            template_name: Name of template file (without .txt extension)
            
        Returns:
            Template content as string
        """
        template_file = self.templates_dir / f"{template_name}.txt"
        
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_name}")
        
        with open(template_file, 'r') as f:
            return f.read()
    
    def list_templates(self) -> list[str]:
        """
        List all available templates.
        
        Returns:
            List of template names
        """
        return [f.stem for f in self.templates_dir.glob("*.txt")]
    
    def format_template(self, template: str, **kwargs) -> str:
        """
        Format a template with provided variables.
        
        Args:
            template: Template string
            **kwargs: Variables to substitute
            
        Returns:
            Formatted template
        """
        return template.format(**kwargs)


# Predefined templates
SQL_FAILURE_ANALYSIS = "sql_failure_analysis"

# Template registry
TEMPLATES = {
    "sql_failure": SQL_FAILURE_ANALYSIS,
}
