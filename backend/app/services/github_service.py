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
        """Generate premium HTML content using SchemaRenderer + SchemaBridge.

        Instead of a hardcoded basic template, this now:
        1. Builds a proper JSON schema from the business info
        2. Renders it through the SchemaRenderer (premium Tailwind templates)
        3. Injects the child→parent analytics tracking snippet
        """
        try:
            from app.services.schema_bridge import SchemaBridge
            from app.services.schema_renderer import SchemaRenderer
            from app.services.tracking_snippet import TrackingSnippet

            # Merge business_name into content for the bridge
            bridge_info = dict(content) if isinstance(content, dict) else {}
            bridge_info.setdefault("website_name", business_name)
            bridge_info.setdefault("site_name", business_name)

            schema = SchemaBridge.build_schema_dict(
                business_id=bridge_info.get("business_id", ""),
                business_info=bridge_info,
            )
            html = SchemaRenderer.render(schema)

            # Inject tracking snippet for child→parent analytics
            html = TrackingSnippet.inject(
                html,
                business_id=bridge_info.get("business_id", ""),
            )
            return html

        except Exception as e:
            # Fallback: if SchemaRenderer fails, return a minimal valid page
            import logging
            logging.getLogger(__name__).warning(
                f"SchemaRenderer fallback for GitHub deploy: {e}"
            )
            return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{business_name}</title></head>
<body><h1>{business_name}</h1><p>{content.get('hero_subtitle', '') if isinstance(content, dict) else ''}</p></body>
</html>"""

# Initialize service - will be created when needed
github_service = None

def get_github_service():
    """Get or create GitHub service instance"""
    global github_service
    if github_service is None:
        github_service = GitHubService()
    return github_service
