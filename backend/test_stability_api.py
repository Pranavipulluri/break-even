import requests

# Test Stability AI API key
api_key = "sk-Ci8STOuJz4ZE1xGzmQXFDoykscMoNFoD4OCQZr5BlWgd83O2"
base_url = "https://api.stability.ai"

print("🔑 Testing Stability AI API key...")
print(f"Key: {api_key[:20]}...")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

try:
    # Test with engines endpoint
    print("📡 Testing connection to Stability AI...")
    response = requests.get(
        f"{base_url}/v1/engines/list",
        headers=headers,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}...")
    
    if response.status_code == 200:
        print("✅ API key is working!")
        engines = response.json()
        print(f"Available engines: {len(engines)}")
    else:
        print("❌ API key test failed")
        
except Exception as e:
    print(f"❌ Error testing API: {e}")
