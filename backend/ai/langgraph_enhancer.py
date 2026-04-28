"""LangGraph-based AI enhancement for schema conversion."""
from typing import Any, Dict, Optional, TypedDict, Annotated
import json
import re
from operator import add
import urllib.request

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from config import settings


class ConversionState(TypedDict):
    """State for the conversion enhancement workflow."""

    sql_schema: str
    target_db: str
    converted_schema: str
    explanation: str
    warnings: Annotated[list, add]
    stats: Dict[str, str]
    score: int
    error: Optional[str]


class _LLMResponse:
    """Minimal response object compatible with the existing invoke flow."""

    def __init__(self, content: str):
        self.content = content


class _OllamaHTTPClient:
    """Fallback Ollama client using the native /api/generate endpoint."""

    def __init__(self, base_url: str, model: str, temperature: float = 0.3, timeout: float = 300.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    def _normalize_message_content(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    parts.append(str(item.get("text", "")))
                else:
                    parts.append(str(item))
            return "\n".join([p for p in parts if p]).strip()
        return str(content)

    def invoke(self, messages: Any) -> _LLMResponse:
        prompt_parts = []

        for message in messages:
            role = getattr(message, "type", "user")
            if role == "human":
                role = "user"
            content = self._normalize_message_content(getattr(message, "content", ""))
            prompt_parts.append(f"[{role.upper()}]\n{content}")

        prompt_text = "\n\n".join(prompt_parts)
        payload = {
            "model": self.model,
            "prompt": prompt_text,
            "stream": False,
            "options": {
                "temperature": self.temperature,
            },
        }

        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        return _LLMResponse(str(data.get("response", "")).strip())


class LangGraphAIEnhancer:
    """LangGraph-based AI enhancer for schema conversions."""

    def __init__(self):
        self.provider = settings.ai_provider
        self.llm = self._initialize_llm()
        self.graph = self._build_graph()

    def _initialize_llm(self):
        """Initialize LLM with BlazeAPI (primary) or Ollama (fallback)."""
        try:
            # Try BlazeAPI first
            if self.provider == "blazeapi" and settings.blazeapi_api_key:
                print(f"Initializing BlazeAPI with model: {settings.blazeapi_model}")
                from openai import OpenAI
                
                client = OpenAI(
                    api_key=settings.blazeapi_api_key,
                    base_url=settings.blazeapi_base_url,
                )
                
                # Wrap OpenAI client to match our interface
                return self._wrap_openai_client(client, settings.blazeapi_model)
            
            # Fallback to Ollama
            print(f"Falling back to Ollama with model: {settings.ollama_model}")
            self.provider = "ollama"
            
            try:
                # Prefer langchain chat integration when available
                from langchain_community.chat_models import ChatOllama

                return ChatOllama(
                    model=settings.ollama_model,
                    base_url=settings.ollama_base_url,
                    temperature=0.3,
                )
            except ModuleNotFoundError:
                print("langchain_community not installed, using direct Ollama HTTP client fallback.")
                return _OllamaHTTPClient(
                    base_url=settings.ollama_base_url,
                    model=settings.ollama_model,
                    temperature=0.3,
                    timeout=300.0,
                )
        except Exception as e:
            print(f"Failed to initialize LLM: {e}")
            print("Falling back to Ollama...")
            self.provider = "ollama"
            
            try:
                return _OllamaHTTPClient(
                    base_url=settings.ollama_base_url,
                    model=settings.ollama_model,
                    temperature=0.3,
                    timeout=300.0,
                )
            except Exception as fallback_error:
                print(f"Ollama fallback also failed: {fallback_error}")
                return None
    
    def _wrap_openai_client(self, client, model: str):
        """Wrap OpenAI client to match our LLM interface."""
        class OpenAIWrapper:
            def __init__(self, client, model):
                self.client = client
                self.model = model
            
            def invoke(self, messages):
                """Convert LangChain-style messages to OpenAI format and call API."""
                openai_messages = []
                
                for msg in messages:
                    role = "user"
                    if hasattr(msg, "type"):
                        if msg.type == "system":
                            role = "system"
                        elif msg.type == "human":
                            role = "user"
                        elif msg.type == "ai":
                            role = "assistant"
                    
                    content = msg.content if hasattr(msg, "content") else str(msg)
                    openai_messages.append({"role": role, "content": content})
                
                # Debug: Print first message preview
                if openai_messages:
                    first_msg = openai_messages[0]
                    preview = first_msg['content'][:100] if len(first_msg['content']) > 100 else first_msg['content']
                    print(f"[BlazeAPI] Sending {len(openai_messages)} messages, first: {preview}...")
                
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=openai_messages,
                        temperature=0.3,
                    )
                    
                    result = response.choices[0].message.content
                    print(f"[BlazeAPI] Received response: {len(result)} chars")
                    return _LLMResponse(result)
                    
                except Exception as e:
                    print(f"[BlazeAPI] Error: {e}")
                    raise
        
        return OpenAIWrapper(client, model)

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for conversion enhancement.
        
        FIX: Removed redundant _analyze_schema node that was overwritten by _generate_explanation.
        """
        workflow = StateGraph(ConversionState)

        # FIX: Start directly with generate_explanation (removed analyze_schema)
        workflow.add_node("generate_explanation", self._generate_explanation)
        workflow.add_node("identify_warnings", self._identify_warnings)
        workflow.add_node("calculate_stats", self._calculate_stats)
        workflow.add_node("score_conversion", self._score_conversion)

        workflow.set_entry_point("generate_explanation")
        workflow.add_edge("generate_explanation", "identify_warnings")
        workflow.add_edge("identify_warnings", "calculate_stats")
        workflow.add_edge("calculate_stats", "score_conversion")
        workflow.add_edge("score_conversion", END)

        return workflow.compile()

    def _invoke_prompt(self, prompt: ChatPromptTemplate) -> str:
        """Invoke a prompt and normalize model output to plain text."""
        response = self.llm.invoke(prompt.format_messages())
        content = response.content if hasattr(response, "content") else str(response)
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    parts.append(str(item.get("text", "")).strip())
                else:
                    parts.append(str(item).strip())
            return "\n".join(part for part in parts if part).strip()
        return str(content).strip()

    def _extract_json_payload(self, content: str) -> Dict[str, Any]:
        """Extract JSON payload from plain text or fenced code blocks."""
        text = content.strip()
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in text:
            text = text.split("```", 1)[1].split("```", 1)[0].strip()
        return json.loads(text)

    def _normalize_explanation(self, content: str, target_db: str) -> str:
        """Normalize AI output into a consistent, human-readable markdown structure."""
        cleaned = content.strip()
        if "```" in cleaned:
            cleaned = cleaned.replace("```markdown", "").replace("```", "").strip()

        if "## Overview" in cleaned and "## Design Decisions" in cleaned:
            return cleaned

        lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
        summary = lines[0] if lines else f"Converted SQL schema to {target_db.upper()} successfully."

        decision_candidates = []
        for line in lines[1:]:
            normalized = line.lstrip("-* ").strip()
            if normalized:
                decision_candidates.append(normalized)

        if not decision_candidates:
            decision_candidates = [
                f"Model aligns structure with {target_db.upper()} access patterns.",
                "Schema prioritizes predictable reads and writes.",
                "Indexes and key strategy are tuned for common query paths.",
            ]

        decisions = "\n".join([f"- {item}" for item in decision_candidates[:3]])

        return (
            f"## Overview\n{summary}\n\n"
            f"## Design Decisions\n{decisions}\n\n"
            f"## Why This Works\n"
            f"- The model uses {target_db.upper()}-native modeling patterns.\n"
            f"- Query paths are simplified to reduce runtime complexity.\n"
            f"- Output balances performance, maintainability, and data integrity.\n\n"
            f"## Validation Checklist\n"
            f"- Run real read/write workloads against representative data volumes.\n"
            f"- Validate key/index strategy against your hottest queries.\n"
            f"- Review edge cases such as nulls, high-cardinality fields, and updates."
        )

    def _generate_explanation(self, state: ConversionState) -> ConversionState:
        """Generate detailed explanation of design decisions - with enhanced prompts."""
        if not self.llm:
            state["explanation"] = self._get_fast_explanation(state)
            return state

        try:
            # Enhanced database-specific prompts with best practices and real-world examples
            db_specific_prompts = {
                "mongodb": """You are a senior MongoDB architect with 10+ years of production experience.

**Focus Areas:**
1. **Embedding vs Referencing Strategy**
   - Embed: 1:1 relationships (User→Profile), 1:few (<100 items like Order→OrderItems)
   - Reference: 1:many (>100 items like User→Orders), many:many (Students↔Courses)
   - Consider: Access patterns, document size limits (16MB), update frequency

2. **Document Structure & Schema Design**
   - Organize data for common query patterns (80/20 rule)
   - Denormalize frequently accessed data together
   - Use arrays for bounded lists, references for unbounded

3. **Index Strategy**
   - Compound indexes for multi-field queries
   - Text indexes for search functionality
   - TTL indexes for time-based expiration
   - Avoid over-indexing (impacts write performance)

4. **Performance Optimization**
   - Minimize document size for faster reads
   - Use projection to fetch only needed fields
   - Consider sharding strategy for horizontal scaling
   - Optimize for read-heavy vs write-heavy workloads

**Real-World Example:**
For an e-commerce schema:
- Embed: Order items (bounded, always accessed together)
- Reference: User orders (unbounded, independently queried)
- Index: email (unique), status+createdAt (compound for filtering)""",
                
                "cassandra": """You are a senior Cassandra architect with 10+ years of production experience.

**Focus Areas:**
1. **Partition Key Selection (Critical!)**
   - High cardinality: Distribute data evenly across nodes
   - Match WHERE clauses: Partition key must be in WHERE
   - Avoid hot partitions: No celebrity problem
   - Size: Keep partitions under 100MB (ideally <10MB)

2. **Clustering Key Strategy**
   - Sort order within partitions (time-series, rankings)
   - Enables range queries and pagination
   - Use DESC for recent-first queries
   - Combine with partition key for uniqueness

3. **Denormalization & Query Tables**
   - One query = One table (query-first design)
   - Duplicate data across tables for different access patterns
   - Materialized views for simple transformations
   - Batch writes to maintain consistency

4. **Performance Optimization**
   - Avoid ALLOW FILTERING (full table scan)
   - Use prepared statements
   - Batch related writes
   - Monitor partition sizes and tombstones

**Real-World Example:**
For a time-series sensor data:
- Partition: sensor_id + date (distribute by sensor, bound by day)
- Clustering: timestamp DESC (recent readings first)
- Query table: sensor_id + metric_type for specific metrics""",
                
                "neo4j": """You are a senior Neo4j architect with 10+ years of production experience.

**Focus Areas:**
1. **Node Labels & Properties**
   - Meaningful labels: User, Product, Order (not generic Entity)
   - Index frequently queried properties
   - Avoid storing large text in nodes (use external storage)
   - Use constraints for data integrity

2. **Relationship Types & Direction**
   - Verb-based names: PURCHASED, FOLLOWS, BELONGS_TO
   - Direction matters: User-[:PURCHASED]->Product
   - Properties on relationships: timestamp, quantity, status
   - Avoid relationship-heavy nodes (>1M relationships)

3. **Traversal Patterns & Queries**
   - Start from indexed nodes
   - Use relationship types to filter traversals
   - Limit depth for performance (avoid unbounded paths)
   - Consider bidirectional relationships for flexibility

4. **Performance Optimization**
   - Create indexes on frequently searched properties
   - Use PROFILE/EXPLAIN to analyze queries
   - Batch imports with UNWIND
   - Consider graph algorithms (PageRank, Community Detection)

**Real-World Example:**
For a social network:
- Nodes: User (indexed on email), Post, Comment
- Relationships: User-[:FOLLOWS]->User, User-[:POSTED]->Post
- Queries: Friend recommendations (2-3 hops), feed generation (1 hop)"""
            }

            specific_prompt = db_specific_prompts.get(state["target_db"], "Explain the conversion decisions.")
            
            # Enhanced system prompt with expertise and context
            system_prompt = f"""{specific_prompt}

**Your Task:**
Analyze the SQL to {state['target_db'].upper()} conversion and provide:
1. Clear explanation of design decisions (WHY, not just WHAT)
2. Specific examples from the schema
3. Trade-offs and alternatives considered
4. Performance implications
5. Best practices applied

**Output Format:**
Write in clear, concise paragraphs (3-5 sentences each).
Use technical terms but explain complex concepts.
Focus on practical, actionable insights.
Avoid generic statements - be specific to THIS schema."""
            
            # Simplified prompt for faster response with schema preview
            sql_preview = state['sql_schema'][:800] if len(state['sql_schema']) > 800 else state['sql_schema']
            converted_preview = state['converted_schema'][:800] if len(state['converted_schema']) > 800 else state['converted_schema']
            
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=system_prompt),
                HumanMessage(
                    content=(
                        f"Explain this SQL to {state['target_db'].upper()} conversion in 4-6 sentences.\n\n"
                        f"**SQL Schema (preview):**\n```sql\n{sql_preview}\n```\n\n"
                        f"**{state['target_db'].upper()} Schema (preview):**\n```\n{converted_preview}\n```\n\n"
                        "Focus on the most important design decisions and their rationale."
                    )
                ),
            ])

            content = self._invoke_prompt(prompt)
            state["explanation"] = self._normalize_explanation(content, state["target_db"])

        except Exception as e:
            print(f"Explanation generation failed: {e}")
            state["explanation"] = self._get_fast_explanation(state)

        return state
    
    def _get_fast_explanation(self, state: ConversionState) -> str:
        """Generate a fast explanation without LLM."""
        db = state["target_db"].upper()
        return f"""## Overview
Successfully converted SQL schema to {db} format.

## Design Decisions
- Schema structure optimized for {db} data model
- Indexes and keys configured for common query patterns
- Data types mapped to native {db} types

## Why This Works
- Follows {db} best practices and conventions
- Balances read/write performance
- Maintains data integrity and relationships

## Validation Checklist
- Test with representative data volumes
- Validate query performance
- Review edge cases and constraints"""

    def _identify_warnings(self, state: ConversionState) -> ConversionState:
        """Identify potential warnings and considerations - with fast heuristics.
        
        FIX: Use extend() to respect the Annotated[list, add] reducer.
        """
        warnings = []
        schema = state.get("converted_schema", "").lower()
        target_db = state["target_db"].lower()
        
        # Common warnings based on schema analysis
        if target_db == "mongodb":
            if "id" in schema and "_id" in schema:
                warnings.append("Schema contains both 'id' and '_id' fields. MongoDB uses '_id' as the primary key by default.")
            if "timestamp" in schema and "default" not in schema:
                warnings.append("Timestamp fields may need default values. MongoDB doesn't auto-populate timestamps like SQL.")
            if "unique" in schema:
                warnings.append("Unique indexes should be created explicitly. Consider case-sensitivity for string fields.")
        
        elif target_db == "cassandra":
            if "partition" not in schema:
                warnings.append("No partition key detected. Cassandra requires a partition key for data distribution.")
            if "order by" in state.get("sql_schema", "").lower():
                warnings.append("SQL ORDER BY requires clustering columns in Cassandra. Verify sort order matches clustering key.")
        
        elif target_db == "neo4j":
            if "relationship" not in schema and "rel" not in schema:
                warnings.append("No relationships detected. Neo4j is optimized for connected data with explicit relationships.")
        
        # Generic warnings
        if len(schema) > 5000:
            warnings.append("Large schema detected. Consider breaking into smaller, focused models for better performance.")
        
        # FIX: Return dict with warnings key to trigger the reducer
        return {"warnings": warnings[:4]}

    def _calculate_stats(self, state: ConversionState) -> ConversionState:
        """Calculate performance statistics - with fast heuristics."""
        # Use fast heuristics instead of LLM
        target_db = state["target_db"].lower()
        schema = state.get("converted_schema", "")
        
        # Simple heuristic based on schema complexity
        has_indexes = "index" in schema.lower() or "key" in schema.lower()
        has_relationships = "ref" in schema.lower() or "foreign" in schema.lower()
        line_count = len(schema.split("\n"))
        
        if target_db == "mongodb":
            reads = "O(1)" if has_indexes else "O(N)"
            writes = "O(log N)" if has_indexes else "O(1)"
            complexity = "Low" if line_count < 50 else "Medium" if line_count < 150 else "High"
        elif target_db == "cassandra":
            reads = "O(1)" if "partition" in schema.lower() else "O(N)"
            writes = "O(1)"
            complexity = "Low" if not has_relationships else "Medium"
        elif target_db == "neo4j":
            reads = "O(log N)"
            writes = "O(log N)"
            complexity = "Medium" if has_relationships else "Low"
        else:
            reads = "O(1)"
            writes = "O(1)"
            complexity = "Medium"
        
        state["stats"] = {
            "reads": reads,
            "writes": writes,
            "complexity": complexity,
        }
        
        return state

    def _score_conversion(self, state: ConversionState) -> ConversionState:
        """Score the conversion quality - with fast fallback."""
        # Use a simple heuristic score instead of LLM to speed up
        base_score = 75
        
        # Bonus for having stats
        if state.get("stats") and state["stats"].get("complexity"):
            complexity = state["stats"]["complexity"].lower()
            if complexity == "low":
                base_score += 15
            elif complexity == "medium":
                base_score += 10
            else:
                base_score += 5
        
        # Bonus for having explanation
        if state.get("explanation") and len(state["explanation"]) > 50:
            base_score += 5
        
        # Penalty for warnings
        warning_count = len(state.get("warnings", []))
        base_score -= min(warning_count * 3, 15)
        
        state["score"] = max(60, min(95, base_score))
        return state

    def enhance_conversion(self, sql_schema: str, converted_schema: str, target_db: str) -> Dict[str, Any]:
        """Enhance a schema conversion using LangGraph workflow."""
        if not self.llm:
            return self._get_fallback_enhancement(target_db)

        try:
            initial_state: ConversionState = {
                "sql_schema": sql_schema,
                "target_db": target_db,
                "converted_schema": converted_schema,
                "explanation": "",
                "warnings": [],
                "stats": {},
                "score": 0,
                "error": None,
            }

            final_state = self.graph.invoke(initial_state)
            return {
                "explanation": final_state["explanation"],
                "warnings": final_state["warnings"],
                "stats": final_state["stats"],
                "score": final_state["score"],
            }

        except Exception as e:
            print(f"LangGraph enhancement failed: {e}")
            return self._get_fallback_enhancement(target_db)

    def translate_query(self, sql_query: str, target_db: str, schema_context: Optional[str] = None) -> Dict[str, Any]:
        """Translate SQL query to target database query language."""
        if not self.llm:
            return self._get_fallback_translation(target_db)

        try:
            db_languages = {
                "mongodb": "MongoDB Query Language (MQL)",
                "cassandra": "Cassandra Query Language (CQL)",
                "neo4j": "Neo4j Cypher",
            }

            target_language = db_languages.get(target_db, "target database language")
            schema_part = f"\n\nSchema Context:\n{schema_context}" if schema_context else ""

            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=f"You are an expert in SQL and {target_language}."),
                HumanMessage(
                    content=(
                        f"Translate this SQL query to {target_language}.\n\n"
                        f"SQL Query:\n{sql_query}{schema_part}\n\n"
                        "Respond in JSON format:\n"
                        "{\n"
                        "  \"translated_query\": \"the translated query\",\n"
                        "  \"explanation\": \"explanation of translation decisions\",\n"
                        "  \"warnings\": [\"warning1\", \"warning2\"]\n"
                        "}"
                    )
                ),
            ])

            content = self._invoke_prompt(prompt)
            data = self._extract_json_payload(content)
            return {
                "translated_query": data.get("translated_query", ""),
                "explanation": data.get("explanation", ""),
                "warnings": data.get("warnings", []),
            }

        except Exception as e:
            print(f"Query translation failed: {e}")
            return self._get_fallback_translation(target_db)

    def _get_fallback_enhancement(self, target_db: str) -> Dict[str, Any]:
        """Return fallback enhancement when LLM is unavailable."""
        return {
            "explanation": (
                f"## Overview\n"
                f"Schema converted to {target_db.upper()} successfully, but Ollama is unavailable.\n\n"
                "## Design Decisions\n"
                "- Converter used default mapping strategy based on SQL structure.\n"
                "- Keys and indexes were generated using deterministic rules.\n"
                "- No model-based optimization feedback is included.\n\n"
                "## Why This Works\n"
                "- Output remains valid for baseline migration scenarios.\n"
                "- Structure can be refined after workload testing.\n"
                "- Deterministic mapping keeps behavior predictable.\n\n"
                "## Validation Checklist\n"
                "- Start Ollama and verify model availability.\n"
                "- Re-run conversion to get AI reasoning and warnings.\n"
                "- Confirm indexes and key choices against real queries."
            ),
            "warnings": ["Ollama is not reachable. AI-enhanced guidance is unavailable."],
            "stats": {"reads": "O(1)", "writes": "O(1)", "complexity": "Medium"},
            "score": 85,
        }

    def _get_fallback_translation(self, target_db: str) -> Dict[str, Any]:
        """Return fallback translation when LLM is unavailable."""
        return {
            "translated_query": f"-- Translation to {target_db} requires manual review",
            "explanation": "Automatic translation unavailable because Ollama is not reachable.",
            "warnings": ["Manual review required", "Start Ollama and retry translation"],
        }