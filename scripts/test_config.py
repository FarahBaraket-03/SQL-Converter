"""Quick test to verify .env file is loading correctly."""
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

print(f"Backend path: {backend_path}")
print(f"Current directory: {os.getcwd()}")

# Check if .env file exists
env_file = os.path.join(backend_path, '.env')
print(f"\n.env file path: {env_file}")
print(f".env file exists: {os.path.exists(env_file)}")

if os.path.exists(env_file):
    print("\n.env file contents:")
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Mask API keys
                if 'API_KEY' in line and '=' in line:
                    key, value = line.split('=', 1)
                    if value:
                        print(f"  {key}={value[:10]}...{value[-4:]}")
                    else:
                        print(f"  {key}=(empty)")
                else:
                    print(f"  {line}")

print("\n" + "="*60)
print("Loading config...")
print("="*60)

from config import settings

print(f"\nSettings loaded:")
print(f"  AI Provider: {settings.ai_provider}")
print(f"  Groq API Key: {settings.groq_api_key[:10] + '...' + settings.groq_api_key[-4:] if settings.groq_api_key else '(not set)'}")
print(f"  OpenAI API Key: {settings.openai_api_key[:10] + '...' + settings.openai_api_key[-4:] if settings.openai_api_key else '(not set)'}")
print(f"  Ollama Base URL: {settings.ollama_base_url}")
print(f"  Ollama Model: {settings.ollama_model}")

print("\n" + "="*60)
if settings.groq_api_key:
    print("✓ Configuration loaded successfully!")
else:
    print("✗ Configuration failed - API key not loaded")
print("="*60)
