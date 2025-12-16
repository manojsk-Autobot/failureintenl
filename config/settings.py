"""Configuration management."""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


class Settings:
    """Application settings."""
    
    # Database Configuration
    MSSQL_SERVER = os.getenv('MSSQL_SERVER', 'localhost')
    MSSQL_DATABASE = os.getenv('MSSQL_DATABASE', 'failed_jobs')
    MSSQL_USERNAME = os.getenv('MSSQL_USERNAME', 'sa')
    MSSQL_PASSWORD = os.getenv('MSSQL_PASSWORD', '')
    MSSQL_DRIVER = os.getenv('MSSQL_DRIVER', 'ODBC Driver 18 for SQL Server')
    MSSQL_TRUST_CERT = os.getenv('MSSQL_TRUST_CERT', 'yes')
    MSSQL_ENCRYPT = os.getenv('MSSQL_ENCRYPT', 'yes')
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'bridgeheads.bskyb.com').strip("'\"")
    SMTP_PORT = int(os.getenv('SMTP_PORT', 25))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'manojkumar.selvakumar@sky.uk').strip("'\"")
    
    # LLM Configuration
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-flash-latest')
    
    @classmethod
    def get_db_config(cls) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            'server': cls.MSSQL_SERVER,
            'database': cls.MSSQL_DATABASE,
            'username': cls.MSSQL_USERNAME,
            'password': cls.MSSQL_PASSWORD,
            'driver': cls.MSSQL_DRIVER,
            'trust_certificate': cls.MSSQL_TRUST_CERT,
            'encrypt': cls.MSSQL_ENCRYPT
        }
    
    @classmethod
    def get_email_config(cls) -> Dict[str, Any]:
        """Get email configuration."""
        return {
            'smtp_server': cls.SMTP_SERVER,
            'smtp_port': cls.SMTP_PORT,
            'sender_email': cls.SENDER_EMAIL
        }


# Create singleton instance
settings = Settings()
