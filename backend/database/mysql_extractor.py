"""MySQL schema extraction utilities."""
import mysql.connector
from typing import Dict, Any, List, Optional
from models import MySQLConnectionRequest


class MySQLExtractor:
    """Extract schema information from MySQL databases."""
    
    def __init__(self, connection_params: MySQLConnectionRequest):
        self.params = connection_params
        self.connection = None
    
    def connect(self) -> bool:
        """Establish connection to MySQL server."""
        try:
            self.connection = mysql.connector.connect(
                host=self.params.host,
                port=self.params.port,
                user=self.params.user,
                password=self.params.password,
                database=self.params.database
            )
            return True
        except Exception as e:
            print(f"MySQL connection failed: {e}")
            return False
    
    def extract_schema(self) -> Dict[str, Any]:
        """Extract complete schema as SQL DDL statements."""
        if not self.connection:
            if not self.connect():
                raise Exception("Failed to connect to MySQL")
        
        cursor = self.connection.cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        # Extract CREATE TABLE statements
        ddl_statements = []
        
        for table in tables:
            cursor.execute(f"SHOW CREATE TABLE `{table}`")
            result = cursor.fetchone()
            if result:
                create_statement = result[1]
                ddl_statements.append(create_statement)
        
        cursor.close()
        
        sql = ";\n\n".join(ddl_statements) + ";"
        
        return {
            'sql': sql,
            'tables': tables,
            'database': self.params.database
        }
    
    def list_databases(self) -> List[str]:
        """List all databases on the MySQL server."""
        if not self.connection:
            if not self.connect():
                raise Exception("Failed to connect to MySQL")
        
        cursor = self.connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        cursor.close()
        
        # Filter out system databases
        system_dbs = ['information_schema', 'mysql', 'performance_schema', 'sys']
        return [db for db in databases if db not in system_dbs]
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific table."""
        if not self.connection:
            if not self.connect():
                raise Exception("Failed to connect to MySQL")
        
        cursor = self.connection.cursor(dictionary=True)
        
        # Get columns
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns = cursor.fetchall()
        
        # Get indexes
        cursor.execute(f"SHOW INDEX FROM `{table_name}`")
        indexes = cursor.fetchall()
        
        # Get foreign keys
        cursor.execute(f"""
            SELECT 
                CONSTRAINT_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s
            AND TABLE_NAME = %s
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """, (self.params.database, table_name))
        foreign_keys = cursor.fetchall()
        
        cursor.close()
        
        return {
            'table_name': table_name,
            'columns': columns,
            'indexes': indexes,
            'foreign_keys': foreign_keys
        }
    
    def close(self):
        """Close the MySQL connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
