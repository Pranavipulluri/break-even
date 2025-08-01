
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/breakeven'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # OpenAI API
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Gemini AI API
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or 'AIzaSyD25Qkutz-mjpOz8ELQVWmocw0hBoFAG2A'
    
    # GitHub API
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN') or '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'
    
    # Netlify API
    NETLIFY_API_KEY = os.environ.get('NETLIFY_API_KEY') or 'nfp_tHbhsuDnH1k8SLeyb7VeqtGxDaoHqyxBadfc'
    
    # Website builder settings
    WEBSITE_BASE_URL = os.environ.get('WEBSITE_BASE_URL') or 'http://localhost:3001'
    FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://localhost:3001'
