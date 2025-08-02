#!/usr/bin/env python3
"""
Test the fixed NetlifyService to ensure enhanced template deployment
"""
import os
import sys

# Add backend path
backend_path = r"C:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\backend"
sys.path.append(backend_path)

def test_enhanced_deployment():
    print("🧪 TESTING ENHANCED TEMPLATE DEPLOYMENT")
    print("=" * 50)
    
    try:
        from app.services.netlify_service import NetlifyService
        
        # Create service instance
        service = NetlifyService()
        
        # Test creating data collection website
        print("Creating enhanced data collection website...")
        
        result = service.create_data_collection_website(
            title="ULTIMATE ENHANCED BAKERY TEST",
            description="Final test of enhanced template with all navigation tabs and forms",
            content="Enhanced bakery content",
            business_id="test-business-456"
        )
        
        print(f"Deployment result: {result}")
        
        if result and result.get('success'):
            print(f"🎉 SUCCESS! Enhanced website deployed!")
            print(f"🌐 URL: {result.get('url')}")
            print(f"📋 Site ID: {result.get('site_id')}")
            
            print(f"\n🔍 VERIFICATION CHECKLIST:")
            print(f"1. Open: {result.get('url')}")
            print(f"2. You should see 4 navigation tabs:")
            print(f"   - Products")
            print(f"   - Customer Feedback") 
            print(f"   - Customer Login")
            print(f"   - Stay Connected")
            print(f"3. Click each tab to verify forms are working")
            print(f"4. Test the star rating system in Customer Feedback")
            print(f"5. All forms should have proper styling and functionality")
            
            return result.get('url')
        else:
            print(f"❌ FAILED: {result.get('error') if result else 'Unknown error'}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

if __name__ == "__main__":
    test_enhanced_deployment()
