"""MSSQL database connector implementation."""
import pyodbc
from typing import Dict, Any, Optional
from .base import BaseConnector


class MSSQLConnector(BaseConnector):
    """Microsoft SQL Server connector."""
    
    def connect(self) -> None:
        """Establish connection to MSSQL database."""
        try:
            connection_string = (
                f"DRIVER={{{self.config['driver']}}};"
                f"SERVER={self.config['server']};"
                f"DATABASE={self.config['database']};"
                f"UID={self.config['username']};"
                f"PWD={self.config['password']};"
            )
            
            # Add Driver 18 specific parameters
            if 'trust_certificate' in self.config:
                connection_string += f"TrustServerCertificate={self.config['trust_certificate']};"
            if 'encrypt' in self.config:
                connection_string += f"Encrypt={self.config['encrypt']};"
            
            self.connection = pyodbc.connect(connection_string, timeout=10)
            print(f"Connected to MSSQL: {self.config['server']}/{self.config['database']}")
        except Exception as e:
            print(f"MSSQL connection error: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close MSSQL connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("MSSQL connection closed")
    
    def fetch_last_row(self, table_name: str, order_by: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch the last row from a MSSQL table.
        
        Args:
            table_name: Name of the table
            order_by: Column to order by (defaults to first column if None)
            
        Returns:
            Dictionary with column names as keys and row values
        """
        if not self.connection:
            raise Exception("Not connected to database")
        
        try:
            cursor = self.connection.cursor()
            
            # If no order_by specified, try to get primary key or use first column
            if not order_by:
                # Simple approach: order by first column descending
                query = f"SELECT TOP 1 * FROM {table_name} ORDER BY (SELECT NULL)"
                # Better approach would be to detect timestamp/id column, but keeping it simple
                cursor.execute(f"SELECT TOP 1 * FROM {table_name}")
            else:
                query = f"SELECT TOP 1 * FROM {table_name} ORDER BY {order_by} DESC"
                cursor.execute(query)
            
            row = cursor.fetchone()
            
            if not row:
                return {}
            
            # Get column names
            columns = [column[0] for column in cursor.description]
            
            # Convert row to dictionary
            result = {}
            for idx, column in enumerate(columns):
                value = row[idx]
                # Convert non-serializable types to strings
                if hasattr(value, 'isoformat'):  # datetime objects
                    result[column] = value.isoformat()
                else:
                    result[column] = value
            
            return result
            
        except Exception as e:
            print(f"Error fetching last row: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test if MSSQL connection is working."""
        try:
            if not self.connection:
                self.connect()
            cursor = self.connection.cursor() #type: ignore
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
