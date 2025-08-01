#!/usr/bin/env python3
"""
Simple test to verify backend starts without errors
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_app_creation():
    """Test if the Flask app can be created without errors"""
    try:
        print("🧪 Testing Flask app creation...")
        
        from app import create_app
        app = create_app()
        
        print("✅ Flask app created successfully!")
        
        # Test if routes are registered
        with app.app_context():
            rules = [str(rule) for rule in app.url_map.iter_rules()]
            ai_routes = [rule for rule in rules if 'ai-tools' in rule]
            
            print(f"📋 Found {len(ai_routes)} AI tool routes:")
            for route in ai_routes:
                print(f"  - {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating Flask app: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_services():
    """Test if services can be imported and initialized"""
    try:
        print("\n🔧 Testing service imports...")
        
        from app.services.gemini_service import get_gemini_service
        from app.services.github_service import get_github_service
        from app.services.netlify_service import get_netlify_service
        
        # Create app context for testing
        from app import create_app
        app = create_app()
        
        with app.app_context():
            gemini = get_gemini_service()
            github = get_github_service()
            netlify = get_netlify_service()
            
            print("✅ Gemini service initialized")
            print("✅ GitHub service initialized") 
            print("✅ Netlify service initialized")
            
            # Test API key access
            print(f"🔑 Gemini API key: {'✅ Set' if gemini.api_key else '❌ Missing'}")
            print(f"🔑 GitHub token: {'✅ Set' if github.token else '❌ Missing'}")
            print(f"🔑 Netlify API key: {'✅ Set' if netlify.api_key else '❌ Missing'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing services: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Break-even Backend...")
    print("=" * 50)
    
    app_test = test_app_creation()
    service_test = test_services()
    
    print("\n📊 Test Results:")
    print("=" * 50)
    print(f"Flask App: {'✅ Pass' if app_test else '❌ Fail'}")
    print(f"Services: {'✅ Pass' if service_test else '❌ Fail'}")
    
    if app_test and service_test:
        print("\n🎉 All tests passed! Backend is ready to start.")
        print("\nTo start the server, run:")
        print("python run.py")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
