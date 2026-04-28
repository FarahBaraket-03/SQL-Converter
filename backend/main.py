"""Main FastAPI application for SQL conversion platform."""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional

from config import settings
from models import (
    ConversionRequest, ConversionResponse, ConversionResult,
    QueryTranslationRequest, QueryTranslationResult,
    MySQLConnectionRequest, MySQLSchemaResponse,
    HealthResponse, TargetDatabase, DatabaseStats
)
from parsers.sql_parser import SQLParser
from converters.mongodb_converter import MongoDBConverter
from converters.cassandra_converter import CassandraConverter
from converters.neo4j_converter import Neo4jConverter
from ai.langgraph_enhancer import LangGraphAIEnhancer
from database.mysql_extractor import MySQLExtractor


# Initialize FastAPI app
app = FastAPI(
    title="SQL Conversion Platform API",
    description="AI-powered SQL to NoSQL conversion service with LangGraph",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LangGraph AI enhancer
ai_enhancer = LangGraphAIEnhancer()


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        ai_provider=settings.ai_provider,
        ai_available=ai_enhancer.llm is not None
    )


@app.post("/api/convert", response_model=ConversionResponse)
async def convert_schema(request: ConversionRequest):
    """
    Convert SQL schema to target NoSQL databases.
    
    Supports MongoDB, Cassandra, and Neo4j conversions with AI-enhanced explanations.
    """
    try:
        # Parse SQL schema
        parser = SQLParser(request.sql)
        schema_info = parser.parse()
        
        if schema_info['table_count'] == 0:
            raise HTTPException(status_code=400, detail="No valid tables found in SQL")
        
        response = ConversionResponse()
        
        # Convert to all databases in parallel worker threads.
        # Converter + AI enhancement are blocking, so run them outside the event loop.
        import asyncio
        
        tasks = []
        if TargetDatabase.MONGODB in request.target_databases:
            tasks.append(('mongodb', asyncio.to_thread(
                _convert_to_mongodb,
                request.sql, schema_info, request.include_ai_explanation
            )))
        
        if TargetDatabase.CASSANDRA in request.target_databases:
            tasks.append(('cassandra', asyncio.to_thread(
                _convert_to_cassandra,
                request.sql, schema_info, request.include_ai_explanation
            )))
        
        if TargetDatabase.NEO4J in request.target_databases:
            tasks.append(('neo4j', asyncio.to_thread(
                _convert_to_neo4j,
                request.sql, schema_info, request.include_ai_explanation
            )))
        
        # Execute all conversions in parallel
        results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
        
        # Assign results
        for i, (db_name, _) in enumerate(tasks):
            result = results[i]
            if isinstance(result, Exception):
                print(f"Warning: {db_name} conversion failed: {result}")
                continue
            
            if db_name == 'mongodb':
                response.mongodb = result
            elif db_name == 'cassandra':
                response.cassandra = result
            elif db_name == 'neo4j':
                response.neo4j = result
        
        # Add metadata
        response.metadata = {
            'table_count': schema_info['table_count'],
            'relationship_count': schema_info['relationship_count'],
            'input_method': request.input_method.value,
            'parallel_execution': True
        }
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@app.post("/api/translate-query", response_model=QueryTranslationResult)
async def translate_query(request: QueryTranslationRequest):
    """
    Translate SQL query to target database query language.
    
    Supports translation to MongoDB MQL, Cassandra CQL, and Neo4j Cypher.
    """
    try:
        import asyncio

        # Use AI to translate query
        translation = await asyncio.to_thread(
            ai_enhancer.translate_query,
            request.sql_query,
            request.target_database.value,
            request.schema_context,
        )
        
        return QueryTranslationResult(
            original_sql=request.sql_query,
            translated_query=translation['translated_query'],
            target_database=request.target_database,
            explanation=translation['explanation'],
            warnings=translation['warnings']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.post("/api/mysql/extract", response_model=MySQLSchemaResponse)
async def extract_mysql_schema(connection: MySQLConnectionRequest):
    """
    Extract schema from a MySQL database.
    
    Connects to MySQL server and retrieves DDL statements for all tables.
    """
    try:
        with MySQLExtractor(connection) as extractor:
            schema_data = extractor.extract_schema()
        
        return MySQLSchemaResponse(
            sql=schema_data['sql'],
            tables=schema_data['tables'],
            database=schema_data['database']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MySQL extraction failed: {str(e)}")


@app.post("/api/upload-sql")
async def upload_sql_file(file: UploadFile = File(...)):
    """
    Upload SQL file for conversion.
    
    Accepts .sql or .txt files containing SQL DDL statements.
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.sql', '.txt')):
            raise HTTPException(status_code=400, detail="Only .sql and .txt files are supported")
        
        # Read file content
        content = await file.read()
        sql = content.decode('utf-8')
        
        return JSONResponse({
            'sql': sql,
            'filename': file.filename,
            'size': len(content)
        })
    
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


# Helper functions

def _convert_to_mongodb(sql: str, schema_info: dict, include_ai: bool) -> ConversionResult:
    """Convert to MongoDB with LangGraph AI enhancement."""
    converter = MongoDBConverter(schema_info)
    result = converter.convert()
    
    # Get LangGraph AI enhancement
    if include_ai:
        enhancement = ai_enhancer.enhance_conversion(
            sql_schema=sql,
            converted_schema=result['schema'],
            target_db='mongodb'
        )
    else:
        enhancement = _get_default_enhancement()
    
    return ConversionResult(
        schema=result['schema'],
        explanation=enhancement['explanation'],
        warnings=enhancement['warnings'],
        stats=DatabaseStats(**enhancement['stats']),
        score=enhancement['score'],
        sample_data=result.get('sample_document'),
        visualization={
            'collections': result.get('collections', []),
            'embedding_strategy': result.get('embedding_strategy', {})
        }
    )


def _convert_to_cassandra(sql: str, schema_info: dict, include_ai: bool) -> ConversionResult:
    """Convert to Cassandra with LangGraph AI enhancement."""
    converter = CassandraConverter(schema_info)
    result = converter.convert()
    
    # Get LangGraph AI enhancement
    if include_ai:
        enhancement = ai_enhancer.enhance_conversion(
            sql_schema=sql,
            converted_schema=result['schema'],
            target_db='cassandra'
        )
    else:
        enhancement = _get_default_enhancement()
    
    return ConversionResult(
        schema=result['schema'],
        explanation=enhancement['explanation'],
        warnings=enhancement['warnings'],
        stats=DatabaseStats(**enhancement['stats']),
        score=enhancement['score'],
        visualization={
            'keyspace': result.get('keyspace'),
            'tables': result.get('tables', [])
        }
    )


def _convert_to_neo4j(sql: str, schema_info: dict, include_ai: bool) -> ConversionResult:
    """Convert to Neo4j with LangGraph AI enhancement."""
    converter = Neo4jConverter(schema_info)
    result = converter.convert()
    
    # Get LangGraph AI enhancement
    if include_ai:
        enhancement = ai_enhancer.enhance_conversion(
            sql_schema=sql,
            converted_schema=result['schema'],
            target_db='neo4j'
        )
    else:
        enhancement = _get_default_enhancement()
    
    return ConversionResult(
        schema=result['schema'],
        explanation=enhancement['explanation'],
        warnings=enhancement['warnings'],
        stats=DatabaseStats(**enhancement['stats']),
        score=enhancement['score'],
        visualization={
            'nodes': result.get('nodes', []),
            'relationships': result.get('relationships', [])
        }
    )


def _get_default_enhancement() -> dict:
    """Get default enhancement when AI is disabled."""
    return {
        'explanation': 'Schema conversion completed successfully.',
        'warnings': [],
        'stats': {
            'reads': 'O(1)',
            'writes': 'O(1)',
            'complexity': 'Medium'
        },
        'score': 90
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
