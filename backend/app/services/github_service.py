"""
GitHub API Service for Break-even App
Provides GitHub integration for code deployment and repository management
"""

import requests
from flask import current_app
import base64
import json

class GitHubService:
    
    def __init__(self, token=None):
        self._token = token
        self.base_url = "https://api.github.com"
    
    @property
    def token(self):
        if self._token:
            return self._token
        try:
            from flask import current_app
            return current_app.config.get('GITHUB_TOKEN')
        except RuntimeError:
            # Fallback when outside application context
            from app.config import Config
            return Config.GITHUB_TOKEN
    
    @property
    def headers(self):
        return {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
    
    def create_repository(self, repo_name, description="", private=True):
        """Create a new GitHub repository"""
        try:
            url = f"{self.base_url}/user/repos"
            data = {
                "name": repo_name,
                "description": description,
                "private": private,
                "has_issues": True,
                "has_projects": True,
                "has_wiki": False,
                "auto_init": True
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                repo_data = response.json()
                return {
                    'success': True,
                    'repository': {
                        'name': repo_data['name'],
                        'full_name': repo_data['full_name'],
                        'clone_url': repo_data['clone_url'],
                        'html_url': repo_data['html_url'],
                        'default_branch': repo_data['default_branch']
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'GitHub API Error: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_file(self, repo_full_name, file_path, content, commit_message="Add file"):
        """Upload a file to GitHub repository"""
        try:
            # Encode content to base64
            if isinstance(content, str):
                content_encoded = base64.b64encode(content.encode()).decode()
            else:
                content_encoded = base64.b64encode(content).decode()
            
            url = f"{self.base_url}/repos/{repo_full_name}/contents/{file_path}"
            
            data = {
                "message": commit_message,
                "content": content_encoded
            }
            
            response = requests.put(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'file_info': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Upload failed: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_website_repository(self, business_name, website_content):
        """Create a complete website repository with HTML files"""
        try:
            # Sanitize repository name
            repo_name = f"{business_name.lower().replace(' ', '-')}-website"
            
            # Create repository
            repo_result = self.create_repository(
                repo_name, 
                f"Website for {business_name}",
                private=False  # Public for GitHub Pages
            )
            
            if not repo_result['success']:
                return repo_result
            
            repo_info = repo_result['repository']
            
            # Generate HTML content
            html_content = self.generate_website_html(business_name, website_content)
            
            # Upload index.html
            upload_result = self.upload_file(
                repo_info['full_name'],
                'index.html',
                html_content,
                f"Initial website for {business_name}"
            )
            
            if upload_result['success']:
                # Enable GitHub Pages
                pages_result = self.enable_github_pages(repo_info['full_name'])
                
                return {
                    'success': True,
                    'repository': repo_info,
                    'website_url': f"https://{repo_info['full_name'].split('/')[0]}.github.io/{repo_name}",
                    'github_pages_enabled': pages_result['success']
                }
            else:
                return upload_result
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def enable_github_pages(self, repo_full_name):
        """Enable GitHub Pages for a repository"""
        try:
            url = f"{self.base_url}/repos/{repo_full_name}/pages"
            data = {
                "source": {
                    "branch": "main",
                    "path": "/"
                }
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'pages_info': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Pages setup failed: {response.status_code} - {response.text}'
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
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        header {{ background: #3b82f6; color: white; padding: 1rem 0; }}
        nav {{ display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 1.5rem; font-weight: bold; }}
        .hero {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 4rem 0; text-align: center; }}
        .hero h1 {{ font-size: 3rem; margin-bottom: 1rem; }}
        .hero p {{ font-size: 1.2rem; margin-bottom: 2rem; }}
        .btn {{ display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; transition: background 0.3s; }}
        .btn:hover {{ background: #059669; }}
        .section {{ padding: 4rem 0; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }}
        .card {{ background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        footer {{ background: #1f2937; color: white; padding: 2rem 0; text-align: center; }}
    </style>
</head>
<body>
    <header>
        <nav class="container">
            <div class="logo">{business_name}</div>
            <div>
                <a href="#about" style="color: white; text-decoration: none; margin: 0 1rem;">About</a>
                <a href="#services" style="color: white; text-decoration: none; margin: 0 1rem;">Services</a>
                <a href="#contact" style="color: white; text-decoration: none; margin: 0 1rem;">Contact</a>
            </div>
        </nav>
    </header>

    <main>
        <section class="hero">
            <div class="container">
                <h1>{content.get('hero_title', f'Welcome to {business_name}')}</h1>
                <p>{content.get('hero_subtitle', 'Your trusted business partner')}</p>
                <a href="#contact" class="btn">Get Started</a>
            </div>
        </section>

        <section id="about" class="section">
            <div class="container">
                <h2>About Us</h2>
                <p>{content.get('about_us', f'{business_name} is dedicated to providing excellent service to our customers.')}</p>
            </div>
        </section>

        <section id="services" class="section" style="background: #f9fafb;">
            <div class="container">
                <h2>Our Services</h2>
                <p>{content.get('services_intro', 'We offer a comprehensive range of services to meet your needs.')}</p>
                <div class="grid">
                    <div class="card">
                        <h3>Service 1</h3>
                        <p>Professional service tailored to your needs.</p>
                    </div>
                    <div class="card">
                        <h3>Service 2</h3>
                        <p>Expert solutions for your business challenges.</p>
                    </div>
                    <div class="card">
                        <h3>Service 3</h3>
                        <p>Innovative approaches to drive your success.</p>
                    </div>
                </div>
            </div>
        </section>

        <section id="contact" class="section">
            <div class="container">
                <h2>Contact Us</h2>
                <p>{content.get('contact_cta', 'Ready to get started? Contact us today!')}</p>
                <div class="grid">
                    <div>
                        <h3>Get In Touch</h3>
                        <p>Phone: {content.get('phone', 'Contact us for phone number')}</p>
                        <p>Email: {content.get('email', 'Contact us for email')}</p>
                        <p>Address: {content.get('address', 'Contact us for address')}</p>
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

# Initialize service - will be created when needed
github_service = None

def get_github_service():
    """Get or create GitHub service instance"""
    global github_service
    if github_service is None:
        github_service = GitHubService()
    return github_service
