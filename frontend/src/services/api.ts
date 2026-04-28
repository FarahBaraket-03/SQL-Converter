/**
 * API service for communicating with the backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ConversionRequest {
  sql: string;
  target_databases?: ('mongodb' | 'cassandra' | 'neo4j')[];
  input_method?: 'manual' | 'mysql' | 'file';
  include_ai_explanation?: boolean;
}

export interface DatabaseStats {
  reads: string;
  writes: string;
  complexity: string;
}

export interface ConversionResult {
  schema: string;
  explanation: string;
  warnings: string[];
  stats: DatabaseStats;
  score: number;
  sample_data?: string;
  visualization?: any;
}

export interface ConversionResponse {
  mongodb?: ConversionResult;
  cassandra?: ConversionResult;
  neo4j?: ConversionResult;
  metadata?: {
    table_count: number;
    relationship_count: number;
    input_method: string;
  };
}

export interface QueryTranslationRequest {
  sql_query: string;
  target_database: 'mongodb' | 'cassandra' | 'neo4j';
  schema_context?: string;
}

export interface QueryTranslationResult {
  original_sql: string;
  translated_query: string;
  target_database: string;
  explanation: string;
  warnings: string[];
}

export interface MySQLConnectionRequest {
  host: string;
  port?: number;
  user: string;
  password: string;
  database: string;
}

export interface MySQLSchemaResponse {
  sql: string;
  tables: string[];
  database: string;
}

export interface HealthResponse {
  status: string;
  ai_provider: string;
  ai_available: boolean;
}

class APIService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Check API health status
   */
  async healthCheck(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/`);
    if (!response.ok) {
      throw new Error('API health check failed');
    }
    return response.json();
  }

  /**
   * Convert SQL schema to NoSQL databases
   */
  async convertSchema(request: ConversionRequest): Promise<ConversionResponse> {
    const response = await fetch(`${this.baseUrl}/api/convert`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        sql: request.sql,
        target_databases: request.target_databases || ['mongodb', 'cassandra', 'neo4j'],
        input_method: request.input_method || 'manual',
        include_ai_explanation: request.include_ai_explanation !== false,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Conversion failed');
    }

    return response.json();
  }

  /**
   * Translate SQL query to target database language
   */
  async translateQuery(request: QueryTranslationRequest): Promise<QueryTranslationResult> {
    const response = await fetch(`${this.baseUrl}/api/translate-query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Query translation failed');
    }

    return response.json();
  }

  /**
   * Extract schema from MySQL database
   */
  async extractMySQLSchema(connection: MySQLConnectionRequest): Promise<MySQLSchemaResponse> {
    const response = await fetch(`${this.baseUrl}/api/mysql/extract`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        host: connection.host,
        port: connection.port || 3306,
        user: connection.user,
        password: connection.password,
        database: connection.database,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'MySQL extraction failed');
    }

    return response.json();
  }

  /**
   * Upload SQL file
   */
  async uploadSQLFile(file: File): Promise<{ sql: string; filename: string; size: number }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/api/upload-sql`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'File upload failed');
    }

    return response.json();
  }
}

// Export singleton instance
export const apiService = new APIService();

// Export class for testing
export default APIService;
