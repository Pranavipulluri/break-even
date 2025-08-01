#!/usr/bin/env python3
"""
Test all API integrations
"""

import requests
import json
from app.config import Config

def test_gemini_api():
    """Test Gemini AI API"""
    print("🤖 Testing Gemini AI API...")
    
    try:
        api_key = Config.GEMINI_API_KEY
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{
                    "text": "Say 'Hello, Gemini AI is working!' in a friendly way."
                }]
            }]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result:
                content = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ Gemini AI: {content}")
                return True
        
        print(f"❌ Gemini AI failed: {response.status_code} - {response.text}")
        return False
        
    except Exception as e:
        print(f"❌ Gemini AI error: {e}")
        return False

def test_github_api():
    """Test GitHub API"""
    print("🐙 Testing GitHub API...")
    
    try:
        token = Config.GITHUB_TOKEN
        url = "https://api.github.com/user"
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ GitHub API: Connected as {user_data.get('login', 'Unknown')}")
            return True
        
        print(f"❌ GitHub API failed: {response.status_code} - {response.text}")
        return False
        
    except Exception as e:
        print(f"❌ GitHub API error: {e}")
        return False

def test_netlify_api():
    """Test Netlify API"""
    print("🚀 Testing Netlify API...")
    
    try:
        api_key = Config.NETLIFY_API_KEY
        url = "https://api.netlify.com/api/v1/sites"
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            sites = response.json()
            print(f"✅ Netlify API: Connected (Found {len(sites)} sites)")
            return True
        
        print(f"❌ Netlify API failed: {response.status_code} - {response.text}")
        return False
        
    except Exception as e:
        print(f"❌ Netlify API error: {e}")
        return False

def main():
    """Test all APIs"""
    print("🧪 Testing API Integrations...")
    print("=" * 50)
    
    results = {
        'gemini': test_gemini_api(),
        'github': test_github_api(),
        'netlify': test_netlify_api()
    }
    
    print("\n📊 Results Summary:")
    print("=" * 50)
    
    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service.upper()}: {'Working' if status else 'Failed'}")
    
    working_count = sum(results.values())
    print(f"\n🎯 {working_count}/3 APIs are working correctly")
    
    if working_count == 3:
        print("\n🎉 All APIs ready! You can now use the AI website builder!")
    else:
        print("\n⚠️  Some APIs need attention. Check the errors above.")

if __name__ == "__main__":
    main()
