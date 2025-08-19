"""
Gemini AI Service for Break-even App
Provides AI-powered content generation, business insights, and text analysis
"""

import requests
from flask import current_app
import json
import google.generativeai as genai
import re
from datetime import datetime
from app import mongo
from bson import ObjectId

    
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
        """Generate website content sections with enhanced prompt engineering"""
        
        # Enhanced prompt with better structure and examples
        prompt = f"""
You are an expert web copywriter and conversion specialist with 10+ years of experience creating high-converting small business websites. Your task is to create compelling, professional website content that drives customer action.

BUSINESS PROFILE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏢 Business Name: {business_info.get('name', 'Business')}
🏷️ Industry: {business_info.get('business_type', 'business')}
📍 Location: {business_info.get('area', 'Local Area')}
📞 Contact: {business_info.get('contact_info', {}).get('phone', 'Contact Available')}
🛠️ Services: {business_info.get('services', 'Professional Services')}
📋 Description: {business_info.get('description', 'Quality service provider')}

CONTENT REQUIREMENTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Use proven copywriting formulas (AIDA, PAS, Before-After-Bridge)
✅ Include emotional triggers and benefit-focused language
✅ Create urgency and scarcity where appropriate
✅ Use local SEO keywords naturally
✅ Include clear calls-to-action throughout
✅ Address customer pain points and objections
✅ Build trust through social proof elements
✅ Make content scannable with bullet points and headers

INDUSTRY-SPECIFIC FOCUS:
{self._get_enhanced_industry_guidance(business_info.get('business_type', 'general'))}

TARGET AUDIENCE PSYCHOLOGY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Primary emotion: {self._get_target_emotion(business_info.get('business_type', 'general'))}
🔍 Main concern: {self._get_customer_concern(business_info.get('business_type', 'general'))}
💰 Decision factor: {self._get_decision_factor(business_info.get('business_type', 'general'))}

Generate content in the following JSON structure with compelling, conversion-focused copy:

{{
    "hero_title": "Powerful headline using proven formula (Problem + Solution + Benefit)",
    "hero_subtitle": "Supporting text that amplifies the headline and creates desire",
    "about_us": "Trust-building about section that addresses credibility and expertise",
    "services_intro": "Benefit-driven services introduction that focuses on customer outcomes",
    "contact_cta": "Urgency-driven call-to-action that compels immediate action",
    "value_proposition": "Clear unique value proposition that differentiates from competitors",
    "trust_elements": [
        "Social proof element 1",
        "Credibility indicator 2", 
        "Risk reversal element 3"
    ],
    "pain_points_addressed": [
        "Customer pain point 1 with solution",
        "Customer pain point 2 with solution",
        "Customer pain point 3 with solution"
    ],
    "local_optimization": {{
        "local_keywords": ["keyword1 {business_info.get('area', 'area')}", "keyword2"],
        "community_connection": "Local community involvement statement",
        "area_specific_benefits": "Why choosing local matters"
    }},
    "conversion_elements": {{
        "urgency_phrases": ["Limited time offer", "Book now"],
        "trust_signals": ["Licensed", "Insured", "Experienced"],
        "risk_reversal": "Guarantee or risk-free trial offer"
    }}
}}

SUCCESSFUL HEADLINE EXAMPLES FOR REFERENCE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• "Finally, [Benefit] Without [Pain Point] in [Location]"
• "The Only [Service Type] in [Area] That Guarantees [Specific Result]"
• "[Number] Reasons Why [Target Audience] Choose Us Over Competitors"
• "Transform Your [Problem Area] in [Timeframe] - Guaranteed"

Make every word count. Focus on benefits over features. Create emotional connection while maintaining professionalism.
"""
        
        result = self.generate_content(prompt, max_tokens=1200)
        
        if result['success']:
            try:
                # Enhanced JSON parsing with better error handling
                content = result['content']
                
                # Multiple JSON extraction methods
                json_content = self._extract_json_content(content)
                
                if json_content:
                    # Validate and enhance the extracted content
                    validated_content = self._validate_and_enhance_content(json_content, business_info)
                    result['parsed_content'] = validated_content
                else:
                    # Fallback with enhanced content extraction
                    result['parsed_content'] = self._create_enhanced_fallback_content(business_info)
                    
            except Exception as e:
                print(f"JSON parsing error: {e}")
                result['parsed_content'] = self._create_enhanced_fallback_content(business_info)
        
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

    def chatbot_response(self, user_message, business_context=None, conversation_history=None):
        """Generate chatbot response with enhanced business context and prompt engineering"""
        
        # Build context from conversation history
        conversation_context = ""
        if conversation_history:
            recent_history = conversation_history[-5:]  # Last 5 exchanges
            for exchange in recent_history:
                conversation_context += f"User: {exchange.get('user_message', '')}\n"
                conversation_context += f"Assistant: {exchange.get('bot_response', '')}\n"
        
        # Build business context
        business_info = ""
        if business_context:
            business_info = f"""
BUSINESS CONTEXT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏢 Business: {business_context.get('business_name', 'Business')}
🏷️ Type: {business_context.get('business_type', 'General Business')}
📍 Location: {business_context.get('area', 'Local Area')}
📋 Services: {business_context.get('services', 'Professional Services')}
"""
        
        # Enhanced chatbot prompt with business expertise
        prompt = f"""
You are a highly knowledgeable AI business assistant specializing in small business management, marketing, and growth strategies. You provide actionable, practical advice tailored to small business owners.

{business_info}

CONVERSATION HISTORY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{conversation_context}

YOUR ROLE & EXPERTISE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Business Strategy Consultant
📈 Marketing & Sales Expert  
💼 Operations Advisor
💰 Financial Planning Guide
🚀 Growth & Scaling Specialist
🛠️ Technology Integration Helper
👥 Customer Service Expert

RESPONSE GUIDELINES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Provide specific, actionable advice
✅ Use business best practices and proven strategies
✅ Include relevant examples and case studies when helpful
✅ Offer step-by-step guidance for complex topics
✅ Reference industry trends and insights
✅ Suggest tools, resources, or next steps
✅ Be encouraging and supportive
✅ Keep responses concise but comprehensive
✅ Use emojis sparingly for clarity, not decoration

CURRENT USER MESSAGE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"{user_message}"

Provide a helpful, expert response that addresses their question while considering their business context. If the question is unclear, ask clarifying questions. If you need more information about their specific situation, request it.

Focus on:
• Practical solutions they can implement immediately
• Strategic insights for long-term success  
• Cost-effective approaches for small businesses
• Local business considerations when relevant
• Industry-specific advice when applicable

Remember: You're their trusted business advisor. Be professional, knowledgeable, and genuinely helpful.
"""
        
        result = self.generate_content(prompt, max_tokens=800)
        
        if result['success']:
            # Clean up the response
            response = result['content'].strip()
            
            # Remove any unwanted formatting
            response = re.sub(r'^(Assistant:|Bot:|AI:)\s*', '', response, flags=re.MULTILINE)
            
            return {
                'success': True,
                'response': response,
                'message_type': 'business_advice',
                'context_used': bool(business_context),
                'conversation_length': len(conversation_history) if conversation_history else 0
            }
        else:
            return {
                'success': False,
                'response': "I apologize, but I'm having trouble processing your request right now. Please try again or rephrase your question.",
                'error': result.get('error', 'Unknown error')
            }

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

    def _get_enhanced_industry_guidance(self, business_type):
        """Get enhanced industry-specific guidance for better prompts"""
        enhanced_guidance = {
            'food_store': """
🍽️ FOOD INDUSTRY FOCUS:
• Emphasize FRESHNESS, TASTE, and QUALITY ingredients
• Use sensory language: "mouth-watering", "fresh-baked", "locally-sourced"
• Highlight health/dietary options: "organic", "gluten-free", "farm-to-table"
• Create urgency: "daily specials", "limited quantities", "while supplies last"
• Focus on experience: atmosphere, family-friendly, date night destination
• Include social proof: "neighborhood favorite", "5-star reviews", "family recipes"
""",
            'fashion': """
👗 FASHION INDUSTRY FOCUS:
• Emphasize STYLE, TRENDS, and PERSONAL EXPRESSION
• Use aspirational language: "transform your look", "express your unique style"
• Highlight variety: "latest trends", "timeless classics", "size-inclusive"
• Create desire: "limited edition", "exclusive collection", "must-have pieces"
• Focus on fit and quality: "perfect fit guaranteed", "premium fabrics"
• Include style authority: "fashion experts", "personal styling", "trend setters"
""",
            'professional': """
💼 PROFESSIONAL SERVICES FOCUS:
• Emphasize EXPERTISE, RESULTS, and TRUST
• Use authority language: "certified experts", "proven track record", "industry leaders"
• Highlight problem-solving: "we solve complex challenges", "streamlined solutions"
• Create confidence: "guaranteed results", "risk-free consultation", "success stories"
• Focus on ROI: "save time and money", "increase efficiency", "measurable results"
• Include credentials: "licensed professionals", "award-winning team", "industry recognition"
""",
            'beauty': """
💄 BEAUTY INDUSTRY FOCUS:
• Emphasize TRANSFORMATION, SELF-CARE, and CONFIDENCE
• Use empowering language: "reveal your natural beauty", "pamper yourself", "feel confident"
• Highlight expertise: "master stylists", "latest techniques", "premium products"
• Create relaxation appeal: "escape and unwind", "luxury experience", "you deserve this"
• Focus on results: "dramatic transformation", "long-lasting results", "natural-looking"
• Include safety: "sanitized tools", "hygienic environment", "skin-safe products"
""",
            'technology': """
💻 TECHNOLOGY FOCUS:
• Emphasize INNOVATION, EFFICIENCY, and FUTURE-PROOFING
• Use technical authority: "cutting-edge solutions", "industry expertise", "advanced systems"
• Highlight problem-solving: "streamline operations", "eliminate bottlenecks", "scale your business"
• Create urgency: "stay competitive", "don't get left behind", "upgrade now"
• Focus on ROI: "increase productivity", "reduce costs", "measurable improvements"
• Include support: "24/7 support", "ongoing maintenance", "training included"
""",
            'general': """
🎯 GENERAL BUSINESS FOCUS:
• Emphasize TRUST, QUALITY, and CUSTOMER SERVICE
• Use community language: "local experts", "neighborhood business", "community-focused"
• Highlight reliability: "dependable service", "on-time delivery", "consistent quality"
• Create personal connection: "family-owned", "personal attention", "we care about you"
• Focus on value: "fair pricing", "excellent value", "no hidden fees"
• Include guarantees: "satisfaction guaranteed", "warranty included", "risk-free trial"
"""
        }
        return enhanced_guidance.get(business_type, enhanced_guidance['general'])

    def _get_target_emotion(self, business_type):
        """Get primary emotional trigger for business type"""
        emotions = {
            'food_store': 'Hunger, comfort, and social connection',
            'fashion': 'Confidence, self-expression, and attractiveness', 
            'professional': 'Security, trust, and success',
            'beauty': 'Confidence, relaxation, and self-worth',
            'technology': 'Efficiency, innovation, and competitive advantage',
            'general': 'Trust, reliability, and peace of mind'
        }
        return emotions.get(business_type, emotions['general'])

    def _get_customer_concern(self, business_type):
        """Get main customer concern for business type"""
        concerns = {
            'food_store': 'Food quality, freshness, and value for money',
            'fashion': 'Finding the right style, fit, and staying trendy',
            'professional': 'Getting reliable results and good value',
            'beauty': 'Safety, results, and professional expertise',
            'technology': 'System reliability, security, and technical support',
            'general': 'Quality service, fair pricing, and trustworthiness'
        }
        return concerns.get(business_type, concerns['general'])

    def _get_decision_factor(self, business_type):
        """Get primary decision factor for business type"""
        factors = {
            'food_store': 'Taste, freshness, and atmosphere',
            'fashion': 'Style variety, quality, and personal service',
            'professional': 'Expertise, track record, and guarantees',
            'beauty': 'Skill level, hygiene standards, and results',
            'technology': 'Reliability, support quality, and innovation',
            'general': 'Trust, quality, and customer service'
        }
        return factors.get(business_type, factors['general'])

    def _extract_json_content(self, content):
        """Enhanced JSON extraction with multiple methods"""
        try:
            # Method 1: Find JSON block with proper brackets
            import re
            json_pattern = r'\{[\s\S]*\}'
            matches = re.findall(json_pattern, content)
            
            for match in matches:
                try:
                    return json.loads(match)
                except:
                    continue
            
            # Method 2: Extract between code blocks
            code_block_pattern = r'```json\s*(.*?)\s*```'
            code_matches = re.findall(code_block_pattern, content, re.DOTALL)
            
            for match in code_matches:
                try:
                    return json.loads(match)
                except:
                    continue
                    
            # Method 3: Find JSON-like structure line by line
            lines = content.split('\n')
            json_lines = []
            in_json = False
            brace_count = 0
            
            for line in lines:
                if '{' in line and not in_json:
                    in_json = True
                    json_lines.append(line)
                    brace_count += line.count('{') - line.count('}')
                elif in_json:
                    json_lines.append(line)
                    brace_count += line.count('{') - line.count('}')
                    if brace_count <= 0:
                        break
            
            if json_lines:
                try:
                    json_str = '\n'.join(json_lines)
                    return json.loads(json_str)
                except:
                    pass
                    
            return None
            
        except Exception as e:
            print(f"JSON extraction error: {e}")
            return None

    def _validate_and_enhance_content(self, content, business_info):
        """Validate and enhance extracted content"""
        try:
            # Ensure all required fields exist
            required_fields = {
                'hero_title': f"Welcome to {business_info.get('name', 'Our Business')}",
                'hero_subtitle': f"Your trusted {business_info.get('business_type', 'service provider')} in {business_info.get('area', 'the area')}",
                'about_us': "We are committed to providing exceptional service to our valued customers.",
                'services_intro': "Discover our comprehensive range of professional services designed to meet your needs.",
                'contact_cta': "Contact us today for a free consultation!"
            }
            
            for field, default in required_fields.items():
                if field not in content or not content[field]:
                    content[field] = default
            
            # Add local optimization if missing
            if 'local_optimization' not in content:
                content['local_optimization'] = {
                    'local_keywords': [f"{business_info.get('business_type', 'business')} {business_info.get('area', '')}"],
                    'community_connection': f"Proudly serving the {business_info.get('area', 'local')} community",
                    'area_specific_benefits': "Local expertise you can trust"
                }
            
            # Add conversion elements if missing
            if 'conversion_elements' not in content:
                content['conversion_elements'] = {
                    'urgency_phrases': ["Contact us today", "Limited availability"],
                    'trust_signals': ["Licensed", "Insured", "Experienced"],
                    'risk_reversal': "Satisfaction guaranteed or your money back"
                }
            
            return content
            
        except Exception as e:
            print(f"Content validation error: {e}")
            return self._create_enhanced_fallback_content(business_info)

    def _create_enhanced_fallback_content(self, business_info):
        """Create enhanced fallback content when AI parsing fails"""
        business_name = business_info.get('name', 'Our Business')
        business_type = business_info.get('business_type', 'business')
        area = business_info.get('area', 'the local area')
        
        return {
            "hero_title": f"Transform Your Experience with {business_name}",
            "hero_subtitle": f"The premier {business_type} in {area} delivering exceptional results you can trust",
            "about_us": f"At {business_name}, we combine years of expertise with personalized service to exceed your expectations. Our commitment to quality and customer satisfaction has made us the preferred choice in {area}.",
            "services_intro": f"Discover why customers choose {business_name} for their {business_type} needs. Our comprehensive services are designed to deliver results that matter.",
            "contact_cta": "Ready to experience the difference? Contact us today for your free consultation!",
            "value_proposition": f"The only {business_type} in {area} that guarantees your complete satisfaction",
            "trust_elements": [
                "Fully licensed and insured professionals",
                "100% satisfaction guarantee", 
                "Serving the community for years"
            ],
            "pain_points_addressed": [
                "No more worrying about quality - we guarantee exceptional results",
                "Skip the hassle of multiple vendors - we handle everything for you",
                "Stop overpaying for subpar service - get premium quality at fair prices"
            ],
            "local_optimization": {
                "local_keywords": [f"{business_type} {area}", f"local {business_type}", f"{area} {business_type} service"],
                "community_connection": f"Proudly serving {area} and surrounding communities",
                "area_specific_benefits": "Local expertise with deep community roots"
            },
            "conversion_elements": {
                "urgency_phrases": ["Contact us today", "Limited spots available", "Book now"],
                "trust_signals": ["Licensed", "Insured", "Guaranteed", "Local experts"],
                "risk_reversal": "100% satisfaction guarantee - if you're not completely happy, we'll make it right"
            }
        }

    def generate_enhanced_website_content(self, business_data, user_context=None):
        """Generate website content using advanced prompt engineering with Gemini"""
        
        # Collect training data from similar businesses
        training_context = self._get_training_context(business_data['business_type'], business_data['area'])
        
        # Build comprehensive prompt with context
        prompt = self._build_enhanced_prompt(business_data, training_context, user_context)
        
        try:
            if self.model:
                response = self.model.generate_content(prompt)
                content = self._parse_gemini_response(response.text)
                
                # Store successful generation for training
                self._store_training_data(business_data, content, 'gemini')
                
                return content
            else:
                return self._fallback_generation(business_data)
                
        except Exception as e:
            print(f"Gemini generation failed: {e}")
            return self._fallback_generation(business_data)
    
    def _build_enhanced_prompt(self, business_data, training_context, user_context):
        """Build sophisticated prompt with context and examples"""
        
        prompt = f"""
You are an expert web designer and copywriter specializing in small business websites. Create compelling, conversion-focused website content.

BUSINESS CONTEXT:
- Business Name: {business_data['website_name']}
- Industry: {business_data['business_type']}
- Location: {business_data['area']}
- Description: {business_data.get('description', 'Not provided')}
- Target Theme: {business_data['color_theme']}
- Contact Info: {json.dumps(business_data['contact_info'], indent=2)}

SUCCESSFUL EXAMPLES FROM SIMILAR BUSINESSES:
{training_context}

USER BEHAVIORAL CONTEXT:
{user_context if user_context else 'New business owner, first website'}

ADVANCED REQUIREMENTS:
1. Create content that converts visitors to customers
2. Use psychology-driven copywriting (urgency, social proof, benefits over features)
3. Include local SEO optimization for {business_data['area']}
4. Make content mobile-first and scannable
5. Include clear call-to-actions throughout
6. Use industry-specific terminology appropriately
7. Create emotional connection with target audience

SPECIFIC INDUSTRY CONSIDERATIONS:
{self._get_industry_specific_guidance(business_data['business_type'])}

LOCAL MARKET INSIGHTS:
{self._get_local_market_insights(business_data['area'])}

CONTENT STRUCTURE REQUIREMENTS:
Generate a comprehensive JSON response with the following structure:

{{
    "hero_section": {{
        "headline": "Compelling headline that addresses customer pain point",
        "subheadline": "Supporting text that builds on the headline",
        "cta_primary": "Primary call-to-action text",
        "cta_secondary": "Secondary call-to-action text",
        "value_proposition": "Unique value proposition in one sentence"
    }},
    "about_section": {{
        "title": "About section title",
        "story": "Compelling brand story that builds trust",
        "mission": "Clear mission statement",
        "values": ["value1", "value2", "value3"],
        "credentials": "Any relevant certifications or experience"
    }},
    "services_products": {{
        "section_title": "Services/Products section title",
        "items": [
            {{
                "name": "Service/Product name",
                "description": "Benefit-focused description",
                "features": ["feature1", "feature2", "feature3"],
                "pricing_hint": "Pricing information or 'Contact for quote'"
            }}
        ]
    }},
    "social_proof": {{
        "testimonials_title": "Testimonials section title",
        "sample_testimonials": [
            {{
                "text": "Realistic testimonial text",
                "author": "Customer Name",
                "business": "Customer Business (if B2B)"
            }}
        ],
        "stats": [
            {{
                "number": "100+",
                "description": "Happy Customers"
            }}
        ]
    }},
    "contact_section": {{
        "title": "Contact section title",
        "description": "Why customers should contact you",
        "form_fields": ["name", "email", "phone", "message"],
        "contact_reasons": ["reason1", "reason2", "reason3"]
    }},
    "seo_meta": {{
        "title": "SEO-optimized page title (max 60 characters)",
        "description": "Meta description (max 160 characters)",
        "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
        "local_keywords": ["local keyword1", "local keyword2"]
    }},
    "content_strategy": {{
        "blog_topics": ["topic1", "topic2", "topic3"],
        "faq_items": [
            {{
                "question": "Common customer question",
                "answer": "Helpful answer"
            }}
        ],
        "conversion_elements": ["urgency", "scarcity", "social_proof", "risk_reversal"]
    }}
}}

TONE AND STYLE:
- Professional yet approachable
- Industry-appropriate language
- Local community connection
- Customer-benefit focused
- Action-oriented

Generate content that would make this business stand out in {business_data['area']} and convert visitors into customers.
"""
        
        return prompt
    
    def _get_training_context(self, business_type, area, limit=3):
        """Get successful examples from similar businesses"""
        try:
            # Find similar businesses that had successful websites
            similar_businesses = list(mongo.db.website_training_data.find({
                'business_type': business_type,
                'performance_score': {'$gte': 4.0},  # High-performing websites
                'area': {'$regex': area.split(',')[0], '$options': 'i'}  # Same city/region
            }).sort('performance_score', -1).limit(limit))
            
            if not similar_businesses:
                # Fallback to same business type regardless of location
                similar_businesses = list(mongo.db.website_training_data.find({
                    'business_type': business_type,
                    'performance_score': {'$gte': 3.5}
                }).sort('performance_score', -1).limit(limit))
            
            context = "Examples of successful similar businesses:\n"
            for business in similar_businesses:
                context += f"""
- {business['business_name']} ({business['area']})
  Success metrics: {business['performance_score']}/5.0
  Key elements: {', '.join(business['success_factors'])}
  Popular content: {business['top_content']}
"""
            
            return context if similar_businesses else "No similar business examples available."
            
        except Exception as e:
            print(f"Error getting training context: {e}")
            return "Training context unavailable."
    
    def _get_industry_specific_guidance(self, business_type):
        """Get industry-specific content guidance"""
        guidance = {
            'food_store': """
- Emphasize freshness, quality ingredients, and taste
- Include menu highlights and dietary options
- Focus on experience (atmosphere, service)
- Use sensory language (delicious, fresh, homemade)
- Include opening hours prominently
- Mention delivery/takeout options
- Local sourcing and community connection
""",
            'fashion': """
- Focus on style, trends, and personal expression
- Emphasize quality, fit, and fabric
- Include size inclusivity messaging
- Showcase variety and latest collections
- Personal styling services
- Return/exchange policies
- Social media integration for outfit inspiration
""",
            'professional': """
- Establish credibility and expertise
- Include certifications and experience
- Focus on problem-solving and results
- Use industry terminology appropriately
- Include case studies or success stories
- Clear process explanation
- Professional credentials and team
""",
            'beauty': """
- Focus on transformation and self-care
- Emphasize relaxation and pampering
- Include before/after concepts
- Mention hygiene and safety standards
- Specialized treatments and products
- Booking convenience
- Staff expertise and training
""",
            'technology': """
- Emphasize innovation and cutting-edge solutions
- Focus on efficiency and problem-solving
- Include technical expertise
- Security and reliability
- Scalability and future-proofing
- Support and maintenance
- Industry compliance
""",
            'general': """
- Focus on customer service excellence
- Emphasize reliability and trust
- Local community involvement
- Quality and value proposition
- Personalized service
- Long-term relationships
- Problem-solving approach
"""
        }
        
        return guidance.get(business_type, guidance['general'])
    
    def _get_local_market_insights(self, area):
        """Generate local market insights"""
        # This could be enhanced with real market data APIs
        city = area.split(',')[0].strip()
        
        insights = f"""
Local Market Context for {area}:
- Emphasize local community connection
- Use local landmarks or references where appropriate
- Consider local competition and differentiation
- Include local service area coverage
- Mention local partnerships or community involvement
- Use location-specific keywords for SEO
- Consider local demographics and preferences
"""
        return insights
    
    def _parse_gemini_response(self, response_text):
        """Parse and validate Gemini response"""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # If no JSON found, create structured content from text
                return self._extract_content_from_text(response_text)
                
        except json.JSONDecodeError:
            # Fallback parsing
            return self._extract_content_from_text(response_text)
    
    def _extract_content_from_text(self, text):
        """Extract structured content from unstructured text response"""
        # Basic content extraction logic
        return {
            "hero_section": {
                "headline": "Welcome to Your Local Business",
                "subheadline": "Quality service you can trust",
                "cta_primary": "Get Started Today",
                "cta_secondary": "Learn More",
                "value_proposition": "Your trusted local partner for exceptional service"
            },
            "about_section": {
                "title": "About Us",
                "story": text[:200] + "..." if len(text) > 200 else text,
                "mission": "To provide exceptional service to our local community",
                "values": ["Quality", "Trust", "Service"],
                "credentials": "Years of experience serving the community"
            },
            "services_products": {
                "section_title": "Our Services",
                "items": [
                    {
                        "name": "Premium Service",
                        "description": "High-quality service tailored to your needs",
                        "features": ["Professional", "Reliable", "Affordable"],
                        "pricing_hint": "Contact for quote"
                    }
                ]
            },
            "seo_meta": {
                "title": "Local Business - Quality Service",
                "description": "Professional service provider in your area",
                "keywords": ["local business", "quality service", "professional"],
                "local_keywords": ["local service", "area business"]
            }
        }
    
    def _store_training_data(self, business_data, generated_content, model_used):
        """Store successful generations for future training"""
        try:
            training_entry = {
                'business_type': business_data['business_type'],
                'area': business_data['area'],
                'business_name': business_data['website_name'],
                'input_data': business_data,
                'generated_content': generated_content,
                'model_used': model_used,
                'created_at': datetime.utcnow(),
                'performance_score': 0.0,  # Will be updated based on user feedback
                'user_modifications': [],
                'success_factors': [],
                'engagement_metrics': {}
            }
            
            mongo.db.website_training_data.insert_one(training_entry)
            
        except Exception as e:
            print(f"Error storing training data: {e}")
    
    def _fallback_generation(self, business_data):
        """Fallback content generation when AI is unavailable"""
        return {
            "hero_section": {
                "headline": f"Welcome to {business_data['website_name']}",
                "subheadline": f"Your trusted {business_data['business_type']} in {business_data['area']}",
                "cta_primary": "Contact Us Today",
                "cta_secondary": "Learn More",
                "value_proposition": "Quality service you can count on"
            },
            "about_section": {
                "title": "About Our Business",
                "story": business_data.get('description', 'We are committed to providing excellent service to our community.'),
                "mission": "To serve our community with excellence and integrity",
                "values": ["Quality", "Trust", "Service"],
                "credentials": "Experienced professionals dedicated to your satisfaction"
            },
            "services_products": {
                "section_title": "What We Offer",
                "items": [
                    {
                        "name": "Professional Service",
                        "description": "High-quality service tailored to your specific needs",
                        "features": ["Professional", "Reliable", "Affordable"],
                        "pricing_hint": "Contact us for pricing"
                    }
                ]
            },
            "seo_meta": {
                "title": f"{business_data['website_name']} - {business_data['business_type']} in {business_data['area']}",
                "description": f"Professional {business_data['business_type']} services in {business_data['area']}. Contact us today!",
                "keywords": [business_data['business_type'], business_data['area'], "professional", "service"],
                "local_keywords": [f"{business_data['business_type']} {business_data['area']}", f"local {business_data['business_type']}"]
            }
        }

class WebsiteTrainingService:
    """Service for collecting and processing training data"""
    
    def __init__(self):
        pass
    
    def collect_user_feedback(self, website_id, feedback_data):
        """Collect user feedback on generated websites"""
        try:
            feedback_entry = {
                'website_id': ObjectId(website_id),
                'feedback_type': feedback_data.get('type', 'general'),
                'rating': feedback_data.get('rating', 0),
                'comments': feedback_data.get('comments', ''),
                'modifications_made': feedback_data.get('modifications', []),
                'user_satisfaction': feedback_data.get('satisfaction', 0),
                'would_recommend': feedback_data.get('recommend', False),
                'created_at': datetime.utcnow()
            }
            
            mongo.db.website_feedback.insert_one(feedback_entry)
            
            # Update training data performance score
            self._update_performance_score(website_id, feedback_data)
            
        except Exception as e:
            print(f"Error collecting feedback: {e}")
    
    def _update_performance_score(self, website_id, feedback_data):
        """Update performance score based on feedback"""
        try:
            # Calculate score based on multiple factors
            score = 0.0
            score += feedback_data.get('rating', 0) * 0.4  # User rating (40%)
            score += feedback_data.get('satisfaction', 0) * 0.3  # Satisfaction (30%)
            score += (1 if feedback_data.get('recommend', False) else 0) * 1.0  # Recommendation (20%)
            score += max(0, (10 - len(feedback_data.get('modifications', []))) / 10) * 1.0  # Few modifications (10%)
            
            # Update training data
            mongo.db.website_training_data.update_one(
                {'website_id': ObjectId(website_id)},
                {
                    '$set': {
                        'performance_score': score,
                        'last_updated': datetime.utcnow()
                    },
                    '$push': {
                        'feedback_history': feedback_data
                    }
                }
            )
            
        except Exception as e:
            print(f"Error updating performance score: {e}")
    
    def analyze_successful_patterns(self, business_type=None):
        """Analyze patterns from successful websites"""
        try:
            match_query = {'performance_score': {'$gte': 4.0}}
            if business_type:
                match_query['business_type'] = business_type
            
            pipeline = [
                {'$match': match_query},
                {'$group': {
                    '_id': '$business_type',
                    'avg_score': {'$avg': '$performance_score'},
                    'common_elements': {'$push': '$success_factors'},
                    'top_content': {'$push': '$generated_content.hero_section.headline'},
                    'count': {'$sum': 1}
                }},
                {'$sort': {'avg_score': -1}}
            ]
            
            results = list(mongo.db.website_training_data.aggregate(pipeline))
            return results
            
        except Exception as e:
            print(f"Error analyzing patterns: {e}")
            return []
    
    def get_content_recommendations(self, business_type, area):
        """Get content recommendations based on successful patterns"""
        try:
            successful_websites = list(mongo.db.website_training_data.find({
                'business_type': business_type,
                'performance_score': {'$gte': 4.0}
            }).sort('performance_score', -1).limit(5))
            
            recommendations = {
                'headline_patterns': [],
                'successful_ctas': [],
                'popular_services': [],
                'effective_descriptions': []
            }
            
            for website in successful_websites:
                content = website.get('generated_content', {})
                
                if 'hero_section' in content:
                    recommendations['headline_patterns'].append(content['hero_section'].get('headline'))
                    recommendations['successful_ctas'].append(content['hero_section'].get('cta_primary'))
                
                if 'services_products' in content:
                    for service in content['services_products'].get('items', []):
                        recommendations['popular_services'].append(service.get('name'))
            
            return recommendations
            
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return {}

# Initialize service - will be created when needed
gemini_service = None

def get_gemini_service():
    """Get or create Gemini service instance"""
    global gemini_service
    if gemini_service is None:
        gemini_service = GeminiAIService()
    return gemini_service

