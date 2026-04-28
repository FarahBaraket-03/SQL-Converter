"""Test script to verify BlazeAPI integration."""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from openai import OpenAI
from config import settings

def test_blazeapi_direct():
    """Test BlazeAPI directly with OpenAI SDK."""
    print("=" * 60)
    print("🧪 Testing BlazeAPI Direct Connection")
    print("=" * 60)
    
    print(f"\n📋 Configuration:")
    print(f"   Provider: {settings.ai_provider}")
    print(f"   API Key: {settings.blazeapi_api_key[:20]}..." if settings.blazeapi_api_key else "   API Key: NOT SET")
    print(f"   Base URL: {settings.blazeapi_base_url}")
    print(f"   Model: {settings.blazeapi_model}")
    
    if not settings.blazeapi_api_key or settings.blazeapi_api_key == "your_blaze_api_key_here":
        print("\n❌ ERROR: BlazeAPI key not configured!")
        print("   Please set BLAZEAPI_API_KEY in backend/.env")
        return False
    
    try:
        print("\n🔌 Connecting to BlazeAPI...")
        client = OpenAI(
            api_key=settings.blazeapi_api_key,
            base_url=settings.blazeapi_base_url,
        )
        
        print("📤 Sending test message...")
        response = client.chat.completions.create(
            model=settings.blazeapi_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello from BlazeAPI!' in one sentence."}
            ],
            temperature=0.3,
        )
        
        print("✅ Response received!")
        print(f"\n💬 Response:")
        print(f"   {response.choices[0].message.content}")
        
        print(f"\n📊 Metadata:")
        print(f"   Model: {response.model}")
        print(f"   Tokens: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"   Type: {type(e).__name__}")
        return False


def test_langgraph_integration():
    """Test BlazeAPI through LangGraph enhancer."""
    print("\n" + "=" * 60)
    print("🧪 Testing LangGraph Integration")
    print("=" * 60)
    
    try:
        from ai.langgraph_enhancer import LangGraphAIEnhancer
        
        print("\n🔧 Initializing LangGraph enhancer...")
        enhancer = LangGraphAIEnhancer()
        
        if not enhancer.llm:
            print("❌ ERROR: LLM not initialized!")
            return False
        
        print(f"✅ LLM initialized with provider: {enhancer.provider}")
        
        print("\n📤 Testing simple enhancement...")
        test_sql = """
        CREATE TABLE users (
            id INT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(255)
        );
        """
        
        test_converted = """
        db.users.insertOne({
            _id: 1,
            name: "John Doe",
            email: "john@example.com"
        })
        """
        
        result = enhancer.enhance_conversion(
            sql_schema=test_sql,
            converted_schema=test_converted,
            target_db='mongodb'
        )
        
        print("✅ Enhancement completed!")
        print(f"\n📝 Explanation (first 200 chars):")
        print(f"   {result['explanation'][:200]}...")
        print(f"\n⚠️  Warnings: {len(result['warnings'])}")
        print(f"📊 Stats: {result['stats']}")
        print(f"⭐ Score: {result['score']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"   Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoint():
    """Test the FastAPI endpoint."""
    print("\n" + "=" * 60)
    print("🧪 Testing FastAPI Endpoint")
    print("=" * 60)
    
    try:
        import requests
        
        print("\n🔍 Checking API health...")
        response = requests.get("http://localhost:8000/")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API is healthy!")
            print(f"   Status: {data['status']}")
            print(f"   Provider: {data['ai_provider']}")
            print(f"   AI Available: {data['ai_available']}")
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
        
        print("\n📤 Testing conversion endpoint...")
        test_request = {
            "sql": "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100));",
            "target_databases": ["mongodb"],
            "input_method": "manual",
            "include_ai_explanation": True
        }
        
        response = requests.post(
            "http://localhost:8000/api/convert",
            json=test_request,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Conversion successful!")
            
            if data.get('mongodb'):
                mongo = data['mongodb']
                print(f"\n📝 MongoDB Schema (first 100 chars):")
                print(f"   {mongo['schema'][:100]}...")
                print(f"\n💬 Explanation (first 150 chars):")
                print(f"   {mongo['explanation'][:150]}...")
                print(f"\n⭐ Score: {mongo['score']}")
            
            return True
        else:
            print(f"❌ Conversion failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API")
        print("   Make sure the backend is running:")
        print("   cd backend && python -m uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"   Type: {type(e).__name__}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🚀 BlazeAPI Integration Test Suite")
    print("=" * 60)
    
    results = {
        "Direct Connection": test_blazeapi_direct(),
        "LangGraph Integration": test_langgraph_integration(),
        "API Endpoint": test_api_endpoint(),
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! BlazeAPI is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
