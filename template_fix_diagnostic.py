#!/usr/bin/env python3
"""
Direct template verification and fix
"""
import os
import sys

# Add backend path
backend_path = r"C:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\backend"
sys.path.append(backend_path)

def verify_template():
    print("=== DIRECT TEMPLATE VERIFICATION ===")
    
    # Check enhanced template directly
    template_path = r"C:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\netlify-functions\enhanced-mini-website-template.html"
    
    if not os.path.exists(template_path):
        print("❌ Enhanced template file not found!")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Template size: {len(content)} characters")
    
    # Check for specific enhanced features
    required_features = {
        'Navigation tabs': 'class="nav-tabs"' in content,
        'Customer Feedback tab': 'Customer Feedback' in content,
        'Customer Login tab': 'Customer Login' in content,
        'Stay Connected tab': 'Stay Connected' in content,
        'Feedback form': 'id="feedbackForm"' in content,
        'Customer login form': 'id="customerLoginForm"' in content,
        'Newsletter form': 'id="newsletterForm"' in content,
        'Rating stars': 'rating-stars' in content,
        'Template variables': '{{title}}' in content and '{{description}}' in content
    }
    
    print("\nFeature verification:")
    missing_features = []
    for feature, exists in required_features.items():
        status = "✅" if exists else "❌"
        print(f"  {status} {feature}")
        if not exists:
            missing_features.append(feature)
    
    if missing_features:
        print(f"\n❌ Missing features: {', '.join(missing_features)}")
        return False
    else:
        print("\n✅ All enhanced features present in template!")
        return True

def test_netlify_service():
    print("\n=== NETLIFY SERVICE TEST ===")
    
    try:
        from app.services.netlify_service import NetlifyService
        service = NetlifyService()
        
        # Test loading
        print("Testing enhanced template loading...")
        template = service.load_template('enhanced-mini-website-template.html')
        
        print(f"Loaded template size: {len(template)} characters")
        
        # Check if it's the basic fallback
        is_basic = 'body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }' in template
        
        if is_basic:
            print("❌ Service is loading BASIC FALLBACK template!")
            print("This means the enhanced template file is not being found by the service.")
            return False
        else:
            # Check for enhanced features in loaded template
            has_nav_tabs = 'class="nav-tabs"' in template
            has_feedback_form = 'id="feedbackForm"' in template
            has_customer_login = 'id="customerLoginForm"' in template
            
            print(f"Loaded template has nav tabs: {'✅' if has_nav_tabs else '❌'}")
            print(f"Loaded template has feedback form: {'✅' if has_feedback_form else '❌'}")
            print(f"Loaded template has customer login: {'✅' if has_customer_login else '❌'}")
            
            if has_nav_tabs and has_feedback_form and has_customer_login:
                print("✅ Service is loading enhanced template correctly!")
                return True
            else:
                print("❌ Service loaded template is missing enhanced features!")
                return False
                
    except Exception as e:
        print(f"❌ Error testing NetlifyService: {e}")
        return False

def create_test_deployment():
    print("\n=== CREATING TEST DEPLOYMENT ===")
    
    try:
        from app.services.netlify_service import NetlifyService
        service = NetlifyService()
        
        # Load and process template
        template = service.load_template('enhanced-mini-website-template.html')
        
        # Replace variables
        html_content = template.replace('{{title}}', 'TEST ENHANCED BAKERY')
        html_content = html_content.replace('{{description}}', 'Testing enhanced template deployment')
        html_content = html_content.replace('{{phone}}', '555-TEST-123')
        html_content = html_content.replace('{{email}}', 'test@enhanced-bakery.com')
        html_content = html_content.replace('{{address}}', 'Test Enhanced Address')
        html_content = html_content.replace('{{business_id}}', 'test-business-123')
        html_content = html_content.replace('{{backend_url}}', 'http://localhost:5000')
        html_content = html_content.replace('{{website_source}}', 'test-enhanced-site')
        
        # Save test file locally to verify
        test_file = r"C:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\test_enhanced_output.html"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Test enhanced HTML saved to: {test_file}")
        print("🌐 Open this file in your browser to see what should be deployed")
        
        # Check final HTML
        has_nav_tabs = 'class="nav-tabs"' in html_content
        has_feedback_form = 'id="feedbackForm"' in html_content
        has_customer_login = 'id="customerLoginForm"' in html_content
        has_replaced_title = 'TEST ENHANCED BAKERY' in html_content
        
        print(f"\nFinal HTML verification:")
        print(f"  Has nav tabs: {'✅' if has_nav_tabs else '❌'}")
        print(f"  Has feedback form: {'✅' if has_feedback_form else '❌'}")
        print(f"  Has customer login: {'✅' if has_customer_login else '❌'}")
        print(f"  Title replaced: {'✅' if has_replaced_title else '❌'}")
        
        if all([has_nav_tabs, has_feedback_form, has_customer_login, has_replaced_title]):
            print("✅ Template processing is working correctly!")
            print("The issue might be with Netlify deployment, not template processing.")
            return True
        else:
            print("❌ Template processing has issues!")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test deployment: {e}")
        return False

def main():
    print("🔍 ENHANCED TEMPLATE DIAGNOSIS")
    print("=" * 50)
    
    template_ok = verify_template()
    service_ok = test_netlify_service()
    deployment_ok = create_test_deployment()
    
    print("\n" + "=" * 50)
    print("DIAGNOSIS SUMMARY:")
    print("=" * 50)
    print(f"Enhanced template file: {'✅ OK' if template_ok else '❌ PROBLEM'}")
    print(f"NetlifyService loading: {'✅ OK' if service_ok else '❌ PROBLEM'}")
    print(f"Template processing: {'✅ OK' if deployment_ok else '❌ PROBLEM'}")
    
    if template_ok and service_ok and deployment_ok:
        print("\n🎯 CONCLUSION: Template system is working correctly!")
        print("The issue is likely with Netlify deployment or caching.")
        print("\nSUGGESTED ACTIONS:")
        print("1. Wait 5-10 minutes for Netlify to fully process deployment")
        print("2. Try hard refresh (Ctrl+F5) on your website")
        print("3. Try opening website in incognito/private mode")
        print("4. Check if Netlify Functions are actually deployed")
    else:
        print("\n❌ CONCLUSION: Template system has issues!")
        print("Need to fix the template loading/processing system.")

if __name__ == "__main__":
    main()
