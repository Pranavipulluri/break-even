#!/usr/bin/env python3
"""
Force deploy enhanced template with direct verification
"""
import os
import sys
import requests
import zipfile
import io
import base64
import random
import string
from datetime import datetime

# Configuration
NETLIFY_API_KEY = "nfp_gp9y9sKHxnKFKJHhP66Ay9HqNxTK1xPk74a1"
BACKEND_URL = "http://localhost:5000"

def create_enhanced_website_directly():
    """Create enhanced website directly without service layer"""
    print("🚀 DIRECT ENHANCED WEBSITE DEPLOYMENT")
    print("=" * 50)
    
    # Load enhanced template directly
    template_path = r"C:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\netlify-functions\enhanced-mini-website-template.html"
    
    if not os.path.exists(template_path):
        print("❌ Enhanced template not found!")
        return None
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    print(f"✅ Loaded enhanced template: {len(template)} characters")
    
    # Verify template has enhanced features
    has_nav_tabs = 'class="nav-tabs"' in template
    has_feedback_form = 'id="feedbackForm"' in template
    has_customer_login = 'id="customerLoginForm"' in template
    has_newsletter = 'id="newsletterForm"' in template
    
    print(f"Enhanced features verification:")
    print(f"  ✅ Navigation tabs: {has_nav_tabs}")
    print(f"  ✅ Feedback form: {has_feedback_form}")
    print(f"  ✅ Customer login: {has_customer_login}")
    print(f"  ✅ Newsletter form: {has_newsletter}")
    
    if not all([has_nav_tabs, has_feedback_form, has_customer_login, has_newsletter]):
        print("❌ Template missing required features!")
        return None
    
    # Replace template variables
    html_content = template.replace('{{title}}', 'ENHANCED BAKERY PRO MAX')
    html_content = html_content.replace('{{description}}', 'Professional bakery with full data collection system')
    html_content = html_content.replace('{{phone}}', '555-ENHANCED-123')
    html_content = html_content.replace('{{email}}', 'enhanced@bakery-pro-max.com')
    html_content = html_content.replace('{{address}}', '123 Enhanced Street, Pro City')
    html_content = html_content.replace('{{business_id}}', 'enhanced-business-123')
    html_content = html_content.replace('{{backend_url}}', BACKEND_URL)
    html_content = html_content.replace('{{website_source}}', 'enhanced-bakery-pro-max')
    
    # Verify replacements
    has_title = 'ENHANCED BAKERY PRO MAX' in html_content
    has_backend_url = BACKEND_URL in html_content
    print(f"Template processing:")
    print(f"  ✅ Title replaced: {has_title}")
    print(f"  ✅ Backend URL set: {has_backend_url}")
    
    # Load all Netlify Functions
    functions_dir = r"C:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\netlify-functions"
    
    netlify_functions = [
        'register-user.js',
        'customer-register.js', 
        'customer-login.js',
        'submit-feedback.js',
        'submit-newsletter.js',
        'submit-interest.js',
        'get-products.js',
        'get-recent-feedback.js'
    ]
    
    website_files = {
        'index.html': html_content
    }
    
    # Load each function
    for func_name in netlify_functions:
        func_path = os.path.join(functions_dir, func_name)
        if os.path.exists(func_path):
            with open(func_path, 'r', encoding='utf-8') as f:
                website_files[f'netlify/functions/{func_name}'] = f.read()
            print(f"  ✅ Loaded function: {func_name}")
        else:
            print(f"  ❌ Missing function: {func_name}")
    
    print(f"\n📦 Total files to deploy: {len(website_files)}")
    
    # Create ZIP file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in website_files.items():
            zip_file.writestr(filename, content)
    
    zip_data = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')
    
    # Generate unique site name
    site_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    site_name = f"enhanced-bakery-max-{datetime.now().strftime('%m%d%H%M')}-{site_suffix}"
    
    print(f"🌐 Deploying as: {site_name}")
    
    # Deploy to Netlify
    headers = {
        'Authorization': f'Bearer {NETLIFY_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Create site
    site_data = {
        'name': site_name,
        'custom_domain': None
    }
    
    try:
        print("Creating Netlify site...")
        response = requests.post(
            'https://api.netlify.com/api/v1/sites',
            json=site_data,
            headers=headers
        )
        
        if response.status_code not in [200, 201]:
            print(f"❌ Failed to create site: {response.status_code}")
            print(response.text)
            return None
        
        site_info = response.json()
        site_id = site_info['id']
        print(f"✅ Site created: {site_id}")
        
        # Deploy files
        print("Deploying files...")
        deploy_data = {
            'files': {filename: {'content': content} for filename, content in website_files.items()}
        }
        
        response = requests.post(
            f'https://api.netlify.com/api/v1/sites/{site_id}/deploys',
            json=deploy_data,
            headers=headers
        )
        
        if response.status_code not in [200, 201]:
            print(f"❌ Failed to deploy: {response.status_code}")
            print(response.text)
            return None
        
        deploy_info = response.json()
        website_url = deploy_info.get('ssl_url') or deploy_info.get('url')
        
        print(f"🎉 ENHANCED WEBSITE DEPLOYED!")
        print(f"🌐 URL: {website_url}")
        print(f"📊 Files deployed: {len(website_files)}")
        print(f"⚡ Functions: {len(netlify_functions)}")
        
        print(f"\n🔍 FEATURES TO VERIFY:")
        print(f"1. Open: {website_url}")
        print(f"2. Look for navigation tabs: Products | Customer Feedback | Customer Login | Stay Connected")
        print(f"3. Test feedback form with star ratings")
        print(f"4. Test customer login form")
        print(f"5. Test newsletter signup")
        
        return website_url
        
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return None

if __name__ == "__main__":
    create_enhanced_website_directly()
