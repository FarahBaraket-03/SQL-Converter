"""MongoDB schema converter."""
from typing import Dict, Any, List
import json


class MongoDBConverter:
    """Convert SQL schema to MongoDB document model."""
    
    def __init__(self, schema_info: Dict[str, Any]):
        self.schema_info = schema_info
        self.tables = schema_info.get('tables', [])
        self.relationships = schema_info.get('relationships', [])
    
    def convert(self) -> Dict[str, Any]:
        """Convert SQL schema to MongoDB collections."""
        collections = []
        embedded_relationships = []
        
        # Analyze relationships to determine embedding strategy
        embedding_strategy = self._determine_embedding_strategy()
        
        for table in self.tables:
            collection = self._convert_table_to_collection(table, embedding_strategy)
            collections.append(collection)
        
        # Generate MongoDB schema
        schema_output = self._generate_schema_output(collections)
        
        # Generate sample document
        sample_doc = self._generate_sample_document(collections[0] if collections else {})
        
        return {
            'schema': schema_output,
            'collections': collections,
            'sample_document': sample_doc,
            'embedding_strategy': embedding_strategy
        }
    
    def _determine_embedding_strategy(self) -> Dict[str, str]:
        """Determine which relationships should be embedded vs referenced.
        
        Rules:
        1. One-to-One: EMBED (e.g., User -> Profile)
        2. One-to-Few (< 100 items): EMBED (e.g., Order -> OrderItems)
        3. One-to-Many (> 100 items): REFERENCE (e.g., User -> Orders)
        4. Many-to-Many: REFERENCE (e.g., Students <-> Courses)
        5. Frequently accessed together: EMBED
        6. Independently queried: REFERENCE
        """
        strategy = {}
        
        for rel in self.relationships:
            from_table = rel['from_table'].lower()
            to_table = rel['to_table'].lower()
            
            # Detect relationship patterns
            embed_keywords = ['profile', 'detail', 'info', 'address', 'setting', 'preference', 'config']
            reference_keywords = ['user', 'customer', 'order', 'product', 'post', 'comment', 'transaction']
            
            # One-to-One patterns (embed)
            if any(keyword in from_table for keyword in embed_keywords):
                strategy[f"{from_table}->{to_table}"] = "embed"
                continue
            
            # Line items pattern (embed if reasonable size)
            if 'item' in from_table or 'line' in from_table:
                strategy[f"{from_table}->{to_table}"] = "embed"
                continue
            
            # Large collections (reference)
            if any(keyword in to_table for keyword in reference_keywords):
                strategy[f"{from_table}->{to_table}"] = "reference"
                continue
            
            # Default: reference for safety
            strategy[f"{from_table}->{to_table}"] = "reference"
        
        return strategy
    
    def _convert_table_to_collection(self, table: Dict[str, Any], embedding_strategy: Dict[str, str]) -> Dict[str, Any]:
        """Convert a SQL table to a MongoDB collection."""
        collection_name = table['name']
        fields = {}
        
        for column in table['columns']:
            field_name = self._to_camel_case(column['name'])
            field_type = self._map_sql_type_to_bson(column['type'])
            
            fields[field_name] = {
                'bsonType': field_type,
                'required': not column['is_nullable'],
                'unique': column['is_unique']
            }
        
        # Check for embedded relationships
        embedded_fields = self._get_embedded_fields(table, embedding_strategy)
        fields.update(embedded_fields)
        
        return {
            'name': collection_name,
            'fields': fields,
            'indexes': self._generate_indexes(table)
        }
    
    def _get_embedded_fields(self, table: Dict[str, Any], embedding_strategy: Dict[str, str]) -> Dict[str, Any]:
        """Get fields that should be embedded from related tables.
        
        FIX: Correct embedding direction - child embeds into parent.
        Example: profiles table embeds INTO users collection.
        """
        embedded = {}
        
        # Check if OTHER tables should be embedded INTO this table
        for rel in self.relationships:
            # FIX: Check if from_table (child) should embed into to_table (parent)
            if rel['to_table'] == table['name']:
                strategy_key = f"{rel['from_table']}->{rel['to_table']}"
                if embedding_strategy.get(strategy_key) == "embed":
                    # The from_table (child) should be embedded into this table (parent)
                    child_table = next((t for t in self.tables if t['name'] == rel['from_table']), None)
                    if child_table:
                        # Embed the child table's fields as a subdocument
                        embedded_field_name = self._to_camel_case(rel['from_table'])
                        embedded[embedded_field_name] = {
                            'bsonType': 'object',
                            'required': False,
                            'description': f'Embedded {rel["from_table"]} data'
                        }
        
        return embedded
    
    def _generate_indexes(self, table: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate index recommendations."""
        indexes = []
        
        # Primary key index
        for pk in table['primary_keys']:
            indexes.append({
                'field': self._to_camel_case(pk),
                'unique': True
            })
        
        # Unique constraints
        for column in table['columns']:
            if column['is_unique'] and not column['is_primary_key']:
                indexes.append({
                    'field': self._to_camel_case(column['name']),
                    'unique': True
                })
        
        # Foreign key indexes
        for fk in table['foreign_keys']:
            for col in fk['from_columns']:
                indexes.append({
                    'field': self._to_camel_case(col),
                    'unique': False
                })
        
        return indexes
    
    def _generate_schema_output(self, collections: List[Dict[str, Any]]) -> str:
        """Generate MongoDB schema validation code."""
        output = []
        
        for collection in collections:
            output.append(f"// {collection['name']} Collection")
            output.append(f"db.createCollection('{collection['name']}', {{")
            output.append("  validator: {")
            output.append("    $jsonSchema: {")
            output.append("      bsonType: 'object',")
            
            # Required fields
            required_fields = [name for name, field in collection['fields'].items() if field.get('required')]
            if required_fields:
                output.append(f"      required: {json.dumps(required_fields)},")
            
            output.append("      properties: {")
            output.append("        _id: { bsonType: 'objectId' },")
            
            for field_name, field_info in collection['fields'].items():
                output.append(f"        {field_name}: {{ bsonType: '{field_info['bsonType']}' }},")
            
            output.append("      }")
            output.append("    }")
            output.append("  }")
            output.append("});")
            output.append("")
            
            # Indexes
            if collection['indexes']:
                output.append(f"// Indexes for {collection['name']}")
                for index in collection['indexes']:
                    unique_str = ", { unique: true }" if index['unique'] else ""
                    output.append(f"db.{collection['name']}.createIndex({{ '{index['field']}': 1 }}{unique_str});")
                output.append("")
        
        return "\n".join(output)
    
    def _generate_sample_document(self, collection: Dict[str, Any]) -> str:
        """Generate a realistic sample MongoDB document with proper data."""
        if not collection:
            return "{}"
        
        collection_name = collection.get('name', '').lower()
        doc = {}
        
        # Generate realistic sample based on collection name
        for field_name, field_info in collection.get('fields', {}).items():
            bson_type = field_info['bsonType']
            doc[field_name] = self._get_realistic_sample_value(field_name, bson_type, collection_name)
        
        # Add metadata fields
        doc['createdAt'] = {'$date': '2024-01-15T10:30:00.000Z'}
        doc['updatedAt'] = {'$date': '2024-01-15T10:30:00.000Z'}
        
        return json.dumps(doc, indent=2, ensure_ascii=False)
    
    def _get_realistic_sample_value(self, field_name: str, bson_type: str, collection_name: str) -> Any:
        """Get realistic sample value based on field name and type."""
        field_lower = field_name.lower()
        
        # ID fields
        if field_name == '_id' or field_lower == 'id':
            return {'$oid': '507f1f77bcf86cd799439011'}
        
        # Email fields
        if 'email' in field_lower:
            return 'john.doe@example.com'
        
        # Name fields
        if field_lower == 'name' or field_lower == 'username':
            return 'John Doe'
        if 'firstname' in field_lower or field_lower == 'fname':
            return 'John'
        if 'lastname' in field_lower or field_lower == 'lname':
            return 'Doe'
        
        # Phone fields
        if 'phone' in field_lower or 'mobile' in field_lower:
            return '+1-555-0123'
        
        # Address fields
        if 'address' in field_lower:
            return '123 Main Street, New York, NY 10001'
        if 'city' in field_lower:
            return 'New York'
        if 'country' in field_lower:
            return 'United States'
        if 'zipcode' in field_lower or 'postalcode' in field_lower:
            return '10001'
        
        # URL fields
        if 'url' in field_lower or 'website' in field_lower:
            return 'https://example.com'
        if 'avatar' in field_lower or 'image' in field_lower or 'photo' in field_lower:
            return 'https://example.com/avatar.jpg'
        
        # Status fields
        if 'status' in field_lower:
            if 'order' in collection_name:
                return 'pending'
            elif 'user' in collection_name:
                return 'active'
            else:
                return 'active'
        
        # Price/Amount fields
        if 'price' in field_lower or 'amount' in field_lower or 'total' in field_lower:
            if bson_type == 'decimal':
                return {'$numberDecimal': '99.99'}
            return 99.99
        
        # Quantity fields
        if 'quantity' in field_lower or 'count' in field_lower or 'stock' in field_lower:
            return 10
        
        # Description fields
        if 'description' in field_lower or 'bio' in field_lower or 'about' in field_lower:
            return 'This is a sample description text that provides more details about the item.'
        
        # Boolean fields
        if bson_type == 'bool':
            if 'active' in field_lower or 'enabled' in field_lower or 'verified' in field_lower:
                return True
            return False
        
        # Date fields
        if bson_type == 'date' or 'date' in field_lower or 'time' in field_lower:
            if 'created' in field_lower:
                return {'$date': '2024-01-15T10:30:00.000Z'}
            elif 'updated' in field_lower or 'modified' in field_lower:
                return {'$date': '2024-01-15T10:30:00.000Z'}
            else:
                return {'$date': '2024-01-15T00:00:00.000Z'}
        
        # Array fields
        if bson_type == 'array':
            if 'tag' in field_lower or 'category' in field_lower:
                return ['tag1', 'tag2', 'tag3']
            elif 'item' in field_lower:
                return [
                    {
                        'productId': {'$oid': '507f1f77bcf86cd799439012'},
                        'name': 'Product Name',
                        'quantity': 2,
                        'price': {'$numberDecimal': '49.99'}
                    }
                ]
            return []
        
        # Object/Embedded fields
        if bson_type == 'object':
            if 'address' in field_lower:
                return {
                    'street': '123 Main Street',
                    'city': 'New York',
                    'state': 'NY',
                    'zipCode': '10001',
                    'country': 'United States'
                }
            elif 'profile' in field_lower:
                return {
                    'firstName': 'John',
                    'lastName': 'Doe',
                    'avatarUrl': 'https://example.com/avatar.jpg',
                    'bio': 'Software developer and tech enthusiast'
                }
            return {}
        
        # Default values by type
        if bson_type == 'string':
            return f'sample_{field_name}'
        elif bson_type == 'int':
            return 123
        elif bson_type == 'decimal':
            return {'$numberDecimal': '99.99'}
        elif bson_type == 'bool':
            return True
        elif bson_type == 'objectId':
            return {'$oid': '507f1f77bcf86cd799439011'}
        else:
            return None
    
    def _map_sql_type_to_bson(self, sql_type: str) -> str:
        """Map SQL data types to BSON types."""
        sql_type = sql_type.upper()
        
        if 'INT' in sql_type or 'SERIAL' in sql_type:
            return 'int'
        elif 'DECIMAL' in sql_type or 'NUMERIC' in sql_type or 'FLOAT' in sql_type or 'DOUBLE' in sql_type:
            return 'decimal'
        elif 'BOOL' in sql_type:
            return 'bool'
        elif 'DATE' in sql_type or 'TIME' in sql_type:
            return 'date'
        elif 'TEXT' in sql_type or 'VARCHAR' in sql_type or 'CHAR' in sql_type:
            return 'string'
        elif 'BLOB' in sql_type or 'BINARY' in sql_type:
            return 'binData'
        else:
            return 'string'
    
    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase."""
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
