"""
Gemini AI Service for Break-even App
Provides AI-powered content generation, business insights, and text analysis
"""

import requests
from flask import current_app
import json

class GeminiAIService:
    
    def __init__(self, api_key=None):
        self._api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    @property
    def api_key(self):
        if self._api_key:
            return self._api_key
        try:
            from flask import current_app
            return current_app.config.get('GEMINI_API_KEY')
        except RuntimeError:
            # Fallback when outside application context
            from app.config import Config
            return Config.GEMINI_API_KEY
    
    def generate_content(self, prompt, max_tokens=1000):
        """Generate content using Gemini AI"""
        try:
            headers = {
                'Content-Type': 'application/json',
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": 0.7,
                    "topP": 0.8,
                    "topK": 40
                }
            }
            
            url = f"{self.base_url}?key={self.api_key}"
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    return {
                        'success': True,
                        'content': result['candidates'][0]['content']['parts'][0]['text']
                    }
            
            return {
                'success': False,
                'error': f'API Error: {response.status_code} - {response.text}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_business_description(self, business_name, business_type, key_features=None):
        """Generate a compelling business description"""
        prompt = f"""
        Create a professional and engaging business description for:
        
        Business Name: {business_name}
        Business Type: {business_type}
        Key Features: {key_features or 'Not specified'}
        
        Requirements:
        - Make it compelling and professional
        - Highlight unique value propositions
        - Keep it concise (2-3 sentences)
        - Focus on customer benefits
        - Make it suitable for a website homepage
        
        Generate only the description text, no additional formatting.
        """
        
        return self.generate_content(prompt, max_tokens=500)
    
    def generate_website_content(self, business_info):
        """Generate website content sections"""
        prompt = f"""
        Create website content for a {business_info.get('business_type', 'business')} called "{business_info.get('name', 'Business')}".
        
        Business Details:
        - Location: {business_info.get('area', 'Not specified')}
        - Contact: {business_info.get('contact_info', {}).get('phone', 'Not provided')}
        - Services: {business_info.get('services', 'Not specified')}
        
        Generate the following sections in JSON format:
        {{
            "hero_title": "Main headline for homepage",
            "hero_subtitle": "Supporting text for hero section",
            "about_us": "About us section (2-3 sentences)",
            "services_intro": "Introduction for services section",
            "contact_cta": "Call-to-action text for contact section"
        }}
        
        Make it professional, engaging, and specific to this business type.
        """
        
        result = self.generate_content(prompt, max_tokens=800)
        
        if result['success']:
            try:
                # Try to parse JSON from the response
                content = result['content']
                # Clean up the response to extract JSON
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != 0:
                    json_content = content[start:end]
                    parsed_content = json.loads(json_content)
                    result['parsed_content'] = parsed_content
            except:
                # If JSON parsing fails, return the raw content
                pass
        
        return result
    
    def analyze_business_trends(self, business_type, location=None):
        """Analyze business trends and provide insights"""
        prompt = f"""
        Provide business insights and trends for a {business_type} business.
        Location: {location or 'General'}
        
        Please provide:
        1. Current market trends (2-3 key points)
        2. Growth opportunities (2-3 suggestions)
        3. Key challenges to watch out for
        4. Marketing recommendations
        
        Keep it practical and actionable for a small business owner.
        Format as clear, numbered points.
        """
        
        return self.generate_content(prompt, max_tokens=600)
    
    def generate_social_media_content(self, business_name, business_type, occasion=None):
        """Generate social media posts"""
        occasion_text = f" for {occasion}" if occasion else ""
        
        prompt = f"""
        Create 3 engaging social media posts for {business_name}, a {business_type} business{occasion_text}.
        
        Requirements:
        - Make them engaging and shareable
        - Include relevant hashtags
        - Keep each post under 280 characters
        - Make them different in tone (professional, casual, promotional)
        
        Format as:
        Post 1: [content]
        Post 2: [content]
        Post 3: [content]
        """
        
        return self.generate_content(prompt, max_tokens=500)

# Initialize service - will be created when needed
gemini_service = None

def get_gemini_service():
    """Get or create Gemini service instance"""
    global gemini_service
    if gemini_service is None:
        gemini_service = GeminiAIService()
    return gemini_service
