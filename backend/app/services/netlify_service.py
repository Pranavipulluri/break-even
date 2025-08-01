"""
Netlify API Service for Break-even App
Provides website deployment and hosting through Netlify
"""

import requests
from flask import current_app
import zipfile
import io
import base64
import random
import string
from datetime import datetime

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
    
    def create_and_deploy_website(self, business_name, website_content):
        """Create a site and deploy website content"""
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
            
            # Create website files
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
    
    def generate_website_html(self, business_name, content):
        """Generate HTML content for the website"""
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
                <h1>{content.get('hero_title', f'Welcome to {business_name}')}</h1>
                <p>{content.get('hero_subtitle', 'Your trusted business partner')}</p>
                <a href="#contact" class="btn-primary">Get Started</a>
            </div>
        </section>

        <section id="about" class="section">
            <div class="container">
                <h2>About Us</h2>
                <p>{content.get('about_us', f'{business_name} is dedicated to providing excellent service to our customers.')}</p>
            </div>
        </section>

        <section id="services" class="section bg-light">
            <div class="container">
                <h2>Our Services</h2>
                <p>{content.get('services_intro', 'We offer a comprehensive range of services to meet your needs.')}</p>
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
                <p>{content.get('contact_cta', 'Ready to get started? Contact us today!')}</p>
                <div class="contact-info">
                    <div class="contact-item">
                        <strong>Phone:</strong> {content.get('phone', 'Contact us for phone number')}
                    </div>
                    <div class="contact-item">
                        <strong>Email:</strong> {content.get('email', 'Contact us for email')}
                    </div>
                    <div class="contact-item">
                        <strong>Address:</strong> {content.get('address', 'Contact us for address')}
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
