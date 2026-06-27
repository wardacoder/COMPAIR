"""
Quick test script to verify your Groq API key works.
"""
import os
import sys

try:
    from groq import Groq
except ImportError:
    print("❌ Groq library not installed. Run: pip install groq")
    sys.exit(1)

# Get API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ GROQ_API_KEY not set!")
    print("\nSet it with:")
    print("  $env:GROQ_API_KEY = 'your-key-here'")
    sys.exit(1)

# Clean and validate
api_key = api_key.strip()
print(f"🔑 Testing API key: {api_key[:10]}...")

if not api_key.startswith("gsk_"):
    print(f"❌ Invalid format! Key should start with 'gsk_'")
    print(f"   Your key starts with: '{api_key[:4] if len(api_key) >= 4 else 'empty'}'")
    sys.exit(1)

# Test the key
try:
    client = Groq(api_key=api_key)
    
    # Make a simple test call
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": "Say 'Hello' if you can read this."}
        ],
        max_tokens=10
    )
    
    print("✅ API key is valid!")
    print(f"✅ Response: {response.choices[0].message.content}")
    print("\n🎉 You're ready to use grok_mcp_client.py!")
    
except Exception as e:
    error_msg = str(e)
    if "401" in error_msg or "invalid_api_key" in error_msg.lower():
        print("❌ Invalid API Key!")
        print("\nPossible issues:")
        print("  1. Key is incorrect or expired")
        print("  2. Key wasn't copied completely")
        print("  3. Key has been revoked")
        print("\nFix:")
        print("  1. Go to: https://console.groq.com/keys")
        print("  2. Create a NEW API key")
        print("  3. Copy it COMPLETELY")
        print("  4. Set it: $env:GROQ_API_KEY = 'your-complete-key-here'")
    else:
        print(f"❌ Error: {error_msg}")






