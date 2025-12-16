"""Email formatter - generates HTML from analysis."""
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class EmailFormatter:
    """Service for formatting email content with HTML templates."""
    
    def __init__(self):
        """Initialize email formatter and load template."""
        # Load email template
        template_path = Path(__file__).parent.parent / "prompts" / "email_template.html"
        with open(template_path, 'r', encoding='utf-8') as f:
            self.email_template = f.read()
    
    def format_with_analysis(
        self,
        job_data: Dict[str, Any],
        analysis: str,
        sender_email: str
    ) -> str:
        """
        Format HTML email with job data and LLM analysis.
        
        Args:
            job_data: Dictionary with job failure data
            analysis: LLM generated analysis text
            sender_email: Sender email address
            
        Returns:
            Formatted HTML string
        """
        # Extract structured information
        error_details = self._extract_error_details(job_data, analysis)
        quick_summary = self._extract_summary(analysis)
        solution_html = self._format_solution(analysis)
        urgency_info = self._extract_urgency(analysis)
        
        # Replace template placeholders
        html = self.email_template
        replacements = {
            '{{job_name}}': error_details['job_name'],
            '{{instance_name}}': error_details['instance'],
            '{{failure_time}}': error_details['failure_time'],
            '{{error_code}}': error_details['error_code'],
            '{{error_summary}}': quick_summary,
            '{{solution_content}}': solution_html,
            '{{urgency_level}}': urgency_info['level'],
            '{{urgency_color}}': urgency_info['color'],
            '{{urgency_border}}': urgency_info['border'],
            '{{urgency_message}}': urgency_info['message'],
            '{{contact_email}}': 'dba-team@sky.uk',
            '{{timestamp}}': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '{{sender_email}}': sender_email
        }
        
        for placeholder, value in replacements.items():
            html = html.replace(placeholder, str(value))
        
        return html
    
    def format_email(self, analysis: str, job_data: Dict[str, Any], sender_email: str = None) -> tuple:
        """
        Format email with analysis - returns both HTML and plain text.
        
        Args:
            analysis: LLM generated analysis text
            job_data: Dictionary with job failure data
            sender_email: Sender email address (optional)
            
        Returns:
            Tuple of (html_body, plain_body)
        """
        sender = sender_email or 'manojkumar.selvakumar@sky.uk'
        html_body = self.format_with_analysis(job_data, analysis, sender)
        plain_body = self.format_plain(job_data)
        return html_body, plain_body
    
    def format_plain(self, job_data: Dict[str, Any]) -> str:
        """
        Format plain text email.
        
        Args:
            job_data: Dictionary with job failure data
            
        Returns:
            Plain text string
        """
        body = "MSSQL Job Failure Alert\n\n"
        for key, value in job_data.items():
            body += f"{key}: {value}\n"
        return body
    
    def _extract_error_details(self, job_data: Dict[str, Any], analysis: str) -> Dict[str, str]:
        """Extract error details from job data and analysis."""
        job_match = re.search(r'Job Name:\s*(.+)', analysis)
        instance_match = re.search(r'Instance:\s*(.+)', analysis)
        failure_match = re.search(r'Failure Time:\s*(.+)', analysis)
        error_code_match = re.search(r'Error Code:\s*(.+)', analysis)
        
        return {
            'job_name': job_match.group(1).strip() if job_match else job_data.get('JobName', 'N/A'),
            'instance': instance_match.group(1).strip() if instance_match else job_data.get('ServerName', 'N/A'),
            'failure_time': failure_match.group(1).strip() if failure_match else job_data.get('FailedDateTime', 'N/A'),
            'error_code': error_code_match.group(1).strip() if error_code_match else 'Unknown'
        }
    
    def _extract_summary(self, analysis: str) -> str:
        """Extract summary from analysis."""
        summary_match = re.search(r'SUMMARY\n(.+?)(?:\n\n|\nURGENCY|$)', analysis, re.DOTALL)
        return summary_match.group(1).strip() if summary_match else 'An error occurred during job execution.'
    
    def _extract_urgency(self, analysis: str) -> Dict[str, str]:
        """Extract urgency information."""
        urgency_map = {
            'HIGH': {'color': '#ffebee', 'border': '#f44336', 'level': 'HIGH'},
            'MEDIUM': {'color': '#fff3e0', 'border': '#ff9800', 'level': 'MEDIUM'},
            'LOW': {'color': '#e8f5e9', 'border': '#4caf50', 'level': 'LOW'}
        }
        
        urgency_match = re.search(r'URGENCY:\s*(HIGH|MEDIUM|LOW)', analysis, re.IGNORECASE)
        level = urgency_match.group(1).upper() if urgency_match else 'MEDIUM'
        
        urgency_msg_match = re.search(r'URGENCY:.*?\n(.+?)(?:\n\n|\nSOLUTION|$)', analysis, re.DOTALL)
        message = urgency_msg_match.group(1).strip() if urgency_msg_match else 'Please review and address this issue.'
        
        result = urgency_map.get(level, urgency_map['MEDIUM']).copy()
        result['message'] = message
        return result
    
    def _format_solution(self, analysis: str) -> str:
        """Format solution steps with code blocks."""
        solution_match = re.search(r'SOLUTION STEPS\n\n(.*?)(?:\nPREVENTIVE MEASURES|$)', analysis, re.DOTALL)
        
        if not solution_match:
            return f'<div style="padding: 15px;">{self._escape_html(analysis)}</div>'
        
        solution_text = solution_match.group(1).strip()
        html_parts = []
        lines = solution_text.split('\n')
        
        current_step = []
        code_buffer = []
        in_code = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Detect step headers
            if re.match(r'^Step \d+:', line_stripped):
                # Flush previous content
                if current_step:
                    html_parts.append(self._format_step(''.join(current_step)))
                    current_step = []
                if code_buffer:
                    html_parts.append(self._format_code('\n'.join(code_buffer)))
                    code_buffer = []
                    in_code = False
                
                current_step.append(line_stripped)
            
            # Detect SQL code block markers
            elif line_stripped.startswith('```sql') or line_stripped == '```':
                if line_stripped.startswith('```sql'):
                    # Start of SQL block
                    if current_step:
                        html_parts.append(self._format_step(''.join(current_step)))
                        current_step = []
                    in_code = True
                elif line_stripped == '```' and in_code:
                    # End of SQL block
                    if code_buffer:
                        html_parts.append(self._format_code('\n'.join(code_buffer)))
                        code_buffer = []
                    in_code = False
            
            # Detect SQL/code lines (legacy format)
            elif line_stripped.startswith('--') or any(kw in line.upper() for kw in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'MERGE', 'CREATE', 'WITH', 'USE', 'EXEC']):
                if current_step:
                    html_parts.append(self._format_step(''.join(current_step)))
                    current_step = []
                in_code = True
                code_buffer.append(line)
            
            # Continue code block
            elif in_code:
                if line_stripped == '':
                    if code_buffer:
                        html_parts.append(self._format_code('\n'.join(code_buffer)))
                        code_buffer = []
                        in_code = False
                else:
                    code_buffer.append(line)
            
            # Regular text
            elif line_stripped:
                current_step.append('<br>' + line_stripped if current_step else line_stripped)
        
        # Flush remaining
        if current_step:
            html_parts.append(self._format_step(''.join(current_step)))
        if code_buffer:
            html_parts.append(self._format_code('\n'.join(code_buffer)))
        
        return ''.join(html_parts)
    
    def _format_step(self, text: str) -> str:
        """Format a step."""
        return f'<div class="step-item">{self._escape_html(text)}</div>'
    
    def _format_code(self, code: str) -> str:
        """Format code block."""
        return f'<div class="sql-query">{self._escape_html(code)}</div>'
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))
