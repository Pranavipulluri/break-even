"""
Groq AI Service for Break-even App
Provides AI-powered image generation using Groq API
"""

import requests
import base64
import io
from PIL import Image, ImageDraw, ImageFont
from flask import current_app
import os
from datetime import datetime
import json

class GroqService:
    
    def __init__(self, api_key=None):
        self._api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"
    
    @property
    def api_key(self):
        if self._api_key:
            return self._api_key
        try:
            from flask import current_app
            return current_app.config.get('GROQ_API_KEY')
        except RuntimeError:
            # Fallback when outside application context
            return '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'
    
    def generate_image_description(self, prompt, business_type="", style="professional"):
        """Generate detailed image description using Groq AI"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Create detailed prompt for image description
            system_prompt = f"""You are an expert graphic designer and visual artist. Create a detailed, vivid description for generating a {style} image for a {business_type} business. 
            
            Your description should include:
            - Visual composition and layout
            - Color scheme and mood
            - Specific design elements
            - Typography style (if text is needed)
            - Professional quality details
            - Brand-appropriate aesthetic
            
            Keep it concise but descriptive, focusing on visual elements that would create a professional business image."""
            
            user_prompt = f"Create a detailed visual description for: {prompt}"
            
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "model": "llama3-8b-8192",
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                description = result['choices'][0]['message']['content'].strip()
                
                return {
                    'success': True,
                    'description': description,
                    'original_prompt': prompt
                }
            else:
                print(f"❌ Groq API Error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Groq API error: {response.status_code}'
                }
                
        except Exception as e:
            print(f"❌ Groq service error: {e}")
            return {
                'success': False,
                'error': f'Service error: {str(e)}'
            }
    
    def generate_business_poster_concept(self, business_name, business_type, message="", style="professional"):
        """Generate business poster concept using Groq AI"""
        try:
            prompt = f"Create a professional {style} poster design concept for '{business_name}', a {business_type} business"
            if message:
                prompt += f" with the message: '{message}'"
            
            result = self.generate_image_description(prompt, business_type, style)
            
            if result['success']:
                # Create a simple poster mock-up using PIL
                poster_image = self._create_poster_mockup(
                    business_name, 
                    business_type, 
                    message, 
                    result['description']
                )
                
                return {
                    'success': True,
                    'concept': result['description'],
                    'poster_image': poster_image,
                    'business_name': business_name,
                    'business_type': business_type,
                    'style': style
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Poster generation error: {str(e)}'
            }
    
    def generate_product_image_concept(self, product_name, product_description="", style="product photography"):
        """Generate product image concept using Groq AI"""
        try:
            prompt = f"Create a {style} concept for {product_name}"
            if product_description:
                prompt += f": {product_description}"
            
            result = self.generate_image_description(prompt, "product", style)
            
            if result['success']:
                # Create a simple product image mock-up
                product_image = self._create_product_mockup(
                    product_name,
                    product_description,
                    result['description']
                )
                
                return {
                    'success': True,
                    'concept': result['description'],
                    'product_image': product_image,
                    'product_name': product_name,
                    'style': style
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Product image generation error: {str(e)}'
            }
    
    def generate_marketing_banner_concept(self, business_name, message, dimensions="web", style="modern"):
        """Generate marketing banner concept using Groq AI"""
        try:
            prompt = f"Create a {style} {dimensions} banner design for '{business_name}' with message: '{message}'"
            
            result = self.generate_image_description(prompt, "marketing", style)
            
            if result['success']:
                # Create banner mock-up
                banner_image = self._create_banner_mockup(
                    business_name,
                    message,
                    dimensions,
                    result['description']
                )
                
                return {
                    'success': True,
                    'concept': result['description'],
                    'banner_image': banner_image,
                    'business_name': business_name,
                    'message': message,
                    'dimensions': dimensions,
                    'style': style
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Banner generation error: {str(e)}'
            }
    
    def _create_poster_mockup(self, business_name, business_type, message, description):
        """Create a simple poster mockup using PIL"""
        try:
            # Create poster image
            width, height = 800, 1000
            image = Image.new('RGB', (width, height), color='#f0f0f0')
            draw = ImageDraw.Draw(image)
            
            # Try to use a font, fallback to default if not available
            try:
                title_font = ImageFont.truetype("arial.ttf", 48)
                subtitle_font = ImageFont.truetype("arial.ttf", 24)
                desc_font = ImageFont.truetype("arial.ttf", 16)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                desc_font = ImageFont.load_default()
            
            # Add business name
            draw.text((50, 100), business_name, fill='#333333', font=title_font)
            
            # Add business type
            draw.text((50, 180), f"{business_type.title()} Business", fill='#666666', font=subtitle_font)
            
            # Add message if provided
            if message:
                draw.text((50, 250), message, fill='#444444', font=subtitle_font)
            
            # Add concept description (wrapped)
            desc_lines = self._wrap_text(description[:200] + "...", 70)
            y_pos = 350
            for line in desc_lines[:8]:  # Limit to 8 lines
                draw.text((50, y_pos), line, fill='#555555', font=desc_font)
                y_pos += 25
            
            # Add decorative border
            draw.rectangle([20, 20, width-20, height-20], outline='#cccccc', width=3)
            
            # Save to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"Error creating poster mockup: {e}")
            return None
    
    def _create_product_mockup(self, product_name, description, concept):
        """Create a simple product mockup using PIL"""
        try:
            width, height = 800, 600
            image = Image.new('RGB', (width, height), color='#ffffff')
            draw = ImageDraw.Draw(image)
            
            try:
                title_font = ImageFont.truetype("arial.ttf", 36)
                desc_font = ImageFont.truetype("arial.ttf", 16)
            except:
                title_font = ImageFont.load_default()
                desc_font = ImageFont.load_default()
            
            # Add product placeholder
            draw.rectangle([200, 100, 600, 350], fill='#e0e0e0', outline='#999999', width=2)
            draw.text((350, 225), "PRODUCT", fill='#666666', font=title_font, anchor="mm")
            
            # Add product name
            draw.text((50, 400), product_name, fill='#333333', font=title_font)
            
            # Add description
            if description:
                desc_lines = self._wrap_text(description, 70)
                y_pos = 450
                for line in desc_lines[:3]:
                    draw.text((50, y_pos), line, fill='#666666', font=desc_font)
                    y_pos += 20
            
            # Save to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"Error creating product mockup: {e}")
            return None
    
    def _create_banner_mockup(self, business_name, message, dimensions, concept):
        """Create a simple banner mockup using PIL"""
        try:
            # Set dimensions based on type
            if dimensions == "social":
                width, height = 1200, 630
            elif dimensions == "web":
                width, height = 1200, 300
            else:
                width, height = 800, 400
            
            image = Image.new('RGB', (width, height), color='#4a90e2')
            draw = ImageDraw.Draw(image)
            
            try:
                title_font = ImageFont.truetype("arial.ttf", 48)
                msg_font = ImageFont.truetype("arial.ttf", 24)
            except:
                title_font = ImageFont.load_default()
                msg_font = ImageFont.load_default()
            
            # Add business name
            draw.text((50, height//4), business_name, fill='white', font=title_font)
            
            # Add message
            draw.text((50, height//2), message, fill='white', font=msg_font)
            
            # Add decorative elements
            draw.rectangle([width-100, 20, width-20, height-20], fill='#ffffff', width=2)
            
            # Save to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"Error creating banner mockup: {e}")
            return None
    
    def _wrap_text(self, text, width):
        """Wrap text to specified width"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
    
    def test_connection(self):
        """Test Groq API connection"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {"role": "user", "content": "Hello, are you working?"}
                ],
                "model": "llama3-8b-8192",
                "max_tokens": 50
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Groq API connection successful'
                }
            else:
                return {
                    'success': False,
                    'error': f'API connection failed: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Connection test failed: {str(e)}'
            }
