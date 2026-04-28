#!/usr/bin/env python3
"""Quick test to verify Groq API key works"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

print("🔍 Testing Groq API Key...")
print(f"   Key: {GROQ_API_KEY[:20]}..." if GROQ_API_KEY else "   ❌ No key found")

if not GROQ_API_KEY:
    print("\n❌ GROQ_API_KEY not found in backend/.env")
    print("   Please add your Groq API key to backend/.env")
    exit(1)

try:
    from groq import Groq
    
    print("\n✅ Groq library installed")
    print("   Testing API connection...")
    
    client = Groq(api_key=GROQ_API_KEY)
    
    # Test with a simple prompt
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, SQL Converter!' in one sentence."}
        ],
        max_tokens=50
    )
    
    print(f"\n✅ Groq API is working!")
    print(f"   Response: {response.choices[0].message.content}")
    print(f"\n🎉 Your Groq setup is ready!")
    print(f"\n💡 Next steps:")
    print(f"   1. Start the backend: docker-compose up -d --build")
    print(f"   2. Run full tests: python test_api.py")
    print(f"   3. Open web UI: http://localhost:3000")
    
except ImportError:
    print("\n⚠️  Groq library not installed")
    print("   Installing now...")
    import subprocess
    subprocess.run(["pip", "install", "groq"])
    print("   ✅ Installed! Run this script again.")
    
except Exception as e:
    print(f"\n❌ Error testing Groq API: {e}")
    print("\n💡 Possible issues:")
    print("   1. Invalid API key")
    print("   2. Network connection problem")
    print("   3. Groq service temporarily unavailable")
    print("\n   Get a new key at: https://console.groq.com")
