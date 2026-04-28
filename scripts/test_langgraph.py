"""Test script for LangGraph AI enhancement with LLM."""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Change to backend directory to load .env file
os.chdir(backend_path)

from ai.langgraph_enhancer import LangGraphAIEnhancer
from config import settings

# Test SQL schema
TEST_SQL = """
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    status ENUM('pending', 'shipped', 'delivered'),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

# Test MongoDB conversion
MONGODB_SCHEMA = """
// MongoDB Collection Schema
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "username"],
      properties: {
        _id: { bsonType: "objectId" },
        email: { bsonType: "string" },
        username: { bsonType: "string" },
        orders: { bsonType: "array" },
        createdAt: { bsonType: "date" }
      }
    }
  }
});

db.users.createIndex({ "email": 1 }, { unique: true });
"""


def test_llm_connection():
    """Test LLM connection and initialization."""
    print("=" * 60)
    print("Testing LLM Connection")
    print("=" * 60)
    
    print(f"\nCurrent directory: {os.getcwd()}")
    print(f"AI Provider: {settings.ai_provider}")
    
    # Debug: Show actual key values (masked)
    groq_key = settings.groq_api_key
    openai_key = settings.openai_api_key
    
    if groq_key:
        print(f"Groq API Key: ✓ Configured ({groq_key[:10]}...{groq_key[-4:]})")
    else:
        print(f"Groq API Key: ✗ Not configured")
    
    if openai_key:
        print(f"OpenAI API Key: ✓ Configured ({openai_key[:10]}...{openai_key[-4:]})")
    else:
        print(f"OpenAI API Key: ✗ Not configured")
    
    enhancer = LangGraphAIEnhancer()
    
    if enhancer.llm:
        print(f"\n✓ LLM initialized successfully!")
        print(f"  Type: {type(enhancer.llm).__name__}")
        return enhancer
    else:
        print("\n✗ LLM initialization failed!")
        print("  Please check your API keys in backend/.env")
        return None


def test_mongodb_enhancement(enhancer):
    """Test MongoDB conversion enhancement."""
    print("\n" + "=" * 60)
    print("Testing MongoDB Enhancement with LangGraph")
    print("=" * 60)
    
    try:
        result = enhancer.enhance_conversion(
            sql_schema=TEST_SQL,
            converted_schema=MONGODB_SCHEMA,
            target_db='mongodb'
        )
        
        print("\n✓ Enhancement completed!")
        print(f"\nExplanation:\n{result['explanation'][:200]}...")
        print(f"\nWarnings: {result['warnings']}")
        print(f"\nStats: {result['stats']}")
        print(f"\nScore: {result['score']}/100")
        
        return True
    
    except Exception as e:
        print(f"\n✗ Enhancement failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_translation(enhancer):
    """Test SQL query translation."""
    print("\n" + "=" * 60)
    print("Testing Query Translation")
    print("=" * 60)
    
    test_query = "SELECT * FROM users WHERE email = 'test@example.com'"
    
    try:
        result = enhancer.translate_query(
            sql_query=test_query,
            target_db='mongodb',
            schema_context=MONGODB_SCHEMA
        )
        
        print("\n✓ Translation completed!")
        print(f"\nOriginal SQL:\n{test_query}")
        print(f"\nTranslated Query:\n{result['translated_query']}")
        print(f"\nExplanation:\n{result['explanation'][:200]}...")
        print(f"\nWarnings: {result['warnings']}")
        
        return True
    
    except Exception as e:
        print(f"\n✗ Translation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_langgraph_workflow(enhancer):
    """Test the LangGraph workflow structure."""
    print("\n" + "=" * 60)
    print("Testing LangGraph Workflow")
    print("=" * 60)
    
    try:
        # Check if graph is compiled
        if enhancer.graph:
            print("\n✓ LangGraph workflow compiled successfully!")
            
            # Get graph structure
            nodes = list(enhancer.graph.nodes.keys()) if hasattr(enhancer.graph, 'nodes') else []
            print(f"\nWorkflow nodes: {len(nodes)}")
            
            # Expected nodes
            expected_nodes = [
                "analyze_schema",
                "generate_explanation",
                "identify_warnings",
                "calculate_stats",
                "score_conversion"
            ]
            
            print("\nExpected workflow steps:")
            for i, node in enumerate(expected_nodes, 1):
                print(f"  {i}. {node}")
            
            return True
        else:
            print("\n✗ LangGraph workflow not compiled!")
            return False
    
    except Exception as e:
        print(f"\n✗ Workflow test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("LangGraph AI Enhancement Test Suite")
    print("=" * 60)
    
    # Test 1: LLM Connection
    enhancer = test_llm_connection()
    if not enhancer:
        print("\n" + "=" * 60)
        print("TESTS FAILED: LLM not initialized")
        print("=" * 60)
        print("\nPlease configure your AI provider:")
        print("1. Edit backend/.env")
        print("2. Set AI_PROVIDER=groq (or openai)")
        print("3. Set GROQ_API_KEY=your_key_here")
        return
    
    # Test 2: LangGraph Workflow
    workflow_ok = test_langgraph_workflow(enhancer)
    
    # Test 3: MongoDB Enhancement
    mongodb_ok = test_mongodb_enhancement(enhancer)
    
    # Test 4: Query Translation
    translation_ok = test_query_translation(enhancer)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"LLM Connection:      {'✓ PASS' if enhancer else '✗ FAIL'}")
    print(f"LangGraph Workflow:  {'✓ PASS' if workflow_ok else '✗ FAIL'}")
    print(f"MongoDB Enhancement: {'✓ PASS' if mongodb_ok else '✗ FAIL'}")
    print(f"Query Translation:   {'✓ PASS' if translation_ok else '✗ FAIL'}")
    
    all_passed = enhancer and workflow_ok and mongodb_ok and translation_ok
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60)


if __name__ == "__main__":
    main()
