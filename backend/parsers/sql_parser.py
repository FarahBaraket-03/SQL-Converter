"""SQL parsing utilities using sqlglot."""
import sqlglot
from sqlglot import exp
from typing import List, Dict, Any, Optional
import re


class SQLParser:
    """Parse SQL DDL statements and extract schema information."""
    
    def __init__(self, sql: str):
        self.sql = sql
        self.tables: List[Dict[str, Any]] = []
        self.relationships: List[Dict[str, Any]] = []
        
    def parse(self) -> Dict[str, Any]:
        """Parse SQL and extract schema information."""
        try:
            # Parse SQL statements
            statements = sqlglot.parse(self.sql, read='mysql')
            
            for statement in statements:
                if isinstance(statement, exp.Create) and statement.kind == 'TABLE':
                    self._parse_table(statement)
            
            return {
                'tables': self.tables,
                'relationships': self.relationships,
                'table_count': len(self.tables),
                'relationship_count': len(self.relationships)
            }
        except Exception as e:
            # Fallback to regex-based parsing
            return self._fallback_parse()
    
    def _parse_table(self, statement: exp.Create):
        """Extract table information from CREATE TABLE statement."""
        table_name = statement.this.name
        columns = []
        primary_keys = []
        foreign_keys = []
        indexes = []
        
        # Extract columns
        if statement.this.expressions:
            for expr in statement.this.expressions:
                if isinstance(expr, exp.ColumnDef):
                    col_info = self._parse_column(expr)
                    columns.append(col_info)
                    
                    # Check for primary key
                    if col_info.get('is_primary_key'):
                        primary_keys.append(col_info['name'])
                
                # Extract constraints
                elif isinstance(expr, exp.PrimaryKey):
                    for col in expr.expressions:
                        primary_keys.append(col.name)
                
                elif isinstance(expr, exp.ForeignKey):
                    fk_info = self._parse_foreign_key(table_name, expr)
                    foreign_keys.append(fk_info)
                    self.relationships.append(fk_info)
        
        self.tables.append({
            'name': table_name,
            'columns': columns,
            'primary_keys': primary_keys,
            'foreign_keys': foreign_keys,
            'indexes': indexes
        })
    
    def _parse_column(self, column_def: exp.ColumnDef) -> Dict[str, Any]:
        """Extract column information."""
        col_name = column_def.this.name
        col_type = str(column_def.kind) if column_def.kind else 'VARCHAR'
        
        constraints = []
        is_primary_key = False
        is_unique = False
        is_nullable = True
        default_value = None
        
        # Check constraints
        if column_def.constraints:
            for constraint in column_def.constraints:
                if isinstance(constraint, exp.PrimaryKeyColumnConstraint):
                    is_primary_key = True
                    is_nullable = False
                elif isinstance(constraint, exp.UniqueColumnConstraint):
                    is_unique = True
                elif isinstance(constraint, exp.NotNullColumnConstraint):
                    is_nullable = False
                elif isinstance(constraint, exp.DefaultColumnConstraint):
                    default_value = str(constraint.this)
        
        return {
            'name': col_name,
            'type': col_type,
            'is_primary_key': is_primary_key,
            'is_unique': is_unique,
            'is_nullable': is_nullable,
            'default_value': default_value
        }
    
    def _parse_foreign_key(self, table_name: str, fk_expr: exp.ForeignKey) -> Dict[str, Any]:
        """Extract foreign key relationship."""
        columns = [col.name for col in fk_expr.expressions]
        reference = fk_expr.reference
        
        ref_table = reference.this.name if reference and reference.this else None
        ref_columns = [col.name for col in reference.expressions] if reference and reference.expressions else []
        
        return {
            'from_table': table_name,
            'from_columns': columns,
            'to_table': ref_table,
            'to_columns': ref_columns,
            'type': '1:N'  # Default assumption
        }
    
    def _fallback_parse(self) -> Dict[str, Any]:
        """Fallback regex-based parsing when sqlglot fails."""
        tables = []
        relationships = []
        
        # Extract CREATE TABLE statements
        create_table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s*\((.*?)\);'
        matches = re.finditer(create_table_pattern, self.sql, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            table_name = match.group(1)
            table_body = match.group(2)
            
            columns = self._extract_columns_regex(table_body)
            primary_keys = self._extract_primary_keys_regex(table_body)
            foreign_keys = self._extract_foreign_keys_regex(table_name, table_body)
            
            tables.append({
                'name': table_name,
                'columns': columns,
                'primary_keys': primary_keys,
                'foreign_keys': foreign_keys,
                'indexes': []
            })
            
            relationships.extend(foreign_keys)
        
        return {
            'tables': tables,
            'relationships': relationships,
            'table_count': len(tables),
            'relationship_count': len(relationships)
        }
    
    def _extract_columns_regex(self, table_body: str) -> List[Dict[str, Any]]:
        """Extract columns using regex."""
        columns = []
        lines = table_body.split(',')
        
        for line in lines:
            line = line.strip()
            if line.upper().startswith(('PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'INDEX', 'KEY', 'CONSTRAINT')):
                continue
            
            # Match column definition
            col_match = re.match(r'`?(\w+)`?\s+(\w+(?:\([^)]+\))?)', line, re.IGNORECASE)
            if col_match:
                col_name = col_match.group(1)
                col_type = col_match.group(2)
                
                is_primary_key = 'PRIMARY KEY' in line.upper()
                is_unique = 'UNIQUE' in line.upper()
                is_nullable = 'NOT NULL' not in line.upper()
                
                columns.append({
                    'name': col_name,
                    'type': col_type,
                    'is_primary_key': is_primary_key,
                    'is_unique': is_unique,
                    'is_nullable': is_nullable,
                    'default_value': None
                })
        
        return columns
    
    def _extract_primary_keys_regex(self, table_body: str) -> List[str]:
        """Extract primary keys using regex."""
        pk_match = re.search(r'PRIMARY\s+KEY\s*\(([^)]+)\)', table_body, re.IGNORECASE)
        if pk_match:
            keys = pk_match.group(1)
            return [k.strip().strip('`') for k in keys.split(',')]
        return []
    
    def _extract_foreign_keys_regex(self, table_name: str, table_body: str) -> List[Dict[str, Any]]:
        """Extract foreign keys using regex."""
        foreign_keys = []
        fk_pattern = r'FOREIGN\s+KEY\s*\(([^)]+)\)\s*REFERENCES\s+`?(\w+)`?\s*\(([^)]+)\)'
        
        for match in re.finditer(fk_pattern, table_body, re.IGNORECASE):
            from_cols = [c.strip().strip('`') for c in match.group(1).split(',')]
            to_table = match.group(2)
            to_cols = [c.strip().strip('`') for c in match.group(3).split(',')]
            
            foreign_keys.append({
                'from_table': table_name,
                'from_columns': from_cols,
                'to_table': to_table,
                'to_columns': to_cols,
                'type': '1:N'
            })
        
        return foreign_keys
