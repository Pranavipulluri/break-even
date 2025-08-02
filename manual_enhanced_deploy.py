import requests
import zipfile
import io
import base64
import random
import string
from datetime import datetime
import os

# Your Netlify API key
NETLIFY_API_KEY = "nfp_gp9y9sKHxnKFKJHhP66Ay9HqNxTK1xPk74a1"

# Load the enhanced template
template_path = r"C:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\netlify-functions\enhanced-mini-website-template.html"

print("🚀 MANUAL ENHANCED TEMPLATE DEPLOYMENT")
print("=" * 50)

if not os.path.exists(template_path):
    print("❌ Enhanced template not found!")
    exit(1)

with open(template_path, 'r', encoding='utf-8') as f:
    template = f.read()

print(f"✅ Loaded template: {len(template)} characters")

# Verify enhanced features
has_nav_tabs = 'nav-tabs' in template
has_feedback = 'feedbackForm' in template
has_login = 'customerLoginForm' in template
has_newsletter = 'newsletterForm' in template

print(f"Enhanced features:")
print(f"  Navigation tabs: {'✅' if has_nav_tabs else '❌'}")
print(f"  Feedback form: {'✅' if has_feedback else '❌'}")
print(f"  Login form: {'✅' if has_login else '❌'}")
print(f"  Newsletter form: {'✅' if has_newsletter else '❌'}")

if not all([has_nav_tabs, has_feedback, has_login, has_newsletter]):
    print("❌ Template missing features!")
    exit(1)

# Replace template variables
html_content = template.replace('{{title}}', 'FINAL ENHANCED BAKERY TEST')
html_content = html_content.replace('{{description}}', 'Ultimate test with all navigation tabs and forms')
html_content = html_content.replace('{{phone}}', '555-FINAL-TEST')
html_content = html_content.replace('{{email}}', 'final@enhanced-test.com')
html_content = html_content.replace('{{address}}', '123 Final Test Street')
html_content = html_content.replace('{{business_id}}', 'final-test-789')
html_content = html_content.replace('{{backend_url}}', 'http://localhost:5000')
html_content = html_content.replace('{{website_source}}', 'final-enhanced-test')

print(f"✅ Template variables replaced")

# Simple deployment with just the HTML
website_files = {
    'index.html': html_content
}

# Create ZIP
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
    for filename, content in website_files.items():
        zip_file.writestr(filename, content)

zip_data = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')

# Generate site name
site_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
site_name = f"final-enhanced-test-{datetime.now().strftime('%m%d%H%M')}-{site_suffix}"

print(f"🌐 Deploying as: {site_name}")

# Deploy to Netlify
headers = {
    'Authorization': f'Bearer {NETLIFY_API_KEY}',
    'Content-Type': 'application/json'
}

try:
    # Create site
    print("Creating site...")
    response = requests.post(
        'https://api.netlify.com/api/v1/sites',
        json={'name': site_name},
        headers=headers
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Site creation failed: {response.status_code}")
        print(response.text)
        exit(1)
    
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
        print(f"❌ Deployment failed: {response.status_code}")
        print(response.text)
        exit(1)
    
    deploy_info = response.json()
    website_url = deploy_info.get('ssl_url') or deploy_info.get('url')
    
    print(f"🎉 ENHANCED WEBSITE DEPLOYED!")
    print(f"🌐 URL: {website_url}")
    print(f"\n🔍 WHAT YOU SHOULD SEE:")
    print(f"1. A beautiful gradient background")
    print(f"2. Four navigation tabs at the top:")
    print(f"   - Products (with shopping bag icon)")
    print(f"   - Customer Feedback (with comments icon)")
    print(f"   - Customer Login (with user icon)")
    print(f"   - Stay Connected (with envelope icon)")
    print(f"3. Click each tab to see different forms")
    print(f"4. Star rating system in feedback form")
    print(f"5. Professional styling throughout")
    
    print(f"\n📋 TEST INSTRUCTIONS:")
    print(f"1. Open the URL above")
    print(f"2. You should immediately see the navigation tabs")
    print(f"3. If you still see a basic website, clear browser cache (Ctrl+F5)")
    print(f"4. Try opening in incognito/private mode")
    
except Exception as e:
    print(f"❌ Error: {e}")
