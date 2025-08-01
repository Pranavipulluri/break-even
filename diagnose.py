#!/usr/bin/env python3
"""
Diagnose and fix CORS/Backend issues for Break-even app
"""

import subprocess
import time
import requests
import os
import sys

def check_backend_running():
    """Check if backend is running on port 5000"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def check_frontend_running():
    """Check if frontend is running on port 3001"""
    try:
        response = requests.get("http://localhost:3001", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    print("🔍 Diagnosing Break-even app issues...")
    print("=" * 50)
    
    # Check backend
    if check_backend_running():
        print("✅ Backend is running on port 5000")
    else:
        print("❌ Backend is NOT running on port 5000")
        print("   To start backend:")
        print("   1. Open Command Prompt")
        print("   2. Navigate to: break-even\\backend")
        print("   3. Run: python run.py")
        print("   Or double-click: start-backend.bat")
        print()
    
    # Check frontend
    if check_frontend_running():
        print("✅ Frontend is running on port 3001")
    else:
        print("❌ Frontend is NOT running on port 3001") 
        print("   To start frontend:")
        print("   1. Open Command Prompt")
        print("   2. Navigate to: break-even\\frontend")
        print("   3. Run: npm start")
        print("   Or double-click: start-frontend.bat")
        print()
    
    # Test CORS if both are running
    if check_backend_running() and check_frontend_running():
        print("🧪 Testing CORS...")
        try:
            response = requests.options("http://localhost:5000/auth/register",
                                      headers={
                                          'Origin': 'http://localhost:3001',
                                          'Access-Control-Request-Method': 'POST',
                                          'Access-Control-Request-Headers': 'Content-Type'
                                      })
            if response.status_code in [200, 204]:
                print("✅ CORS is working correctly")
            else:
                print(f"❌ CORS preflight failed: {response.status_code}")
        except Exception as e:
            print(f"❌ CORS test failed: {e}")
    
    print()
    print("📋 Summary:")
    print("- Frontend should run on: http://localhost:3001")
    print("- Backend should run on: http://localhost:5000") 
    print("- Both need to be running for the app to work")
    print()
    print("🔧 If you're still having issues:")
    print("1. Make sure both servers are running")
    print("2. Check Windows Firewall isn't blocking the ports")
    print("3. Try refreshing the browser page")

if __name__ == "__main__":
    main()
