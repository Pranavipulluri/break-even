#!/usr/bin/env python3
"""
Comprehensive integration test script to verify all API keys and services
"""

import os
import sys
import io
import requests
import json
from dotenv import load_dotenv

# Fix Windows console encoding for Unicode (Telugu/Hindi)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add backend path to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
backend_path = os.path.join(project_root, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Load environment variables
dotenv_path = os.path.join(backend_path, '.env')
print(f"[INFO] Loading environment from: {dotenv_path}")
load_dotenv(dotenv_path)

def test_mongodb():
    print("\n[TEST] Testing MongoDB Connectivity...")
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/breakeven")
    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        # Trigger connection
        client.server_info()
        print("   [OK] MongoDB is running and connected successfully!")
        return True
    except Exception as e:
        print(f"   [FAIL] MongoDB connection failed: {e}")
        print("      (Make sure MongoDB is running on port 27017)")
        return False

def test_gemini():
    print("\n[TEST] Testing Google Gemini AI Service...")
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("   [FAIL] GEMINI_API_KEY is not set in .env")
        return False
    
    try:
        from app.services.gemini_service import GeminiAIService
        # Instantiate service
        service = GeminiAIService(api_key=gemini_key)
        prompt = "Say 'Gemini is online!' and nothing else."
        result = service.generate_content(prompt)
        
        if result.get('success'):
            print(f"   [OK] Gemini response: \"{result.get('content').strip()}\"")
            return True
        else:
            print(f"   [FAIL] Gemini call failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"   [FAIL] Gemini service instantiation/call error: {e}")
        return False

def test_groq():
    print("\n[TEST] Testing Groq AI Service...")
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("   [FAIL] GROQ_API_KEY is not set in .env")
        return False
    
    try:
        from app.services.groq_service import GroqService
        service = GroqService(api_key=groq_key)
        result = service.test_connection()
        
        if result.get('success'):
            print(f"   [OK] Groq Connection: {result.get('message')}")
            return True
        else:
            print(f"   [FAIL] Groq call failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"   [FAIL] Groq service error: {e}")
        return False

def test_stability():
    print("\n[TEST] Testing Stability AI Service...")
    stability_key = os.getenv("STABILITY_API_KEY")
    if not stability_key:
        print("   [FAIL] STABILITY_API_KEY is not set in .env")
        return False
    
    try:
        from app.services.stability_service import StabilityService
        service = StabilityService()
        # Ensure it has our key (StabilityService reads from env directly)
        os.environ['STABILITY_API_KEY'] = stability_key
        result = service.test_connection()
        
        if result.get('success'):
            print(f"   [OK] Stability AI Connection: {result.get('message')}")
            return True
        else:
            print(f"   [FAIL] Stability AI call failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"   [FAIL] Stability AI service error: {e}")
        return False

def test_netlify():
    print("\n[TEST] Testing Netlify API Integration...")
    netlify_key = os.getenv("NETLIFY_API_KEY")
    if not netlify_key:
        print("   [FAIL] NETLIFY_API_KEY is not set in .env")
        return False
    
    try:
        url = "https://api.netlify.com/api/v1/sites"
        headers = {
            'Authorization': f'Bearer {netlify_key}',
            'Content-Type': 'application/json'
        }
        # Request with limit 1 to verify credentials quickly
        response = requests.get(url, headers=headers, params={'per_page': 1}, timeout=10)
        
        if response.status_code == 200:
            sites = response.json()
            site_count = len(sites)
            print(f"   [OK] Netlify API connection successful! Token is valid. (Found {site_count} site preview)")
            return True
        else:
            print(f"   [FAIL] Netlify API validation failed: Status {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   [FAIL] Netlify integration test error: {e}")
        return False

def test_github():
    print("\n[TEST] Testing GitHub API Integration...")
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("   [FAIL] GITHUB_TOKEN is not set in .env")
        return False
    
    try:
        url = "https://api.github.com/user"
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   [OK] GitHub API connection successful! User: @{user_data.get('login')} ({user_data.get('name')})")
            return True
        else:
            print(f"   [FAIL] GitHub API validation failed: Status {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   [FAIL] GitHub integration test error: {e}")
        return False

def test_email():
    print("\n[TEST] Testing Email Campaign SMTP Connection...")
    gmail_email = os.getenv("GMAIL_EMAIL")
    gmail_pwd = os.getenv("GMAIL_APP_PASSWORD")
    if not gmail_email or not gmail_pwd:
        print("   [FAIL] GMAIL_EMAIL or GMAIL_APP_PASSWORD is not set in .env")
        return False
    
    try:
        from app.services.email_service import EmailService
        service = EmailService()
        result = service.test_connection()
        
        if result.get('success'):
            print(f"   [OK] Email SMTP Connection: {result.get('message')} (Sender: {result.get('sender_email')})")
            return True
        else:
            print(f"   [FAIL] Email SMTP call failed: {result.get('error')}")
            if result.get('help'):
                print(f"      Help: {result.get('help')}")
            return False
    except Exception as e:
        print(f"   [FAIL] Email service error: {e}")
        return False

def test_translation():
    print("\n[TEST] Testing Translation Service...")
    try:
        from app.services.translation_service import TranslationService
        service = TranslationService()
        test_text = "Welcome to our law firm! We are here to help you."
        
        print("   Translating to Telugu (te)...")
        te_translation = service.translate_text(test_text, target_lang='te', source_lang='en')
        print(f"      Result: {te_translation}")
        
        print("   Translating to Hindi (hi)...")
        hi_translation = service.translate_text(test_text, target_lang='hi', source_lang='en')
        print(f"      Result: {hi_translation}")
        
        if te_translation != test_text and hi_translation != test_text:
            print("   [OK] Translation service completed successfully!")
            return True
        else:
            print("   [WARN] Translation service returned original text (fallback or API issue).")
            return False
    except Exception as e:
        print(f"   [FAIL] Translation service error: {e}")
        return False

if __name__ == "__main__":
    print("==================================================================")
    print("BREAK-EVEN PLATFORM - INTEGRATIONS & API KEYS VERIFIER")
    print("==================================================================")
    
    results = {
        "MongoDB": test_mongodb(),
        "Gemini AI": test_gemini(),
        "Groq AI": test_groq(),
        "Stability AI": test_stability(),
        "Netlify API": test_netlify(),
        "GitHub API": test_github(),
        "Email SMTP": test_email(),
        "Translation": test_translation()
    }
    
    print("\n" + "=" * 50)
    print("INTEGRATIONS SUMMARY REPORT:")
    print("=" * 50)
    
    all_passed = True
    for service_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        if not passed:
            all_passed = False
        print(f"   {service_name:<15}: {status}")
        
    print("=" * 50)
    if all_passed:
        print("All API keys and integrations are fully verified and WORKING!")
    else:
        print("Some integrations failed. Please verify the relevant keys in your .env file.")
    print("==================================================================")
