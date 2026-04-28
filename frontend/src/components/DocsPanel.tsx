import { useState } from "react";
import { BookOpen, Search, ChevronRight, ExternalLink, Code, Database, Zap } from "lucide-react";
import { motion } from "motion/react";

interface DocSection {
  id: string;
  title: string;
  icon: any;
  content: string;
  examples?: { title: string; code: string }[];
}

const docs: DocSection[] = [
  {
    id: "getting-started",
    title: "Getting Started",
    icon: Zap,
    content: `Welcome to the SQL Conversion Platform! This tool helps you convert SQL schemas to MongoDB, Cassandra, and Neo4j with AI-powered explanations.

**Quick Start:**
1. Paste your SQL DDL statements in the editor
2. Click "Convert" to generate schemas for all databases
3. View AI explanations and performance insights
4. Export the converted schemas

**Input Methods:**
- **Manual**: Paste SQL directly
- **MySQL**: Connect to a live MySQL database
- **Upload**: Upload .sql or .txt files`,
    examples: [
      {
        title: "Simple Table",
        code: `CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(100) NOT NULL
);`
      }
    ]
  },
  {
    id: "mongodb",
    title: "MongoDB Conversion",
    icon: Database,
    content: `MongoDB uses a document-oriented model. The converter analyzes your SQL schema and determines the best approach:

**Embedding Strategy:**
- 1:1 relationships → Embedded documents
- 1:N with small N → Embedded arrays
- 1:N with large N → Referenced collections

**Output Includes:**
- Collection schemas with validation
- Index recommendations
- Sample documents
- Performance analysis`,
    examples: [
      {
        title: "Embedded Document",
        code: `{
  "_id": ObjectId("..."),
  "email": "user@example.com",
  "profile": {
    "firstName": "John",
    "lastName": "Doe"
  }
}`
      }
    ]
  },
  {
    id: "cassandra",
    title: "Cassandra Conversion",
    icon: Database,
    content: `Cassandra uses a query-first design approach. The converter creates denormalized tables optimized for your access patterns.

**Key Concepts:**
- **Partition Keys**: Determine data distribution
- **Clustering Keys**: Sort data within partitions
- **Denormalization**: Data duplication for read performance

**Output Includes:**
- Keyspace definition
- Primary tables
- Query-optimized tables
- Replication strategy`,
    examples: [
      {
        title: "Query-Optimized Table",
        code: `CREATE TABLE users_by_email (
  email TEXT,
  user_id UUID,
  username TEXT,
  PRIMARY KEY ((email))
);`
      }
    ]
  },
  {
    id: "neo4j",
    title: "Neo4j Conversion",
    icon: Database,
    content: `Neo4j uses a graph model with nodes and relationships. The converter transforms tables into nodes and foreign keys into relationships.

**Key Concepts:**
- **Nodes**: Entities (Users, Orders, Products)
- **Relationships**: Connections between nodes
- **Properties**: Attributes on nodes/relationships

**Output Includes:**
- Node definitions
- Relationship types
- Constraints and indexes
- Sample Cypher queries`,
    examples: [
      {
        title: "Create Relationship",
        code: `MATCH (u:User), (o:Order)
WHERE u.id = o.user_id
CREATE (u)-[:PLACED]->(o)`
      }
    ]
  },
  {
    id: "query-translation",
    title: "Query Translation",
    icon: Code,
    content: `The platform can translate SQL queries to MongoDB MQL, Cassandra CQL, and Neo4j Cypher.

**Supported Operations:**
- SELECT statements
- WHERE clauses
- JOIN operations
- GROUP BY and aggregations
- ORDER BY and LIMIT

**AI-Enhanced:**
- Explains translation decisions
- Identifies potential issues
- Suggests optimizations`,
    examples: [
      {
        title: "SQL to MongoDB",
        code: `-- SQL
SELECT * FROM users WHERE age > 18

-- MongoDB
db.users.find({ age: { $gt: 18 } })`
      }
    ]
  },
  {
    id: "mysql-connection",
    title: "MySQL Connection",
    icon: Database,
    content: `Connect directly to your MySQL database to extract schemas automatically.

**Steps:**
1. Click the "MySQL" tab
2. Enter connection details:
   - Host: localhost:3306
   - Username: your_username
   - Password: your_password
   - Database: database_name
3. Click "Connect & Extract Schema"
4. Review and convert the extracted schema

**Security:**
- Credentials are not stored
- Connection is direct from your browser
- Use read-only accounts when possible`,
  },
  {
    id: "ai-runtime",
    title: "AI Runtime (Ollama)",
    icon: Zap,
    content: `This platform runs with Ollama only for all AI-enhanced explanations and query translations.

**Why Ollama:**
- Fully local execution
- No third-party API dependency
- Better privacy and predictable runtime behavior

**Required setup:**
- Install Ollama locally
- Pull a model (example: mistral)
- Set OLLAMA_BASE_URL and OLLAMA_MODEL in backend/.env

**Configuration:**
Use backend/.env to configure host and model name.`,
  }
];

export default function DocsPanel() {
  const [selectedDoc, setSelectedDoc] = useState<string>("getting-started");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredDocs = docs.filter(doc =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const currentDoc = docs.find(doc => doc.id === selectedDoc) || docs[0];
  const Icon = currentDoc.icon;

  return (
    <div className="flex h-full bg-[#0a0a12]/90 backdrop-blur-xl">
      {/* Sidebar */}
      <div className="w-64 border-r border-white/10 flex flex-col">
        <div className="p-4 border-b border-white/10">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
              <BookOpen size={20} className="text-white" />
            </div>
            <h2 className="font-semibold text-white">Documentation</h2>
          </div>
          
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search docs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/50"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {filteredDocs.map((doc) => {
            const DocIcon = doc.icon;
            return (
              <button
                key={doc.id}
                onClick={() => setSelectedDoc(doc.id)}
                className={`w-full flex items-center gap-3 p-3 rounded-lg text-left transition-all mb-1 ${
                  selectedDoc === doc.id
                    ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                }`}
              >
                <DocIcon size={18} />
                <span className="text-sm font-medium flex-1">{doc.title}</span>
                <ChevronRight size={16} className={selectedDoc === doc.id ? 'opacity-100' : 'opacity-0'} />
              </button>
            );
          })}
        </div>

        <div className="p-4 border-t border-white/10">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300 transition-colors"
          >
            <ExternalLink size={14} />
            API Documentation
          </a>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        <motion.div
          key={selectedDoc}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-8 max-w-3xl"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
              <Icon size={24} className="text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white">{currentDoc.title}</h1>
          </div>

          <div className="prose prose-invert max-w-none">
            {currentDoc.content.split('\n\n').map((paragraph, i) => {
              if (paragraph.startsWith('**') && paragraph.endsWith('**')) {
                return (
                  <h3 key={i} className="text-xl font-semibold text-white mt-6 mb-3">
                    {paragraph.replace(/\*\*/g, '')}
                  </h3>
                );
              }
              if (paragraph.startsWith('- ')) {
                const items = paragraph.split('\n');
                return (
                  <ul key={i} className="list-disc list-inside space-y-2 text-gray-300 mb-4">
                    {items.map((item, j) => (
                      <li key={j}>{item.replace('- ', '').replace(/\*\*/g, '')}</li>
                    ))}
                  </ul>
                );
              }
              return (
                <p key={i} className="text-gray-300 leading-relaxed mb-4">
                  {paragraph}
                </p>
              );
            })}
          </div>

          {currentDoc.examples && currentDoc.examples.length > 0 && (
            <div className="mt-8">
              <h3 className="text-xl font-semibold text-white mb-4">Examples</h3>
              {currentDoc.examples.map((example, i) => (
                <div key={i} className="mb-6">
                  <h4 className="text-sm font-medium text-gray-400 mb-2">{example.title}</h4>
                  <div className="bg-[#0d1117] rounded-xl p-4 border border-white/10">
                    <pre className="text-sm text-blue-300 font-mono overflow-x-auto">
                      <code>{example.code}</code>
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
