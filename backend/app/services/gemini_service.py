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

    def generate_image_description(self, prompt, image_type="poster", style="professional"):
        """Generate detailed image description using Gemini AI for image creation"""
        try:
            system_prompt = f"""
            You are an expert graphic designer and visual artist. Create a detailed, vivid description for generating a {style} {image_type} image. 
            
            Your description should include:
            - Visual composition and layout details
            - Specific color scheme and mood
            - Typography and text placement suggestions  
            - Design elements and graphics
            - Professional quality specifications
            - Brand-appropriate aesthetic choices
            
            Make it detailed enough that an AI image generator could create a professional business image from your description.
            Keep it concise but comprehensive, focusing on visual elements.
            """
            
            full_prompt = f"{system_prompt}\n\nUser Request: {prompt}\n\nImage Type: {image_type}\nStyle: {style}"
            
            result = self.generate_content(full_prompt, max_tokens=800)
            
            if result.get('success'):
                return {
                    'success': True,
                    'description': result['content'],
                    'original_prompt': prompt,
                    'image_type': image_type,
                    'style': style
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Image description generation error: {str(e)}'
            }

    def generate_business_poster_concept(self, business_name, business_type, message="", style="professional"):
        """Generate business poster concept using Gemini AI"""
        try:
            prompt = f"Create a detailed visual description for a {style} business poster for '{business_name}', a {business_type} business"
            if message:
                prompt += f" featuring the message: '{message}'"
            
            result = self.generate_image_description(prompt, "poster", style)
            
            if result['success']:
                # Import PIL for mockup creation
                import base64
                import io
                from PIL import Image, ImageDraw, ImageFont
                
                # Create a visual mockup using the description
                poster_image = self._create_poster_mockup(
                    business_name, 
                    business_type, 
                    message, 
                    result['description']
                )
                
                return {
                    'success': True,
                    'concept': result['description'],
                    'image_data': poster_image,
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
    
    def generate_product_image_concept(self, product_name, product_description="", style="professional"):
        """Generate product image concept using Gemini AI"""
        try:
            prompt = f"Create a detailed visual description for a {style} product image of {product_name}"
            if product_description:
                prompt += f": {product_description}"
            
            result = self.generate_image_description(prompt, "product", style)
            
            if result['success']:
                import base64
                import io
                from PIL import Image, ImageDraw, ImageFont
                
                # Create product image mockup
                product_image = self._create_product_mockup(
                    product_name,
                    product_description,
                    result['description']
                )
                
                return {
                    'success': True,
                    'concept': result['description'],
                    'image_data': product_image,
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
    
    def generate_marketing_banner_concept(self, business_name, message, style="modern"):
        """Generate marketing banner concept using Gemini AI"""
        try:
            prompt = f"Create a detailed visual description for a {style} marketing banner for '{business_name}' with message: '{message}'"
            
            result = self.generate_image_description(prompt, "banner", style)
            
            if result['success']:
                import base64
                import io
                from PIL import Image, ImageDraw, ImageFont
                
                # Create banner mockup
                banner_image = self._create_banner_mockup(
                    business_name,
                    message,
                    result['description']
                )
                
                return {
                    'success': True,
                    'concept': result['description'],
                    'image_data': banner_image,
                    'business_name': business_name,
                    'message': message,
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
        """Create a poster mockup using PIL based on Gemini's description"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import base64
            import io
            
            # Create poster image
            width, height = 800, 1000
            image = Image.new('RGB', (width, height), color='#f8f9fa')
            draw = ImageDraw.Draw(image)
            
            # Try to use fonts, fallback to default
            try:
                title_font = ImageFont.truetype("arial.ttf", 48)
                subtitle_font = ImageFont.truetype("arial.ttf", 28)
                desc_font = ImageFont.truetype("arial.ttf", 18)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                desc_font = ImageFont.load_default()
            
            # Add gradient background effect
            for i in range(height):
                color_val = int(248 - (i * 30 / height))
                draw.line([(0, i), (width, i)], fill=(color_val, color_val + 5, color_val + 10))
            
            # Add business name with shadow effect
            draw.text((52, 102), business_name, fill='#cccccc', font=title_font)  # Shadow
            draw.text((50, 100), business_name, fill='#2c3e50', font=title_font)   # Main text
            
            # Add business type
            draw.text((50, 180), f"{business_type.title()} Business", fill='#34495e', font=subtitle_font)
            
            # Add message if provided
            if message:
                # Wrap message text
                wrapped_message = self._wrap_text(message, 35)
                y_pos = 250
                for line in wrapped_message[:3]:  # Max 3 lines
                    draw.text((50, y_pos), line, fill='#e74c3c', font=subtitle_font)
                    y_pos += 35
            
            # Add AI-generated concept (truncated)
            concept_text = f"AI Concept: {description[:150]}..."
            concept_lines = self._wrap_text(concept_text, 50)
            y_pos = 400
            for line in concept_lines[:8]:  # Limit lines
                draw.text((50, y_pos), line, fill='#7f8c8d', font=desc_font)
                y_pos += 25
            
            # Add decorative elements
            draw.rectangle([20, 20, width-20, height-20], outline='#3498db', width=4)
            draw.rectangle([40, 40, width-40, height-40], outline='#ecf0f1', width=2)
            
            # Add "POWERED BY GEMINI AI" watermark
            draw.text((width-250, height-30), "Powered by Gemini AI", fill='#95a5a6', font=desc_font)
            
            # Save to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"Error creating poster mockup: {e}")
            return None
    
    def _create_product_mockup(self, product_name, description, concept):
        """Create a product mockup using PIL"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import base64
            import io
            
            width, height = 800, 600
            image = Image.new('RGB', (width, height), color='#ffffff')
            draw = ImageDraw.Draw(image)
            
            try:
                title_font = ImageFont.truetype("arial.ttf", 36)
                desc_font = ImageFont.truetype("arial.ttf", 16)
                concept_font = ImageFont.truetype("arial.ttf", 14)
            except:
                title_font = ImageFont.load_default()
                desc_font = ImageFont.load_default()
                concept_font = ImageFont.load_default()
            
            # Add gradient background
            for i in range(width):
                color_val = int(255 - (i * 20 / width))
                draw.line([(i, 0), (i, height)], fill=(color_val, color_val, color_val + 5))
            
            # Add product placeholder with shadow
            shadow_rect = [202, 102, 602, 352]
            main_rect = [200, 100, 600, 350]
            draw.rectangle(shadow_rect, fill='#bdc3c7')
            draw.rectangle(main_rect, fill='#ecf0f1', outline='#34495e', width=3)
            
            # Add "PRODUCT" text in center
            draw.text((400, 225), product_name.upper()[:15], fill='#2c3e50', font=title_font, anchor="mm")
            
            # Add product name below image
            draw.text((50, 400), f"Product: {product_name}", fill='#2c3e50', font=title_font)
            
            # Add description if provided
            if description:
                desc_lines = self._wrap_text(f"Description: {description}", 60)
                y_pos = 450
                for line in desc_lines[:2]:
                    draw.text((50, y_pos), line, fill='#34495e', font=desc_font)
                    y_pos += 20
            
            # Add AI concept
            concept_lines = self._wrap_text(f"AI Concept: {concept[:100]}...", 60)
            y_pos = 500
            for line in concept_lines[:3]:
                draw.text((50, y_pos), line, fill='#7f8c8d', font=concept_font)
                y_pos += 18
            
            # Add border
            draw.rectangle([10, 10, width-10, height-10], outline='#3498db', width=2)
            
            # Save to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"Error creating product mockup: {e}")
            return None
    
    def _create_banner_mockup(self, business_name, message, concept):
        """Create a banner mockup using PIL"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import base64
            import io
            
            width, height = 1200, 400
            image = Image.new('RGB', (width, height), color='#3498db')
            draw = ImageDraw.Draw(image)
            
            try:
                title_font = ImageFont.truetype("arial.ttf", 54)
                msg_font = ImageFont.truetype("arial.ttf", 28)
                concept_font = ImageFont.truetype("arial.ttf", 16)
            except:
                title_font = ImageFont.load_default()
                msg_font = ImageFont.load_default()
                concept_font = ImageFont.load_default()
            
            # Add gradient background
            for i in range(height):
                blue_val = int(52 + (i * 30 / height))
                draw.line([(0, i), (width, i)], fill=(blue_val, blue_val + 100, 219))
            
            # Add business name with shadow
            draw.text((52, 52), business_name, fill='#2c3e50', font=title_font)
            draw.text((50, 50), business_name, fill='white', font=title_font)
            
            # Add message
            msg_lines = self._wrap_text(message, 60)
            y_pos = 140
            for line in msg_lines[:2]:
                draw.text((50, y_pos), line, fill='white', font=msg_font)
                y_pos += 35
            
            # Add concept preview
            concept_preview = f"AI Design Concept: {concept[:80]}..."
            draw.text((50, height-60), concept_preview, fill='#ecf0f1', font=concept_font)
            
            # Add decorative elements
            draw.rectangle([width-150, 30, width-30, height-30], fill='rgba(255,255,255,0.1)', outline='white', width=2)
            draw.text((width-140, height//2), "GEMINI\nAI", fill='white', font=msg_font, anchor="mm")
            
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

# Initialize service - will be created when needed
gemini_service = None

def get_gemini_service():
    """Get or create Gemini service instance"""
    global gemini_service
    if gemini_service is None:
        gemini_service = GeminiAIService()
    return gemini_service
