#!/usr/bin/env python3
"""
Test CORS and backend connectivity
"""

import requests
import json

def test_backend():
    """Test if backend is running and CORS is working"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing backend connectivity...")
    
    try:
        # Test basic connectivity
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Backend health check: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not responding: {e}")
        return False
    
    try:
        # Test OPTIONS request (preflight)
        response = requests.options(f"{base_url}/auth/register", 
                                  headers={
                                      'Origin': 'http://localhost:3001',
                                      'Access-Control-Request-Method': 'POST',
                                      'Access-Control-Request-Headers': 'Content-Type'
                                  },
                                  timeout=5)
        print(f"✅ CORS preflight test: {response.status_code}")
        print(f"CORS headers: {dict(response.headers)}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS preflight failed: {e}")
        return False
    
    try:
        # Test actual POST request
        test_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User"
        }
        
        response = requests.post(f"{base_url}/auth/register", 
                               json=test_data,
                               headers={
                                   'Origin': 'http://localhost:3001',
                                   'Content-Type': 'application/json'
                               },
                               timeout=5)
        
        print(f"✅ POST request test: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ POST request failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_backend()
