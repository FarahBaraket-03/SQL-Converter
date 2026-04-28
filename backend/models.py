"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum


class TargetDatabase(str, Enum):
    """Supported target databases."""
    MONGODB = "mongodb"
    CASSANDRA = "cassandra"
    NEO4J = "neo4j"


class InputMethod(str, Enum):
    """SQL input methods."""
    MANUAL = "manual"
    MYSQL = "mysql"
    FILE = "file"


class MySQLConnectionRequest(BaseModel):
    """MySQL connection parameters."""
    host: str = Field(..., description="MySQL server host")
    port: int = Field(3306, description="MySQL server port")
    user: str = Field(..., description="MySQL username")
    password: str = Field(..., description="MySQL password")
    database: str = Field(..., description="Database name to extract schema from")


class ConversionRequest(BaseModel):
    """Request model for SQL conversion."""
    sql: str = Field(..., description="SQL DDL statements to convert")
    target_databases: List[TargetDatabase] = Field(
        default=[TargetDatabase.MONGODB, TargetDatabase.CASSANDRA, TargetDatabase.NEO4J],
        description="Target databases for conversion"
    )
    input_method: InputMethod = Field(InputMethod.MANUAL, description="How the SQL was provided")
    mysql_connection: Optional[MySQLConnectionRequest] = None
    include_ai_explanation: bool = Field(True, description="Include AI-generated explanations")


class QueryTranslationRequest(BaseModel):
    """Request model for query translation."""
    sql_query: str = Field(..., description="SQL query to translate")
    target_database: TargetDatabase = Field(..., description="Target database for translation")
    schema_context: Optional[str] = Field(None, description="Optional schema context for better translation")


class DatabaseStats(BaseModel):
    """Performance statistics for a database conversion."""
    reads: str = Field(..., description="Read performance complexity")
    writes: str = Field(..., description="Write performance complexity")
    complexity: str = Field(..., description="Overall complexity rating")


class ConversionResult(BaseModel):
    """Result for a single database conversion."""
    schema_code: str = Field(..., description="Converted schema/DDL", alias="schema")
    explanation: str = Field(..., description="AI-generated explanation of design decisions")
    warnings: List[str] = Field(default_factory=list, description="Potential issues or considerations")
    stats: DatabaseStats = Field(..., description="Performance statistics")
    score: int = Field(..., ge=0, le=100, description="Confidence score (0-100)")
    sample_data: Optional[str] = Field(None, description="Sample data structure")
    visualization: Optional[Dict[str, Any]] = Field(
        None,
        description="Structured graph/layout data used by the frontend visualization layer"
    )
    
    model_config = {"populate_by_name": True}  # Allow both 'schema' and 'schema_code'


class ConversionResponse(BaseModel):
    """Complete conversion response."""
    mongodb: Optional[ConversionResult] = None
    cassandra: Optional[ConversionResult] = None
    neo4j: Optional[ConversionResult] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class QueryTranslationResult(BaseModel):
    """Result of query translation."""
    original_sql: str = Field(..., description="Original SQL query")
    translated_query: str = Field(..., description="Translated query in target database language")
    target_database: TargetDatabase = Field(..., description="Target database")
    explanation: str = Field(..., description="Explanation of translation decisions")
    warnings: List[str] = Field(default_factory=list, description="Potential issues")


class MySQLSchemaResponse(BaseModel):
    """Response containing extracted MySQL schema."""
    sql: str = Field(..., description="Extracted SQL DDL statements")
    tables: List[str] = Field(..., description="List of table names")
    database: str = Field(..., description="Database name")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    ai_provider: str
    ai_available: bool
