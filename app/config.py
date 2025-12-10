"""Configuration management."""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_db_config(db_type: str) -> Dict[str, Any]:
    """
    Get database configuration for specified type.
    
    Args:
        db_type: Type of database ('mssql', 'mysql', 'mongodb')
        
    Returns:
        Dictionary with connection parameters
    """
    if db_type.lower() == 'mssql':
        return {
            'server': os.getenv('MSSQL_SERVER'),
            'database': os.getenv('MSSQL_DATABASE'),
            'username': os.getenv('MSSQL_USERNAME'),
            'password': os.getenv('MSSQL_PASSWORD'),
            'driver': os.getenv('MSSQL_DRIVER', 'ODBC Driver 18 for SQL Server'),
            'trust_certificate': os.getenv('MSSQL_TRUST_CERT', 'yes'),
            'encrypt': os.getenv('MSSQL_ENCRYPT', 'yes')
        }
    elif db_type.lower() == 'mysql':
        return {
            'host': os.getenv('MYSQL_HOST'),
            'database': os.getenv('MYSQL_DATABASE'),
            'username': os.getenv('MYSQL_USERNAME'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'port': int(os.getenv('MYSQL_PORT', '3306'))
        }
    elif db_type.lower() == 'mongodb':
        return {
            'host': os.getenv('MONGO_HOST'),
            'database': os.getenv('MONGO_DATABASE'),
            'username': os.getenv('MONGO_USERNAME'),
            'password': os.getenv('MONGO_PASSWORD'),
            'port': int(os.getenv('MONGO_PORT', '27017'))
        }
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


def get_email_config() -> Dict[str, str]:
    """
    Get email configuration.
    
    Returns:
        Dictionary with SMTP settings
    """
    return {
        'smtp_server': os.getenv('SMTP_SERVER', 'localhost'),
        'smtp_port': int(os.getenv('SMTP_PORT', '25')), #type: ignore
        'sender_email': os.getenv('SENDER_EMAIL', 'noreply@localhost')
    }
