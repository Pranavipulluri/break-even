#!/usr/bin/env python3
"""
Template deployment diagnostic tool
"""
import os
import sys

# Add the backend path
backend_path = r"C:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\backend"
sys.path.append(backend_path)

def main():
    print("=== Enhanced Template Diagnostic ===")
    
    # Test 1: Check if enhanced template file exists
    template_path = r"C:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\netlify-functions\enhanced-mini-website-template.html"
    print(f"1. Template file exists: {os.path.exists(template_path)}")
    
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"   Template size: {len(content)} characters")
        
        # Check for enhanced features
        features = [
            ('Navigation tabs', 'nav-tabs' in content),
            ('Customer Feedback tab', 'Customer Feedback' in content),
            ('Customer Login tab', 'Customer Login' in content),  
            ('Feedback form', 'feedbackForm' in content),
            ('Customer login form', 'customerLoginForm' in content),
            ('Newsletter form', 'newsletterForm' in content),
            ('Rating stars', 'rating-stars' in content),
            ('Business info placeholders', '{{phone}}' in content and '{{email}}' in content)
        ]
        
        print("\n2. Enhanced features check:")
        all_good = True
        for feature, exists in features:
            status = "✅" if exists else "❌"
            print(f"   {status} {feature}")
            if not exists:
                all_good = False
        
        if all_good:
            print("\n✅ Enhanced template has all required features!")
        else:
            print("\n❌ Enhanced template is missing some features!")
    
    # Test 2: Check netlify service path resolution
    print("\n3. Testing NetlifyService path resolution:")
    try:
        from app.services.netlify_service import NetlifyService
        service = NetlifyService()
        
        # Test the load_template method
        loaded_template = service.load_template('enhanced-mini-website-template.html')
        print(f"   Service loaded template size: {len(loaded_template)} characters")
        
        # Check if it's the basic fallback template
        is_basic_fallback = 'body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }' in loaded_template
        
        if is_basic_fallback:
            print("   ❌ Service is loading BASIC FALLBACK template - path issue!")
        else:
            print("   ✅ Service is loading ENHANCED template correctly")
            
        # Compare with direct file read
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                direct_content = f.read()
            
            if loaded_template == direct_content:
                print("   ✅ Service template matches file template")
            else:
                print("   ❌ Service template doesn't match file template!")
                print(f"      Service size: {len(loaded_template)}")
                print(f"      File size: {len(direct_content)}")
        
    except Exception as e:
        print(f"   ❌ Error testing NetlifyService: {e}")
    
    # Test 3: Check what's actually being deployed
    print("\n4. Checking data collection website creation:")
    try:
        from app.services.netlify_service import NetlifyService
        service = NetlifyService()
        
        # Simulate what happens in create_data_collection_website
        template = service.load_template('enhanced-mini-website-template.html')
        
        # Replace template variables (simplified)
        html_content = template.replace('{{title}}', 'TEST BAKERY')
        html_content = html_content.replace('{{description}}', 'Test description')
        html_content = html_content.replace('{{phone}}', '123-456-7890')
        html_content = html_content.replace('{{email}}', 'test@bakery.com')
        html_content = html_content.replace('{{address}}', 'Test Address')
        
        # Check if final HTML has enhanced features
        has_nav_tabs = 'nav-tabs' in html_content
        has_feedback_form = 'feedbackForm' in html_content
        has_customer_login = 'customerLoginForm' in html_content
        
        print(f"   Final HTML has nav tabs: {'✅' if has_nav_tabs else '❌'}")
        print(f"   Final HTML has feedback form: {'✅' if has_feedback_form else '❌'}")
        print(f"   Final HTML has customer login: {'✅' if has_customer_login else '❌'}")
        
        if has_nav_tabs and has_feedback_form and has_customer_login:
            print("   ✅ Template processing is working correctly!")
        else:
            print("   ❌ Template processing has issues!")
            
        # Save a test HTML file to check
        test_file = r"C:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\test_output.html"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"   💾 Saved test HTML to: {test_file}")
        print("   🌐 Open this file in browser to see what's actually being generated")
        
    except Exception as e:
        print(f"   ❌ Error testing template processing: {e}")
    
    print("\n" + "="*60)
    print("DIAGNOSIS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
