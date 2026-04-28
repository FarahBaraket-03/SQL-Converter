"""Cassandra CQL converter."""
from typing import Dict, Any, List


class CassandraConverter:
    """Convert SQL schema to Cassandra CQL."""
    
    def __init__(self, schema_info: Dict[str, Any]):
        self.schema_info = schema_info
        self.tables = schema_info.get('tables', [])
        self.relationships = schema_info.get('relationships', [])
    
    def convert(self) -> Dict[str, Any]:
        """Convert SQL schema to Cassandra CQL."""
        # Cassandra requires query-first design
        # We'll create denormalized tables optimized for common access patterns
        
        cql_tables = []
        
        # Create keyspace
        keyspace_name = "app_keyspace"
        
        # Convert each table with denormalization
        for table in self.tables:
            # Create primary table
            primary_table = self._convert_table(table)
            cql_tables.append(primary_table)
            
            # Create query-optimized tables
            query_tables = self._create_query_tables(table)
            cql_tables.extend(query_tables)
        
        # Generate CQL output
        cql_output = self._generate_cql_output(keyspace_name, cql_tables)
        
        return {
            'schema': cql_output,
            'tables': cql_tables,
            'keyspace': keyspace_name
        }
    
    def _convert_table(self, table: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a SQL table to Cassandra table with proper partition/clustering keys.
        
        Cassandra Best Practices:
        1. Partition key: Determines data distribution (high cardinality)
        2. Clustering key: Determines sort order within partition
        3. Avoid hot partitions: Choose keys with even distribution
        4. Query-first design: Partition key should match WHERE clause
        """
        table_name = table['name']
        columns = []
        
        for column in table['columns']:
            cql_type = self._map_sql_type_to_cql(column['type'])
            columns.append({
                'name': column['name'],
                'type': cql_type,
                'is_primary_key': column['is_primary_key']
            })
        
        # Smart partition key selection
        partition_keys = self._select_partition_keys(table)
        clustering_keys = self._select_clustering_keys(table, partition_keys)
        
        return {
            'name': table_name,
            'columns': columns,
            'partition_keys': partition_keys,
            'clustering_keys': clustering_keys,
            'is_query_table': False
        }
    
    def _select_partition_keys(self, table: Dict[str, Any]) -> List[str]:
        """Select optimal partition key(s) for Cassandra.
        
        Priority:
        1. Foreign keys (for query patterns)
        2. High-cardinality columns (user_id, customer_id)
        3. Primary key (fallback)
        """
        # Check for foreign keys first (common query pattern)
        if table['foreign_keys']:
            fk = table['foreign_keys'][0]
            if fk['from_columns']:
                return fk['from_columns'][:1]  # Use first FK column
        
        # Use primary key
        if table['primary_keys']:
            return table['primary_keys'][:1]
        
        # Fallback to first column
        if table['columns']:
            return [table['columns'][0]['name']]
        
        return ['id']
    
    def _select_clustering_keys(self, table: Dict[str, Any], partition_keys: List[str]) -> List[str]:
        """Select clustering keys for sort order within partition.
        
        Common patterns:
        - Timestamp columns (for time-series data)
        - Remaining primary key columns
        - Frequently sorted columns
        """
        clustering = []
        
        # Add remaining primary keys as clustering keys
        for pk in table['primary_keys']:
            if pk not in partition_keys:
                clustering.append(pk)
        
        # Add timestamp columns for time-series ordering
        for column in table['columns']:
            col_name = column['name'].lower()
            col_type = column['type'].upper()
            if ('timestamp' in col_type or 'datetime' in col_type or 
                'created' in col_name or 'updated' in col_name or 'date' in col_name):
                if column['name'] not in partition_keys and column['name'] not in clustering:
                    clustering.append(column['name'])
                    break  # Only add one timestamp
        
        return clustering
    
    def _create_query_tables(self, table: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create additional tables optimized for specific query patterns."""
        query_tables = []
        
        # Example: Create a table for querying by foreign key
        for fk in table['foreign_keys']:
            query_table_name = f"{table['name']}_by_{fk['to_table']}"
            
            # FIX: Deep copy and remap SQL types to CQL
            columns = []
            for col in table['columns']:
                cql_type = self._map_sql_type_to_cql(col['type'])
                columns.append({
                    'name': col['name'],
                    'type': cql_type,
                    'is_primary_key': col['is_primary_key']
                })
            
            query_tables.append({
                'name': query_table_name,
                'columns': columns,
                'partition_keys': fk['from_columns'],
                'clustering_keys': table['primary_keys'] if table['primary_keys'] else [],
                'is_query_table': True,
                'query_pattern': f"Query {table['name']} by {fk['to_table']}"
            })
        
        return query_tables
    
    def _generate_cql_output(self, keyspace: str, tables: List[Dict[str, Any]]) -> str:
        """Generate CQL statements with correct syntax."""
        output = []
        
        # Create keyspace
        output.append(f"-- Cassandra Keyspace")
        output.append(f"CREATE KEYSPACE IF NOT EXISTS {keyspace}")
        output.append("WITH replication = {")
        output.append("  'class': 'NetworkTopologyStrategy',")
        output.append("  'datacenter1': 3")
        output.append("};")
        output.append("")
        output.append(f"USE {keyspace};")
        output.append("")
        
        # Create tables
        for table in tables:
            if table.get('is_query_table'):
                output.append(f"-- Query Table: {table.get('query_pattern', '')}")
            else:
                output.append(f"-- Primary Table: {table['name']}")
            
            output.append(f"CREATE TABLE IF NOT EXISTS {table['name']} (")
            
            # Columns
            for i, column in enumerate(table['columns']):
                comma = ","
                output.append(f"  {column['name']} {column['type']}{comma}")
            
            # Primary key - FIX: Single partition key without double parentheses
            partition_key = ", ".join(table['partition_keys'])
            if len(table['partition_keys']) > 1:
                # Multiple partition keys need double parentheses
                partition_clause = f"({partition_key})"
            else:
                # Single partition key - no double parentheses
                partition_clause = partition_key
            
            if table['clustering_keys']:
                clustering_key = ", ".join(table['clustering_keys'])
                output.append(f"  PRIMARY KEY (({partition_clause}), {clustering_key})")
            else:
                output.append(f"  PRIMARY KEY ({partition_clause})")
            
            # FIX: Close parenthesis first, then add WITH clause
            output.append(")")
            
            # Clustering order - FIX: Add BEFORE semicolon
            if table['clustering_keys']:
                clustering_order = ", ".join([f"{key} DESC" for key in table['clustering_keys']])
                output.append(f"WITH CLUSTERING ORDER BY ({clustering_order});")
            else:
                output.append(";")
            
            output.append("")
        
        return "\n".join(output)
    
    def _map_sql_type_to_cql(self, sql_type: str) -> str:
        """Map SQL data types to CQL types."""
        sql_type = sql_type.upper()
        
        if 'INT' in sql_type:
            if 'BIGINT' in sql_type:
                return 'BIGINT'
            elif 'SMALLINT' in sql_type:
                return 'SMALLINT'
            elif 'TINYINT' in sql_type:
                return 'TINYINT'
            else:
                return 'INT'
        elif 'DECIMAL' in sql_type or 'NUMERIC' in sql_type:
            return 'DECIMAL'
        elif 'FLOAT' in sql_type:
            return 'FLOAT'
        elif 'DOUBLE' in sql_type:
            return 'DOUBLE'
        elif 'BOOL' in sql_type:
            return 'BOOLEAN'
        elif 'DATE' in sql_type:
            return 'DATE'
        elif 'TIMESTAMP' in sql_type or 'DATETIME' in sql_type:
            return 'TIMESTAMP'
        elif 'TIME' in sql_type:
            return 'TIME'
        elif 'TEXT' in sql_type:
            return 'TEXT'
        elif 'VARCHAR' in sql_type or 'CHAR' in sql_type:
            return 'TEXT'
        elif 'BLOB' in sql_type or 'BINARY' in sql_type:
            return 'BLOB'
        elif 'UUID' in sql_type:
            return 'UUID'
        else:
            return 'TEXT'
