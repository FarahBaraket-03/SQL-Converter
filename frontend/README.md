# SQL-to-NoSQL AI Converter

An interactive web application that converts SQL schemas to MongoDB, Cassandra, and Neo4j using AI (Mistral via Groq) and LangGraph.

## Tech Stack
- **Backend**: Python 3.11, FastAPI, SQLGlot, LangGraph, FAISS, Groq API
- **Frontend**: Next.js 14, Tailwind CSS, Monaco Editor, Mermaid.js, Cytoscape.js
- **DevOps**: Docker, Docker Compose

## Setup Instructions

1. **Clone the repository**

2. **Environment Variables**
   Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   - Get a free Groq API key from [console.groq.com](https://console.groq.com) for fast, free LLM inference.
   - If `GROQ_API_KEY` is not set, the app will use mock explanations (or you can configure local Ollama in `ai_enhancer.py`).

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the Application**
   - Frontend: `http://localhost:3000`
   - Backend API Docs: `http://localhost:8000/docs`

## Features
- **SQL Parsing**: Uses SQLGlot to extract AST from DDL statements.
- **LangGraph Pipeline**: Orchestrates parallel conversion to 3 NoSQL targets.
- **RAG Context**: Upload `.sql` files to build a FAISS index for context-aware AI enhancements.
- **AI Explanations**: Mistral 7B provides denormalization suggestions and confidence scores.
- **Interactive UI**: Monaco editor for input, Mermaid/Cytoscape for visualization.
