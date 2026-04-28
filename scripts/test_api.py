#!/usr/bin/env python3
"""
Quick test script for the SQL Conversion Platform API
Tests both Groq and Ollama configurations
"""

import requests
import json
import sys

API_BASE = "http://localhost:8000"

def test_health():
    """Test API health and AI provider status"""
    print("🔍 Testing API Health...")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data['status']}")
            print(f"🤖 AI Provider: {data['ai_provider']}")
            print(f"🧠 AI Available: {data['ai_available']}")
            return data['ai_available']
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the backend running?")
        print("   Run: docker-compose up -d")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_simple_conversion():
    """Test a simple SQL conversion"""
    print("\n📝 Testing Simple SQL Conversion...")
    
    sql = """
    CREATE TABLE users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        email VARCHAR(255) UNIQUE NOT NULL,
        username VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    payload = {
        "sql": sql,
        "target_databases": ["mongodb"],
        "include_ai_explanation": True
    }
    
    try:
        print("   Sending conversion request...")
        response = requests.post(
            f"{API_BASE}/api/convert",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'mongodb' in data:
                mongo = data['mongodb']
                print("\n✅ MongoDB Conversion Successful!")
                print("\n📄 Schema:")
                print(mongo['schema'][:300] + "..." if len(mongo['schema']) > 300 else mongo['schema'])
                
                print(f"\n🤖 AI Explanation:")
                print(f"   {mongo['explanation'][:200]}...")
                
                print(f"\n📊 Stats:")
                print(f"   Reads: {mongo['stats']['reads']}")
                print(f"   Writes: {mongo['stats']['writes']}")
                print(f"   Complexity: {mongo['stats']['complexity']}")
                print(f"   Score: {mongo['score']}/100")
                
                if mongo['warnings']:
                    print(f"\n⚠️  Warnings:")
                    for warning in mongo['warnings']:
                        print(f"   - {warning}")
                
                return True
            else:
                print("❌ No MongoDB result in response")
                return False
        else:
            print(f"❌ Conversion failed with status code: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out. AI provider might be slow or unavailable.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_query_translation():
    """Test SQL query translation"""
    print("\n🔄 Testing Query Translation...")
    
    payload = {
        "sql_query": "SELECT * FROM users WHERE email = 'john@example.com'",
        "target_database": "mongodb"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/translate-query",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Query Translation Successful!")
            print(f"\n📝 Original SQL:")
            print(f"   {data['original_sql']}")
            print(f"\n🔄 Translated to MongoDB:")
            print(f"   {data['translated_query']}")
            print(f"\n💡 Explanation:")
            print(f"   {data['explanation'][:200]}...")
            return True
        else:
            print(f"❌ Translation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_complex_schema():
    """Test with a more complex schema"""
    print("\n🏗️  Testing Complex Schema (E-commerce)...")
    
    sql = """
    CREATE TABLE users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        email VARCHAR(255) UNIQUE NOT NULL,
        username VARCHAR(100) NOT NULL
    );
    
    CREATE TABLE orders (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        total DECIMAL(10, 2) NOT NULL,
        status ENUM('pending', 'shipped', 'delivered'),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    
    CREATE TABLE order_items (
        id INT PRIMARY KEY AUTO_INCREMENT,
        order_id INT NOT NULL,
        product_name VARCHAR(255) NOT NULL,
        quantity INT NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id)
    );
    """
    
    payload = {
        "sql": sql,
        "target_databases": ["mongodb", "cassandra", "neo4j"],
        "include_ai_explanation": True
    }
    
    try:
        print("   Converting to all 3 databases...")
        response = requests.post(
            f"{API_BASE}/api/convert",
            json=payload,
            timeout=45
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Multi-Database Conversion Successful!")
            
            for db in ['mongodb', 'cassandra', 'neo4j']:
                if db in data:
                    print(f"\n📦 {db.upper()}:")
                    print(f"   Score: {data[db]['score']}/100")
                    print(f"   Complexity: {data[db]['stats']['complexity']}")
            
            if 'metadata' in data:
                print(f"\n📊 Metadata:")
                print(f"   Tables: {data['metadata']['table_count']}")
                print(f"   Relationships: {data['metadata']['relationship_count']}")
            
            return True
        else:
            print(f"❌ Conversion failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 SQL Conversion Platform - API Test Suite")
    print("=" * 60)
    
    # Test 1: Health Check
    ai_available = test_health()
    
    if not ai_available:
        print("\n⚠️  AI provider is not available.")
        print("   The API will work but without AI explanations.")
        print("\n💡 To enable AI:")
        print("   1. For Groq: Add GROQ_API_KEY to backend/.env")
        print("   2. For Ollama: Run 'ollama serve' and set AI_PROVIDER=ollama")
        response = input("\n   Continue testing without AI? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Test 2: Simple Conversion
    test_simple_conversion()
    
    # Test 3: Query Translation
    if ai_available:
        test_query_translation()
    
    # Test 4: Complex Schema
    test_complex_schema()
    
    print("\n" + "=" * 60)
    print("✅ Testing Complete!")
    print("=" * 60)
    print("\n💡 Next Steps:")
    print("   1. Open http://localhost:3000 to use the web interface")
    print("   2. Check API docs at http://localhost:8000/docs")
    print("   3. Try the example schemas in examples/ folder")

if __name__ == "__main__":
    main()
