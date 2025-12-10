"""Base connector interface for all database types."""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BaseConnector(ABC):
    """Abstract base class for database connectors."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize connector with config.
        
        Args:
            config: Dictionary containing connection parameters
        """
        self.config = config
        self.connection = None
    
    @abstractmethod
    def connect(self) -> None:
        """Establish database connection."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    def fetch_last_row(self, table_name: str, order_by: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch the last row from a table.
        
        Args:
            table_name: Name of the table
            order_by: Column to order by (if None, uses default ordering)
            
        Returns:
            Dictionary containing column names and values
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if connection is working."""
        pass
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
