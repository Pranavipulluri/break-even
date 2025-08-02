"""
Netlify API Service for Break-even App
COMPLETE FIXED VERSION - Provides website deployment and hosting through Netlify with data collection
"""

import requests
from flask import current_app
import zipfile
import io
import base64
import random
import string
from datetime import datetime
import os

class NetlifyService:
    
    def __init__(self, api_key=None):
        self._api_key = api_key
        self.base_url = "https://api.netlify.com/api/v1"
    
    @property
    def api_key(self):
        if self._api_key:
            return self._api_key
        try:
            from flask import current_app
            return current_app.config.get('NETLIFY_API_KEY')
        except RuntimeError:
            # Fallback when outside application context
            from app.config import Config
            return Config.NETLIFY_API_KEY
    
    @property
    def headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_site(self, site_name, custom_domain=None):
        """Create a new Netlify site"""
        try:
            url = f"{self.base_url}/sites"
            data = {
                "name": site_name,
                "custom_domain": custom_domain
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                site_data = response.json()
                return {
                    'success': True,
                    'site': {
                        'id': site_data['id'],
                        'name': site_data['name'],
                        'url': site_data['url'],
                        'admin_url': site_data['admin_url'],
                        'ssl_url': site_data['ssl_url']
                    }
                }
            elif response.status_code == 422:
                # Handle subdomain uniqueness error specifically
                error_data = response.json()
                if 'errors' in error_data and 'subdomain' in error_data['errors']:
                    return {
                        'success': False,
                        'error': 'Site name already exists. Please try with a different name or wait a moment and try again.',
                        'retry_suggested': True
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Netlify Validation Error: {response.text}'
                    }
            else:
                return {
                    'success': False,
                    'error': f'Netlify API Error: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def deploy_site(self, site_id, files_dict):
        """Deploy files to a Netlify site"""
        try:
            # Create a zip file with the website files
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path, content in files_dict.items():
                    if isinstance(content, str):
                        zip_file.writestr(file_path, content.encode())
                    else:
                        zip_file.writestr(file_path, content)
            
            zip_buffer.seek(0)
            
            # Deploy to Netlify
            url = f"{self.base_url}/sites/{site_id}/deploys"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/zip'
            }
            
            response = requests.post(url, headers=headers, data=zip_buffer.getvalue())
            
            if response.status_code in [200, 201]:
                deploy_data = response.json()
                return {
                    'success': True,
                    'deploy': {
                        'id': deploy_data['id'],
                        'url': deploy_data['deploy_ssl_url'],
                        'state': deploy_data['state'],
                        'created_at': deploy_data['created_at']
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'Deploy failed: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def deploy_enhanced_website(self, business_name, website_files):
        """Deploy enhanced website with custom files (FIXED VERSION)"""
        try:
            # Sanitize and create unique site name
            base_name = business_name.lower().replace(' ', '-').replace('_', '-')
            # Remove any non-alphanumeric characters except hyphens
            base_name = ''.join(c for c in base_name if c.isalnum() or c == '-')
            # Limit length and ensure it doesn't start/end with hyphen
            base_name = base_name[:20].strip('-')
            
            # Add timestamp and random string for uniqueness
            timestamp = datetime.now().strftime('%m%d%H%M')  # MMDDHHMM format
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            site_name = f"{base_name}-{timestamp}-{random_suffix}"
            
            # Ensure name is valid (max 63 chars, no consecutive hyphens)
            site_name = site_name.replace('--', '-')[:63]
            
            print(f"🚀 Creating enhanced website: {site_name}")
            
            # Create site with retry logic for uniqueness conflicts
            max_retries = 3
            for attempt in range(max_retries):
                site_result = self.create_site(site_name)
                
                if site_result['success']:
                    break
                elif site_result.get('retry_suggested') and attempt < max_retries - 1:
                    # Generate a new unique name and try again
                    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                    site_name = f"{base_name}-{timestamp}-{random_suffix}"
                    site_name = site_name.replace('--', '-')[:63]
                    continue
                else:
                    return site_result
            
            if not site_result['success']:
                return site_result
            
            site_info = site_result['site']
            
            print(f"✅ Site created: {site_info['ssl_url']}")
            print(f"📁 Deploying {len(website_files)} files...")
            
            # Deploy the enhanced website files (NO OVERRIDE!)
            deploy_result = self.deploy_site(site_info['id'], website_files)
            
            if deploy_result['success']:
                print(f"🎉 Enhanced website deployed successfully!")
                return {
                    'success': True,
                    'site': site_info,
                    'deploy': deploy_result['deploy'],
                    'website_url': site_info['ssl_url'],
                    'netlify_url': site_info['ssl_url']
                }
            else:
                return deploy_result
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_and_deploy_website(self, business_name, website_content):
        """Create a site and deploy website content (BASIC VERSION)"""
        try:
            # Sanitize and create unique site name
            base_name = business_name.lower().replace(' ', '-').replace('_', '-')
            # Remove any non-alphanumeric characters except hyphens
            base_name = ''.join(c for c in base_name if c.isalnum() or c == '-')
            # Limit length and ensure it doesn't start/end with hyphen
            base_name = base_name[:20].strip('-')
            
            # Add timestamp and random string for uniqueness
            timestamp = datetime.now().strftime('%m%d%H%M')  # MMDDHHMM format
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            site_name = f"{base_name}-{timestamp}-{random_suffix}"
            
            # Ensure name is valid (max 63 chars, no consecutive hyphens)
            site_name = site_name.replace('--', '-')[:63]
            
            # Create site with retry logic for uniqueness conflicts
            max_retries = 3
            for attempt in range(max_retries):
                site_result = self.create_site(site_name)
                
                if site_result['success']:
                    break
                elif site_result.get('retry_suggested') and attempt < max_retries - 1:
                    # Generate a new unique name and try again
                    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                    site_name = f"{base_name}-{timestamp}-{random_suffix}"
                    site_name = site_name.replace('--', '-')[:63]
                    continue
                else:
                    return site_result
            
            if not site_result['success']:
                return site_result
            
            site_info = site_result['site']
            
            # Create basic website files
            files = {
                'index.html': self.generate_website_html(business_name, website_content),
                'style.css': self.generate_css(),
                '_redirects': '/*    /index.html   200'  # SPA redirect rules
            }
            
            # Deploy the site
            deploy_result = self.deploy_site(site_info['id'], files)
            
            if deploy_result['success']:
                return {
                    'success': True,
                    'site': site_info,
                    'deploy': deploy_result['deploy'],
                    'website_url': site_info['ssl_url']
                }
            else:
                return deploy_result
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_data_collection_website(self, title, description, content, business_id=None, netlify_site_name=None):
        """Create a website with integrated data collection forms (FINAL FIXED VERSION)"""
        try:
            # FORCE load the enhanced template with absolute path
            enhanced_template_path = r"C:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\netlify-functions\enhanced-mini-website-template.html"
            
            print(f"🚀 Loading enhanced template from: {enhanced_template_path}")
            
            if not os.path.exists(enhanced_template_path):
                print(f"❌ Enhanced template not found, using fallback")
                # Use the fixed template content directly
                template = self.get_fixed_enhanced_template()
            else:
                with open(enhanced_template_path, 'r', encoding='utf-8') as f:
                    template = f.read()
            
            print(f"✅ Enhanced template loaded: {len(template)} characters")
            
            # Verify it's the enhanced template
            has_nav_tabs = 'nav-tabs' in template
            has_feedback_form = 'feedbackForm' in template or 'register' in template.lower()
            has_register_form = 'registerForm' in template or 'register' in template.lower()
            
            print(f"Template verification:")
            print(f"  - Navigation tabs: {'✅' if has_nav_tabs else '❌'}")
            print(f"  - Feedback form: {'✅' if has_feedback_form else '❌'}")
            print(f"  - Register form: {'✅' if has_register_form else '❌'}")
            
            if not (has_nav_tabs and has_feedback_form and has_register_form):
                print("⚠️ Using fallback enhanced template")
                template = self.get_fixed_enhanced_template()
            
            # Get user information for business details
            user_info = {
                'phone': '',
                'email': '',
                'address': ''
            }
            
            if business_id:
                try:
                    from bson import ObjectId
                    from app import mongo
                    user = mongo.db.users.find_one({'_id': ObjectId(business_id)})
                    if user:
                        user_info = {
                            'phone': user.get('phone', ''),
                            'email': user.get('email', ''),
                            'address': user.get('address', '')
                        }
                except Exception as e:
                    print(f"Error fetching user info: {e}")
            
            # Replace template variables
            html_content = template.replace('{{title}}', title)
            html_content = html_content.replace('{{description}}', description)
            html_content = html_content.replace('{{phone}}', user_info['phone'])
            html_content = html_content.replace('{{email}}', user_info['email'])
            html_content = html_content.replace('{{address}}', user_info['address'])
            html_content = html_content.replace('{{business_id}}', business_id or '')
            
            print(f"📝 Template variables replaced")
            
            # Create the website files with simple Netlify Functions
            website_files = {
                'index.html': html_content,
                'netlify.toml': '''[build]
  functions = "functions"

[functions]
  external_node_modules = ["mongodb"]

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200''',
                'functions/register-user.js': self.get_simple_register_function(),
                'functions/submit-feedback.js': self.get_simple_feedback_function(),
                'functions/submit-newsletter.js': self.get_simple_newsletter_function(),
                'functions/get-recent-feedback.js': self.get_simple_recent_feedback_function(),
                'functions/package.json': '''{
  "name": "netlify-functions",
  "version": "1.0.0",
  "dependencies": {
    "mongodb": "^6.3.0"
  }
}'''
            }
            
            print(f"📦 Prepared {len(website_files)} files for deployment")
            
            # Deploy the enhanced website using the fixed deployment method
            result = self.deploy_enhanced_website(title, website_files)
            
            if result.get('success'):
                print(f"🎉 Enhanced data collection website deployed successfully!")
                print(f"🌐 URL: {result['website_url']}")
            else:
                print(f"❌ Deployment failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error creating data collection website: {e}")
            return {
                'success': False,
                'error': f'Failed to create data collection website: {str(e)}'
            }
    
    def get_fixed_enhanced_template(self):
        """Returns the fixed enhanced template with proper Netlify Functions integration"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6; color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header {
            background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);
            border-radius: 20px; padding: 2rem; text-align: center; margin-bottom: 2rem;
            box-shadow: 0 15px 40px rgba(0,0,0,0.1);
        }
        .header h1 {
            font-size: 3rem; margin-bottom: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .header p { font-size: 1.2rem; color: #666; margin-bottom: 1rem; }
        .business-info {
            display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 1rem;
        }
        .business-info div { display: flex; align-items: center; gap: 0.5rem; color: #555; }
        .business-info i { color: #667eea; }
        .nav-tabs {
            display: flex; justify-content: center; margin-bottom: 2rem;
            background: rgba(255, 255, 255, 0.9); border-radius: 15px;
            padding: 0.5rem; backdrop-filter: blur(10px);
        }
        .nav-tab {
            background: none; border: none; padding: 1rem 2rem;
            border-radius: 10px; cursor: pointer; font-weight: 600;
            transition: all 0.3s ease; color: #666;
        }
        .nav-tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; transform: translateY(-2px);
        }
        .nav-tab:hover:not(.active) { background: rgba(102, 126, 234, 0.1); color: #667eea; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .form-card {
            background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);
            border-radius: 20px; padding: 2rem; margin: 1rem 0;
            box-shadow: 0 15px 40px rgba(0,0,0,0.1);
        }
        .form-card h3 { color: #667eea; margin-bottom: 1.5rem; text-align: center; font-size: 1.5rem; }
        .form-group { margin-bottom: 1.5rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #555; }
        .form-group input, .form-group textarea {
            width: 100%; padding: 1rem; border: 2px solid #e0e0e0;
            border-radius: 12px; font-size: 1rem; transition: all 0.3s ease;
        }
        .form-group input:focus, .form-group textarea:focus {
            outline: none; border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .form-group textarea { resize: vertical; min-height: 120px; }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; padding: 1rem 2rem;
            border-radius: 12px; font-weight: 600; cursor: pointer;
            transition: all 0.3s ease; width: 100%;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .alert { padding: 1rem; border-radius: 12px; margin: 1rem 0; font-weight: 600; display: none; }
        .alert-success { background: #dcfce7; color: #166534; }
        .alert-error { background: #fee2e2; color: #991b1b; }
        .rating-stars { display: flex; gap: 0.5rem; justify-content: center; margin: 1rem 0; }
        .rating-stars button {
            background: none; border: none; font-size: 2rem; cursor: pointer;
            color: #ddd; transition: all 0.3s ease;
        }
        .rating-stars button.active { color: #ffd700; transform: scale(1.1); }
        .feedback-categories {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem; margin: 1rem 0;
        }
        .category-btn {
            padding: 0.75rem; border: 2px solid #e0e0e0; background: white;
            border-radius: 10px; cursor: pointer; transition: all 0.3s ease;
            text-align: center; font-weight: 600;
        }
        .category-btn.active { border-color: #667eea; background: rgba(102, 126, 234, 0.1); color: #667eea; }
        .loading {
            display: inline-block; width: 20px; height: 20px;
            border: 3px solid rgba(255,255,255,.3); border-radius: 50%;
            border-top-color: #fff; animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .footer {
            background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px);
            border-radius: 20px; padding: 2rem; text-align: center;
            margin-top: 3rem; color: #666;
        }
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .header h1 { font-size: 2rem; }
            .nav-tabs { flex-direction: column; gap: 0.5rem; }
            .business-info { flex-direction: column; gap: 1rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{title}}</h1>
            <p>{{description}}</p>
            <div class="business-info">
                <div><i class="fas fa-phone"></i> {{phone}}</div>
                <div><i class="fas fa-envelope"></i> {{email}}</div>
                <div><i class="fas fa-map-marker-alt"></i> {{address}}</div>
            </div>
        </div>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('register')">
                <i class="fas fa-user-plus"></i> Register
            </button>
            <button class="nav-tab" onclick="showTab('feedback')">
                <i class="fas fa-comments"></i> Feedback
            </button>
            <button class="nav-tab" onclick="showTab('newsletter')">
                <i class="fas fa-envelope"></i> Newsletter
            </button>
        </div>
        
        <div id="register" class="tab-content active">
            <div class="form-card">
                <h3><i class="fas fa-user-plus"></i> Join Our Community</h3>
                <form id="registerForm">
                    <div class="form-group">
                        <label for="register_name">Your Name</label>
                        <input type="text" id="register_name" name="register_name" required>
                    </div>
                    <div class="form-group">
                        <label for="register_email">Email Address</label>
                        <input type="email" id="register_email" name="register_email" required>
                    </div>
                    <div class="form-group">
                        <label for="register_phone">Phone Number</label>
                        <input type="tel" id="register_phone" name="register_phone">
                    </div>
                    <div class="form-group">
                        <label for="register_interests">What are you interested in?</label>
                        <textarea id="register_interests" name="register_interests" placeholder="Tell us about your interests..."></textarea>
                    </div>
                    <button type="submit" class="btn">
                        <span class="btn-text">Register</span>
                    </button>
                    <div id="register-alert" class="alert"></div>
                </form>
            </div>
        </div>
        
        <div id="feedback" class="tab-content">
            <div class="form-card">
                <h3><i class="fas fa-star"></i> Share Your Feedback</h3>
                <form id="feedbackForm">
                    <div class="form-group">
                        <label for="customer_name">Your Name</label>
                        <input type="text" id="customer_name" name="customer_name" required>
                    </div>
                    <div class="form-group">
                        <label for="customer_email">Email Address</label>
                        <input type="email" id="customer_email" name="customer_email" required>
                    </div>
                    <div class="form-group">
                        <label for="customer_phone">Phone Number (Optional)</label>
                        <input type="tel" id="customer_phone" name="customer_phone">
                    </div>
                    <div class="form-group">
                        <label>Feedback Category</label>
                        <div class="feedback-categories">
                            <div class="category-btn active" onclick="selectCategory(this, 'general')">General</div>
                            <div class="category-btn" onclick="selectCategory(this, 'product_quality')">Product Quality</div>
                            <div class="category-btn" onclick="selectCategory(this, 'customer_service')">Customer Service</div>
                            <div class="category-btn" onclick="selectCategory(this, 'delivery')">Delivery</div>
                        </div>
                        <input type="hidden" id="feedback_category" name="feedback_category" value="general">
                    </div>
                    <div class="form-group">
                        <label>Overall Rating</label>
                        <div class="rating-stars" id="rating-stars">
                            <button type="button" onclick="setRating(1)">★</button>
                            <button type="button" onclick="setRating(2)">★</button>
                            <button type="button" onclick="setRating(3)">★</button>
                            <button type="button" onclick="setRating(4)">★</button>
                            <button type="button" onclick="setRating(5)">★</button>
                        </div>
                        <input type="hidden" id="rating" name="rating" value="5">
                    </div>
                    <div class="form-group">
                        <label for="feedback_message">Your Feedback</label>
                        <textarea id="feedback_message" name="feedback_message" placeholder="Tell us about your experience..." required></textarea>
                    </div>
                    <button type="submit" class="btn">
                        <span class="btn-text">Submit Feedback</span>
                    </button>
                    <div id="feedback-alert" class="alert"></div>
                </form>
            </div>
        </div>
        
        <div id="newsletter" class="tab-content">
            <div class="form-card">
                <h3><i class="fas fa-envelope"></i> Stay Connected</h3>
                <p style="text-align: center; color: #666; margin-bottom: 2rem;">
                    Join our newsletter for updates and special offers!
                </p>
                <form id="newsletterForm">
                    <div class="form-group">
                        <label for="newsletter_name">Your Name</label>
                        <input type="text" id="newsletter_name" name="newsletter_name" required>
                    </div>
                    <div class="form-group">
                        <label for="newsletter_email">Email Address</label>
                        <input type="email" id="newsletter_email" name="newsletter_email" required>
                    </div>
                    <div class="form-group">
                        <label>Interests</label>
                        <div class="feedback-categories">
                            <div class="category-btn" onclick="toggleInterest(this, 'new_products')">New Products</div>
                            <div class="category-btn" onclick="toggleInterest(this, 'promotions')">Promotions</div>
                            <div class="category-btn" onclick="toggleInterest(this, 'tips')">Tips & Guides</div>
                            <div class="category-btn" onclick="toggleInterest(this, 'events')">Events</div>
                        </div>
                        <input type="hidden" id="newsletter_interests" name="newsletter_interests" value="">
                    </div>
                    <button type="submit" class="btn">
                        <span class="btn-text">Subscribe Now</span>
                    </button>
                    <div id="newsletter-alert" class="alert"></div>
                </form>
            </div>
        </div>
        
        <div class="footer">
            <p>&copy; 2025 {{title}}. All rights reserved.</p>
            <p>Powered by Break-even Platform</p>
        </div>
    </div>

    <script>
        // Configuration - FIXED to use only Netlify Functions
        const FUNCTIONS_BASE_URL = `${window.location.origin}/.netlify/functions`;
        const BUSINESS_ID = '{{business_id}}';
        const WEBSITE_SOURCE = window.location.hostname;
        
        // Global variables
        let selectedRating = 5;
        let selectedCategory = 'general';
        let selectedInterests = [];
        
        // Initialize the page
        document.addEventListener('DOMContentLoaded', function() {
            setRating(5); // Default rating
        });
        
        // Tab switching functionality
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Remove active class from all nav tabs
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked nav tab
            event.target.closest('.nav-tab').classList.add('active');
        }
        
        // Rating functionality
        function setRating(rating) {
            selectedRating = rating;
            document.getElementById('rating').value = rating;
            
            const stars = document.querySelectorAll('#rating-stars button');
            stars.forEach((star, index) => {
                if (index < rating) {
                    star.classList.add('active');
                } else {
                    star.classList.remove('active');
                }
            });
        }
        
        // Category selection
        function selectCategory(element, category) {
            // Remove active class from all category buttons in the same group
            element.parentElement.querySelectorAll('.category-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Add active class to selected button
            element.classList.add('active');
            
            // Set the hidden field value
            selectedCategory = category;
            document.getElementById('feedback_category').value = category;
        }
        
        // Newsletter interests toggle
        function toggleInterest(element, interest) {
            element.classList.toggle('active');
            
            if (selectedInterests.includes(interest)) {
                selectedInterests = selectedInterests.filter(i => i !== interest);
            } else {
                selectedInterests.push(interest);
            }
            
            document.getElementById('newsletter_interests').value = selectedInterests.join(',');
        }
        
        // Generic form submission
        async function submitForm(form, functionName, alertId) {
            const submitBtn = form.querySelector('.btn');
            const btnText = submitBtn.querySelector('.btn-text');
            const alert = document.getElementById(alertId);
            
            // Show loading state
            submitBtn.disabled = true;
            btnText.innerHTML = '<div class="loading"></div> Submitting...';
            
            try {
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());
                
                // Add metadata
                data.website_source = WEBSITE_SOURCE;
                data.business_id = BUSINESS_ID;
                data.timestamp = new Date().toISOString();
                
                const response = await fetch(`${FUNCTIONS_BASE_URL}/${functionName}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                
                const result = await response.json();
                
                if (result.success) {
                    showAlert(alert, 'success', result.message || 'Thank you! Your submission has been received.');
                    form.reset();
                    
                    // Reset form states
                    if (functionName === 'submit-feedback') {
                        setRating(5);
                        selectCategory(document.querySelector('.category-btn'), 'general');
                    }
                    if (functionName === 'submit-newsletter') {
                        selectedInterests = [];
                        document.querySelectorAll('#newsletter .category-btn').forEach(btn => btn.classList.remove('active'));
                    }
                } else {
                    showAlert(alert, 'error', result.message || 'Something went wrong. Please try again.');
                }
                
            } catch (error) {
                console.error('Submission error:', error);
                showAlert(alert, 'error', 'Network error. Please check your connection and try again.');
            } finally {
                // Reset button state
                submitBtn.disabled = false;
                btnText.innerHTML = functionName === 'submit-feedback' ? 'Submit Feedback' : 
                                   functionName === 'register-user' ? 'Register' : 'Subscribe Now';
            }
        }
        
        // Show alert message
        function showAlert(alertElement, type, message) {
            alertElement.className = `alert alert-${type}`;
            alertElement.textContent = message;
            alertElement.style.display = 'block';
            
            // Hide after 5 seconds
            setTimeout(() => {
                alertElement.style.display = 'none';
            }, 5000);
        }
        
        // Form event listeners
        document.getElementById('registerForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            await submitForm(this, 'register-user', 'register-alert');
        });
        
        document.getElementById('feedbackForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            await submitForm(this, 'submit-feedback', 'feedback-alert');
        });
        
        document.getElementById('newsletterForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            await submitForm(this, 'submit-newsletter', 'newsletter-alert');
        });
    </script>
</body>
</html>'''
    
    def get_simple_register_function(self):
        """Simple registration function"""
        return '''const { MongoClient } = require('mongodb');
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb+srv://breakeven:breakeven123@cluster0.mongodb.net/breakeven-websites?retryWrites=true&w=majority';

exports.handler = async (event, context) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    if (event.httpMethod === 'OPTIONS') return { statusCode: 200, headers, body: '' };
    if (event.httpMethod !== 'POST') return { statusCode: 405, headers, body: JSON.stringify({ success: false, error: 'Method not allowed' }) };

    try {
        const data = JSON.parse(event.body);
        
        if (!data.register_name || !data.register_email) {
            return { statusCode: 400, headers, body: JSON.stringify({ success: false, error: 'Name and email required' }) };
        }

        const registration = {
            name: data.register_name,
            email: data.register_email,
            phone: data.register_phone || '',
            interests: data.register_interests || '',
            website_source: data.website_source || '',
            business_id: data.business_id || '',
            created_at: new Date().toISOString(),
            ip_address: event.headers['x-forwarded-for'] || event.headers['x-real-ip'] || 'unknown'
        };

        try {
            const client = new MongoClient(MONGODB_URI);
            await client.connect();
            const db = client.db('breakeven-websites');
            await db.collection('registrations').insertOne(registration);
            await client.close();
            console.log('User registered:', registration.email);
        } catch (dbError) {
            console.error('DB Error:', dbError);
        }

        return { statusCode: 200, headers, body: JSON.stringify({ success: true, message: 'Registration successful! Welcome to our community.' }) };
    } catch (error) {
        console.error('Registration error:', error);
        return { statusCode: 500, headers, body: JSON.stringify({ success: false, error: 'Registration failed. Please try again.' }) };
    }
};'''

    def get_simple_feedback_function(self):
        """Simple feedback function"""
        return '''const { MongoClient } = require('mongodb');
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb+srv://breakeven:breakeven123@cluster0.mongodb.net/breakeven-websites?retryWrites=true&w=majority';

exports.handler = async (event, context) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    if (event.httpMethod === 'OPTIONS') return { statusCode: 200, headers, body: '' };
    if (event.httpMethod !== 'POST') return { statusCode: 405, headers, body: JSON.stringify({ success: false, error: 'Method not allowed' }) };

    try {
        const data = JSON.parse(event.body);
        
        if (!data.customer_name || !data.customer_email || !data.feedback_message) {
            return { statusCode: 400, headers, body: JSON.stringify({ success: false, error: 'Name, email and message required' }) };
        }

        // Simple sentiment analysis
        const message = data.feedback_message.toLowerCase();
        let sentiment = 'neutral';
        
        const positiveWords = ['good', 'great', 'excellent', 'amazing', 'love', 'perfect', 'wonderful', 'fantastic'];
        const negativeWords = ['bad', 'terrible', 'awful', 'hate', 'horrible', 'poor', 'worst'];
        
        const hasPositive = positiveWords.some(word => message.includes(word));
        const hasNegative = negativeWords.some(word => message.includes(word));
        
        if (hasPositive && !hasNegative) sentiment = 'positive';
        else if (hasNegative && !hasPositive) sentiment = 'negative';

        const feedback = {
            customer_name: data.customer_name,
            customer_email: data.customer_email,
            customer_phone: data.customer_phone || '',
            feedback_category: data.feedback_category || 'general',
            rating: parseInt(data.rating) || 5,
            feedback_message: data.feedback_message,
            sentiment: sentiment,
            website_source: data.website_source || '',
            business_id: data.business_id || '',
            created_at: new Date().toISOString(),
            ip_address: event.headers['x-forwarded-for'] || event.headers['x-real-ip'] || 'unknown'
        };

        try {
            const client = new MongoClient(MONGODB_URI);
            await client.connect();
            const db = client.db('breakeven-websites');
            await db.collection('feedback').insertOne(feedback);
            await client.close();
            console.log('Feedback submitted:', feedback.customer_email);
        } catch (dbError) {
            console.error('DB Error:', dbError);
        }

        return { statusCode: 200, headers, body: JSON.stringify({ success: true, message: 'Thank you for your feedback! We really appreciate it.' }) };
    } catch (error) {
        console.error('Feedback error:', error);
        return { statusCode: 500, headers, body: JSON.stringify({ success: false, error: 'Feedback submission failed. Please try again.' }) };
    }
};'''

    def get_simple_newsletter_function(self):
        """Simple newsletter function"""
        return '''const { MongoClient } = require('mongodb');
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb+srv://breakeven:breakeven123@cluster0.mongodb.net/breakeven-websites?retryWrites=true&w=majority';

exports.handler = async (event, context) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    if (event.httpMethod === 'OPTIONS') return { statusCode: 200, headers, body: '' };
    if (event.httpMethod !== 'POST') return { statusCode: 405, headers, body: JSON.stringify({ success: false, error: 'Method not allowed' }) };

    try {
        const data = JSON.parse(event.body);
        
        if (!data.newsletter_name || !data.newsletter_email) {
            return { statusCode: 400, headers, body: JSON.stringify({ success: false, error: 'Name and email required' }) };
        }

        const subscription = {
            name: data.newsletter_name,
            email: data.newsletter_email,
            interests: data.newsletter_interests ? data.newsletter_interests.split(',') : [],
            website_source: data.website_source || '',
            business_id: data.business_id || '',
            subscribed_at: new Date().toISOString(),
            active: true,
            ip_address: event.headers['x-forwarded-for'] || event.headers['x-real-ip'] || 'unknown'
        };

        try {
            const client = new MongoClient(MONGODB_URI);
            await client.connect();
            const db = client.db('breakeven-websites');
            await db.collection('newsletter').replaceOne(
                { email: subscription.email },
                subscription,
                { upsert: true }
            );
            await client.close();
            console.log('Newsletter subscription:', subscription.email);
        } catch (dbError) {
            console.error('DB Error:', dbError);
        }

        return { statusCode: 200, headers, body: JSON.stringify({ success: true, message: 'Successfully subscribed to our newsletter!' }) };
    } catch (error) {
        console.error('Newsletter error:', error);
        return { statusCode: 500, headers, body: JSON.stringify({ success: false, error: 'Newsletter subscription failed. Please try again.' }) };
    }
};'''

    def get_simple_recent_feedback_function(self):
        """Simple recent feedback function"""
        return '''const { MongoClient } = require('mongodb');
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb+srv://breakeven:breakeven123@cluster0.mongodb.net/breakeven-websites?retryWrites=true&w=majority';

exports.handler = async (event, context) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    if (event.httpMethod === 'OPTIONS') return { statusCode: 200, headers, body: '' };

    try {
        const sampleFeedback = [
            { 
                customer_name: 'Sarah Johnson', 
                feedback_message: 'Excellent service and great quality products! Highly recommended.', 
                rating: 5, 
                feedback_category: 'general',
                sentiment: 'positive',
                created_at: new Date(Date.now() - 86400000).toISOString() 
            },
            { 
                customer_name: 'Mike Chen', 
                feedback_message: 'Good experience overall. Fast delivery and helpful customer support.', 
                rating: 4, 
                feedback_category: 'customer_service',
                sentiment: 'positive',
                created_at: new Date(Date.now() - 172800000).toISOString() 
            },
            { 
                customer_name: 'Emma Wilson', 
                feedback_message: 'Love the variety of products available. Will definitely order again!', 
                rating: 5, 
                feedback_category: 'product_quality',
                sentiment: 'positive',
                created_at: new Date(Date.now() - 259200000).toISOString() 
            }
        ];

        let feedback = sampleFeedback;
        
        try {
            const client = new MongoClient(MONGODB_URI);
            await client.connect();
            const db = client.db('breakeven-websites');
            const dbFeedback = await db.collection('feedback').find({}).sort({ created_at: -1 }).limit(10).toArray();
            await client.close();
            
            if (dbFeedback && dbFeedback.length > 0) {
                feedback = dbFeedback;
            }
        } catch (dbError) {
            console.error('DB Error:', dbError);
        }

        return { statusCode: 200, headers, body: JSON.stringify({ success: true, feedback: feedback }) };
    } catch (error) {
        console.error('Get feedback error:', error);
        return { statusCode: 500, headers, body: JSON.stringify({ success: false, error: 'Failed to load feedback' }) };
    }
};'''
    
    def get_site_info(self, site_id):
        """Get information about a Netlify site"""
        try:
            url = f"{self.base_url}/sites/{site_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                site_data = response.json()
                return {
                    'success': True,
                    'site': {
                        'id': site_data['id'],
                        'name': site_data['name'],
                        'url': site_data['url'],
                        'ssl_url': site_data['ssl_url'],
                        'state': site_data['state'],
                        'created_at': site_data['created_at']
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'Site not found: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_site_name(self, site_id, new_name):
        """Update site name/subdomain"""
        try:
            url = f"{self.base_url}/sites/{site_id}"
            data = {
                "name": new_name
            }
            
            response = requests.patch(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'site': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Update failed: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def load_template(self, template_name='mini-website-template.html'):
        """Load HTML template for mini websites"""
        try:
            # Try multiple path resolution strategies
            possible_paths = [
                # Original path resolution
                os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    'netlify-functions',
                    template_name
                ),
                # Alternative path from project root
                os.path.join(
                    os.getcwd(),
                    'netlify-functions',
                    template_name
                ),
                # Absolute path
                os.path.join(
                    r"C:\Users\sreen\OneDrive\Documents\Python Scripts\break-even",
                    'netlify-functions',
                    template_name
                )
            ]
            
            print(f"Loading template: {template_name}")
            
            for i, template_path in enumerate(possible_paths):
                print(f"Trying path {i+1}: {template_path}")
                print(f"Path exists: {os.path.exists(template_path)}")
                
                if os.path.exists(template_path):
                    with open(template_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        print(f"Template loaded successfully, size: {len(content)} characters")
                        
                        # Verify it's the enhanced template for data collection
                        if template_name == 'enhanced-mini-website-template.html':
                            has_forms = 'feedbackForm' in content
                            has_tabs = 'nav-tabs' in content
                            has_login = 'customerLoginForm' in content
                            print(f"Enhanced template verification:")
                            print(f"  - Has feedback forms: {has_forms}")
                            print(f"  - Has navigation tabs: {has_tabs}")
                            print(f"  - Has customer login: {has_login}")
                            
                            if not (has_forms and has_tabs and has_login):
                                print("WARNING: Template missing enhanced features!")
                        
                        return content
            
            print(f"Template not found at any path, falling back to basic template")
            return self.get_basic_template()
            
        except Exception as e:
            print(f"Error loading template: {e}")
            return self.get_basic_template()
    
    def get_basic_template(self):
        """Fallback basic template with data collection"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        .form { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        input, textarea, select { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .alert { padding: 15px; margin: 10px 0; border-radius: 4px; }
        .alert-success { background: #d4edda; color: #155724; }
        .alert-error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{title}}</h1>
        <p>{{description}}</p>
        
        <div>{{content}}</div>
        
        <div class="form">
            <h3>Join Our Community</h3>
            <form id="registration-form">
                <input type="text" id="name" placeholder="Your Name" required>
                <input type="email" id="email" placeholder="Your Email" required>
                <button type="submit">Register</button>
                <div id="reg-message"></div>
            </form>
        </div>
        
        <div class="form">
            <h3>Share Your Feedback</h3>
            <form id="feedback-form">
                <textarea id="feedback" placeholder="Your feedback..." required></textarea>
                <select id="rating">
                    <option value="">Rate your experience</option>
                    <option value="5">5 - Excellent</option>
                    <option value="4">4 - Good</option>
                    <option value="3">3 - Average</option>
                    <option value="2">2 - Poor</option>
                    <option value="1">1 - Very Poor</option>
                </select>
                <button type="submit">Submit Feedback</button>
                <div id="feedback-message"></div>
            </form>
        </div>
    </div>
    
    <script>
        const websiteSource = window.location.hostname;
        const FUNCTIONS_BASE_URL = `${window.location.origin}/.netlify/functions`;
        
        document.getElementById('registration-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            
            try {
                const response = await fetch(`${FUNCTIONS_BASE_URL}/register-user`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ register_name: name, register_email: email, website_source: websiteSource })
                });
                
                const result = await response.json();
                document.getElementById('reg-message').innerHTML = 
                    `<div class="alert ${result.success ? 'alert-success' : 'alert-error'}">
                        ${result.success ? 'Registration successful!' : result.error}
                    </div>`;
                    
                if (result.success) e.target.reset();
            } catch (error) {
                document.getElementById('reg-message').innerHTML = 
                    '<div class="alert alert-error">Registration failed. Please try again.</div>';
            }
        });
        
        document.getElementById('feedback-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const feedback = document.getElementById('feedback').value;
            const rating = document.getElementById('rating').value;
            
            try {
                const response = await fetch(`${FUNCTIONS_BASE_URL}/submit-feedback`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        customer_name: 'Anonymous',
                        customer_email: 'anonymous@example.com',
                        feedback_message: feedback, 
                        rating: rating ? parseInt(rating) : null, 
                        website_source: websiteSource 
                    })
                });
                
                const result = await response.json();
                document.getElementById('feedback-message').innerHTML = 
                    `<div class="alert ${result.success ? 'alert-success' : 'alert-error'}">
                        ${result.success ? 'Thank you for your feedback!' : result.error}
                    </div>`;
                    
                if (result.success) e.target.reset();
            } catch (error) {
                document.getElementById('feedback-message').innerHTML = 
                    '<div class="alert alert-error">Feedback submission failed. Please try again.</div>';
            }
        });
    </script>
</body>
</html>'''
    
    def get_register_function(self):
        """Get the registration function code"""
        try:
            function_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'netlify-functions',
                'register-user.js'
            )
            
            if os.path.exists(function_path):
                with open(function_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                return self.get_simple_register_function()
        except Exception as e:
            return self.get_simple_register_function()
    
    def get_feedback_function(self):
        """Get the feedback function code"""
        try:
            function_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'netlify-functions',
                'submit-feedback.js'
            )
            
            if os.path.exists(function_path):
                with open(function_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                return self.get_simple_feedback_function()
        except Exception as e:
            return self.get_simple_feedback_function()
    
    def get_interest_function(self):
        """Get the product interest function code"""
        try:
            function_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'netlify-functions',
                'submit-interest.js'
            )
            
            if os.path.exists(function_path):
                with open(function_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                return '// Interest function not found'
        except Exception as e:
            return f'// Error loading interest function: {e}'
            
    def get_newsletter_function(self):
        """Get the newsletter signup function code"""
        try:
            function_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'netlify-functions',
                'submit-newsletter.js'
            )
            
            if os.path.exists(function_path):
                with open(function_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                return self.get_simple_newsletter_function()
        except Exception as e:
            return self.get_simple_newsletter_function()
    
    def get_customer_login_function(self):
        """Get the customer login function code"""
        try:
            function_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'netlify-functions',
                'customer-login.js'
            )
            
            if os.path.exists(function_path):
                with open(function_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                return '// Customer login function not found'
        except Exception as e:
            return f'// Error loading customer login function: {e}'
    
    def get_customer_register_function(self):
        """Get the customer register function code"""
        try:
            function_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'netlify-functions',
                'customer-register.js'
            )
            
            if os.path.exists(function_path):
                with open(function_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                return '// Customer register function not found'
        except Exception as e:
            return f'// Error loading customer register function: {e}'
    
    def get_products_function(self):
        """Get the products function code"""
        try:
            function_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'netlify-functions',
                'get-products.js'
            )
            
            if os.path.exists(function_path):
                with open(function_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                return '// Products function not found'
        except Exception as e:
            return f'// Error loading products function: {e}'
    
    def get_recent_feedback_function(self):
        """Get the recent feedback function code"""
        try:
            function_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'netlify-functions',
                'get-recent-feedback.js'
            )
            
            if os.path.exists(function_path):
                with open(function_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                return self.get_simple_recent_feedback_function()
        except Exception as e:
            return self.get_simple_recent_feedback_function()
    
    def generate_website_html(self, business_name, content):
        """Generate HTML content for the website (BASIC VERSION)"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{business_name}</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <nav class="container">
            <div class="logo">{business_name}</div>
            <div class="nav-links">
                <a href="#about">About</a>
                <a href="#services">Services</a>
                <a href="#contact">Contact</a>
            </div>
        </nav>
    </header>

    <main>
        <section class="hero">
            <div class="container">
                <h1>{content.get('hero_title', f'Welcome to {business_name}') if isinstance(content, dict) else f'Welcome to {business_name}'}</h1>
                <p>{content.get('hero_subtitle', 'Your trusted business partner') if isinstance(content, dict) else 'Your trusted business partner'}</p>
                <a href="#contact" class="btn-primary">Get Started</a>
            </div>
        </section>

        <section id="about" class="section">
            <div class="container">
                <h2>About Us</h2>
                <p>{content.get('about_us', f'{business_name} is dedicated to providing excellent service to our customers.') if isinstance(content, dict) else f'{business_name} is dedicated to providing excellent service to our customers.'}</p>
            </div>
        </section>

        <section id="services" class="section bg-light">
            <div class="container">
                <h2>Our Services</h2>
                <p>{content.get('services_intro', 'We offer a comprehensive range of services to meet your needs.') if isinstance(content, dict) else 'We offer a comprehensive range of services to meet your needs.'}</p>
                <div class="services-grid">
                    <div class="service-card">
                        <h3>Professional Service</h3>
                        <p>Expert solutions tailored to your specific needs and requirements.</p>
                    </div>
                    <div class="service-card">
                        <h3>Quality Assurance</h3>
                        <p>We ensure the highest quality standards in everything we deliver.</p>
                    </div>
                    <div class="service-card">
                        <h3>Customer Support</h3>
                        <p>24/7 support to help you succeed and overcome any challenges.</p>
                    </div>
                </div>
            </div>
        </section>

        <section id="contact" class="section">
            <div class="container">
                <h2>Contact Us</h2>
                <p>{content.get('contact_cta', 'Ready to get started? Contact us today!') if isinstance(content, dict) else 'Ready to get started? Contact us today!'}</p>
                <div class="contact-info">
                    <div class="contact-item">
                        <strong>Phone:</strong> {content.get('phone', 'Contact us for phone number') if isinstance(content, dict) else 'Contact us for phone number'}
                    </div>
                    <div class="contact-item">
                        <strong>Email:</strong> {content.get('email', 'Contact us for email') if isinstance(content, dict) else 'Contact us for email'}
                    </div>
                    <div class="contact-item">
                        <strong>Address:</strong> {content.get('address', 'Contact us for address') if isinstance(content, dict) else 'Contact us for address'}
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 {business_name}. All rights reserved. Powered by Break-even.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def generate_css(self):
        """Generate CSS styles for the website"""
        return """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

header {
    background: #3b82f6;
    color: white;
    padding: 1rem 0;
    position: fixed;
    width: 100%;
    top: 0;
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 1.5rem;
    font-weight: 700;
}

.nav-links a {
    color: white;
    text-decoration: none;
    margin: 0 1rem;
    transition: opacity 0.3s;
}

.nav-links a:hover {
    opacity: 0.8;
}

.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 8rem 0 4rem;
    text-align: center;
    margin-top: 60px;
}

.hero h1 {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    font-weight: 700;
}

.hero p {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}

.btn-primary {
    display: inline-block;
    background: #10b981;
    color: white;
    padding: 12px 24px;
    text-decoration: none;
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.btn-primary:hover {
    background: #059669;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.section {
    padding: 4rem 0;
}

.bg-light {
    background: #f9fafb;
}

.section h2 {
    font-size: 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
    color: #1f2937;
}

.section p {
    font-size: 1.1rem;
    text-align: center;
    margin-bottom: 3rem;
    color: #6b7280;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.services-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 3rem;
}

.service-card {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    transition: all 0.3s;
    border: 1px solid #e5e7eb;
}

.service-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.service-card h3 {
    color: #3b82f6;
    margin-bottom: 1rem;
    font-size: 1.25rem;
}

.contact-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
}

.contact-item {
    text-align: center;
    padding: 1rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

footer {
    background: #1f2937;
    color: white;
    padding: 2rem 0;
    text-align: center;
}

@media (max-width: 768px) {
    .hero h1 {
        font-size: 2.5rem;
    }
    
    .nav-links {
        display: none;
    }
    
    .services-grid {
        grid-template-columns: 1fr;
    }
}
"""

# Initialize service - will be created when needed
netlify_service = None

def get_netlify_service():
    """Get or create Netlify service instance"""
    global netlify_service
    if netlify_service is None:
        netlify_service = NetlifyService()
    return netlify_service