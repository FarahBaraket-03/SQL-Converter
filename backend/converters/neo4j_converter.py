"""Neo4j Cypher converter."""
from typing import Dict, Any, List


class Neo4jConverter:
    """Convert SQL schema to Neo4j graph model."""
    
    def __init__(self, schema_info: Dict[str, Any]):
        self.schema_info = schema_info
        self.tables = schema_info.get('tables', [])
        self.relationships = schema_info.get('relationships', [])
    
    def convert(self) -> Dict[str, Any]:
        """Convert SQL schema to Neo4j Cypher."""
        nodes = []
        relationships = []
        
        # Convert tables to nodes
        for table in self.tables:
            node = self._convert_table_to_node(table)
            nodes.append(node)
        
        # Convert foreign keys to relationships
        for rel in self.relationships:
            relationship = self._convert_to_relationship(rel)
            relationships.append(relationship)
        
        # Generate Cypher output
        cypher_output = self._generate_cypher_output(nodes, relationships)
        
        return {
            'schema': cypher_output,
            'nodes': nodes,
            'relationships': relationships
        }
    
    def _convert_table_to_node(self, table: Dict[str, Any]) -> Dict[str, Any]:
        """Convert SQL table to Neo4j node."""
        label = self._to_pascal_case(table['name'])
        properties = []
        
        for column in table['columns']:
            neo4j_type = self._map_sql_type_to_neo4j(column['type'])
            properties.append({
                'name': column['name'],
                'type': neo4j_type,
                'is_unique': column['is_unique'] or column['is_primary_key']
            })
        
        return {
            'label': label,
            'properties': properties,
            'primary_keys': table['primary_keys']
        }
    
    def _convert_to_relationship(self, rel: Dict[str, Any]) -> Dict[str, Any]:
        """Convert foreign key to Neo4j relationship."""
        from_label = self._to_pascal_case(rel['from_table'])
        to_label = self._to_pascal_case(rel['to_table'])
        
        # Determine relationship type from table names
        rel_type = self._infer_relationship_type(rel['from_table'], rel['to_table'])
        
        return {
            'from_label': from_label,
            'to_label': to_label,
            'type': rel_type,
            'from_property': rel['from_columns'][0] if rel['from_columns'] else 'id',
            'to_property': rel['to_columns'][0] if rel['to_columns'] else 'id'
        }
    
    def _infer_relationship_type(self, from_table: str, to_table: str) -> str:
        """Infer meaningful relationship type from table names.
        
        Neo4j Best Practices:
        - Use UPPERCASE for relationship types
        - Use verbs or verb phrases (PLACED, BELONGS_TO, HAS)
        - Be specific and descriptive
        - Follow domain language
        """
        from_lower = from_table.lower()
        to_lower = to_table.lower()
        
        # E-commerce patterns
        if 'order' in from_lower and 'user' in to_lower:
            return 'PLACED_BY'
        elif 'order' in from_lower and 'product' in to_lower:
            return 'CONTAINS'
        elif 'order' in from_lower and 'customer' in to_lower:
            return 'ORDERED_BY'
        elif 'payment' in from_lower and 'order' in to_lower:
            return 'PAYS_FOR'
        elif 'shipment' in from_lower and 'order' in to_lower:
            return 'SHIPS'
        
        # Social media patterns
        elif 'comment' in from_lower and 'post' in to_lower:
            return 'COMMENTED_ON'
        elif 'comment' in from_lower and 'user' in to_lower:
            return 'WRITTEN_BY'
        elif 'like' in from_lower and 'post' in to_lower:
            return 'LIKES'
        elif 'follow' in from_lower:
            return 'FOLLOWS'
        elif 'friend' in from_lower:
            return 'FRIENDS_WITH'
        elif 'message' in from_lower and 'user' in to_lower:
            return 'SENT_BY'
        
        # User/Profile patterns
        elif 'profile' in from_lower and 'user' in to_lower:
            return 'BELONGS_TO'
        elif 'address' in from_lower and 'user' in to_lower:
            return 'LIVES_AT'
        elif 'setting' in from_lower and 'user' in to_lower:
            return 'CONFIGURED_BY'
        
        # Product/Category patterns
        elif 'product' in from_lower and 'category' in to_lower:
            return 'IN_CATEGORY'
        elif 'product' in from_lower and 'brand' in to_lower:
            return 'MANUFACTURED_BY'
        elif 'review' in from_lower and 'product' in to_lower:
            return 'REVIEWS'
        elif 'review' in from_lower and 'user' in to_lower:
            return 'WRITTEN_BY'
        
        # Generic patterns
        elif 'item' in from_lower:
            return 'PART_OF'
        elif 'detail' in from_lower:
            return 'DETAILS_FOR'
        else:
            # Generic relationship with meaningful name
            return f"RELATED_TO_{to_table.upper()}"
    
    def _generate_cypher_output(self, nodes: List[Dict[str, Any]], relationships: List[Dict[str, Any]]) -> str:
        """Generate Cypher statements."""
        output = []
        
        output.append("// Neo4j Graph Schema")
        output.append("")
        
        # Create constraints and indexes
        output.append("// Constraints & Indexes")
        for node in nodes:
            for prop in node['properties']:
                if prop['is_unique']:
                    output.append(f"CREATE CONSTRAINT {node['label'].lower()}_{prop['name']}_unique IF NOT EXISTS")
                    output.append(f"FOR (n:{node['label']})")
                    output.append(f"REQUIRE n.{prop['name']} IS UNIQUE;")
                    output.append("")
        
        # Create nodes
        output.append("// Create Nodes")
        for node in nodes:
            output.append(f"// {node['label']} Node")
            # FIX: Include ALL properties, not just first 3
            props = ", ".join([f"{p['name']}: ${p['name']}" for p in node['properties']])
            output.append(f"CREATE (n:{node['label']} {{{props}}})")
            output.append("RETURN n;")
            output.append("")
        
        # Create relationships
        if relationships:
            output.append("// Create Relationships")
            for rel in relationships:
                output.append(f"// {rel['from_label']} -> {rel['to_label']}")
                output.append(f"MATCH (a:{rel['from_label']}), (b:{rel['to_label']})")
                output.append(f"WHERE a.{rel['from_property']} = b.{rel['to_property']}")
                output.append(f"CREATE (a)-[r:{rel['type']}]->(b)")
                output.append("RETURN r;")
                output.append("")
        
        # Sample query
        output.append("// Sample Query: Traverse Relationships")
        if relationships:
            first_rel = relationships[0]
            output.append(f"MATCH (a:{first_rel['from_label']})-[r:{first_rel['type']}]->(b:{first_rel['to_label']})")
            output.append("RETURN a, r, b")
            output.append("LIMIT 10;")
        
        return "\n".join(output)
    
    def _map_sql_type_to_neo4j(self, sql_type: str) -> str:
        """Map SQL data types to Neo4j property types."""
        sql_type = sql_type.upper()
        
        if 'INT' in sql_type:
            return 'INTEGER'
        elif 'DECIMAL' in sql_type or 'NUMERIC' in sql_type or 'FLOAT' in sql_type or 'DOUBLE' in sql_type:
            return 'FLOAT'
        elif 'BOOL' in sql_type:
            return 'BOOLEAN'
        elif 'DATE' in sql_type or 'TIME' in sql_type:
            return 'DATETIME'
        elif 'TEXT' in sql_type or 'VARCHAR' in sql_type or 'CHAR' in sql_type:
            return 'STRING'
        else:
            return 'STRING'
    
    def _to_pascal_case(self, snake_str: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in snake_str.split('_'))
