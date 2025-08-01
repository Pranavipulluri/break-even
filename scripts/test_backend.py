#!/usr/bin/env python3
"""
Test script to verify backend API connectivity
"""

import requests
import sys

def test_backend_connectivity():
    """Test if the backend API is accessible"""
    
    base_urls = [
        'http://localhost:5000',
        'http://127.0.0.1:5000'
    ]
    
    test_endpoints = [
        '/',
        '/api/auth/register',  # Should return method not allowed for GET
        '/api/dashboard/stats'  # Should return 401 for unauthorized
    ]
    
    print("🔍 Testing Backend API Connectivity...")
    print("=" * 50)
    
    for base_url in base_urls:
        print(f"\n📡 Testing base URL: {base_url}")
        
        # Test basic connectivity
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            print(f"   ✅ Root endpoint: Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Root endpoint: Connection failed - {e}")
            continue
        
        # Test API endpoints
        for endpoint in test_endpoints[1:]:  # Skip root endpoint
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                print(f"   ✅ {endpoint}: Status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"   ❌ {endpoint}: Connection failed - {e}")
    
    print("\n" + "=" * 50)
    print("🧪 Testing CORS Configuration...")
    
    # Test CORS with frontend origin
    try:
        headers = {
            'Origin': 'http://localhost:3001',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options('http://localhost:5000/api/auth/register', 
                                  headers=headers, timeout=5)
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        print("CORS Headers received:")
        for header, value in cors_headers.items():
            print(f"   {header}: {value}")
        
        if cors_headers['Access-Control-Allow-Origin']:
            print("   ✅ CORS is configured")
        else:
            print("   ❌ CORS might not be configured correctly")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ CORS test failed: {e}")

def test_simple_api_call():
    """Test a simple API call that might be used by frontend"""
    print("\n🔄 Testing API call similar to what frontend might make...")
    
    try:
        # Test a POST request to register (should fail with validation error)
        response = requests.post('http://localhost:5000/api/auth/register', 
                               json={}, 
                               headers={'Content-Type': 'application/json'},
                               timeout=5)
        
        print(f"   Registration endpoint test: Status {response.status_code}")
        if response.status_code == 400:
            print("   ✅ Endpoint is responding (400 = validation error is expected)")
        
        try:
            data = response.json()
            print(f"   Response: {data}")
        except:
            print(f"   Response text: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ API call failed: {e}")

if __name__ == "__main__":
    try:
        test_backend_connectivity()
        test_simple_api_call()
        
        print("\n" + "=" * 50)
        print("💡 Recommendations:")
        print("1. Make sure backend is running: python run.py")
        print("2. Start frontend: npm start (should use PORT=3001 from .env)")
        print("3. Check browser console for any JavaScript errors")
        print("4. Verify Network tab in browser dev tools for failed requests")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test script error: {e}")
        sys.exit(1)
