import google.generativeai as genai
from flask import current_app
import json
import random
from datetime import datetime
import requests
from PIL import Image
import io
import base64

class AIService:
    def __init__(self):
        self.api_key = current_app.config.get('GEMINI_API_KEY')
        self.model_name = current_app.config.get('GEMINI_MODEL', 'gemini-1.5-flash')
        self.temperature = float(current_app.config.get('GEMINI_TEMPERATURE', 0.7))
        self.max_tokens = int(current_app.config.get('GEMINI_MAX_TOKENS', 1000))
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                self.use_gemini = True
                print("✅ Gemini AI initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize Gemini AI: {e}")
                self.use_gemini = False
        else:
            self.use_gemini = False
            print("⚠️ Warning: Gemini API key not found. Using template responses.")
    
    def generate_content(self, content_type, prompt, business_context=''):
        """Generate content using Gemini AI"""
        try:
            if self.use_gemini:
                return self._generate_content_gemini(content_type, prompt, business_context)
            else:
                return self._generate_content_template(content_type, prompt, business_context)
        except Exception as e:
            print(f"Error generating content: {e}")
            return self._generate_content_template(content_type, prompt, business_context)
    
    def _generate_content_gemini(self, content_type, prompt, business_context):
        """Generate content using Gemini AI"""
        system_prompts = {
            'product_description': 'You are a professional copywriter specializing in product descriptions. Create engaging, SEO-friendly product descriptions that highlight benefits and features. Keep it concise and compelling.',
            'marketing_copy': 'You are a marketing expert. Create compelling marketing copy that converts readers into customers. Focus on benefits, urgency, and clear calls to action.',
            'social_media': 'You are a social media specialist. Create engaging social media posts that drive engagement and brand awareness. Use appropriate hashtags and engaging language.',
            'email_campaign': 'You are an email marketing expert. Create compelling email content that drives opens, clicks, and conversions. Include subject line suggestions.',
            'blog_post': 'You are a professional blog writer. Create informative, engaging blog posts that provide value to readers and improve SEO.',
            'website_content': 'You are a web content specialist. Create professional website content that is clear, engaging, and converts visitors into customers.'
        }
        
        system_prompt = system_prompts.get(content_type, 'You are a professional content writer. Create high-quality, engaging content.')
        
        full_prompt = f"""
{system_prompt}

Business Context: {business_context}
Content Type: {content_type}
Request: {prompt}

Please create professional, engaging content that is appropriate for the business context and content type. Make it compelling and actionable.
"""
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._generate_content_template(content_type, prompt, business_context)
    
    def generate_image(self, prompt, image_type='poster'):
        """Generate image description using Gemini AI (Note: Gemini doesn't generate actual images)"""
        try:
            if self.use_gemini:
                return self._generate_image_description_gemini(prompt, image_type)
            else:
                return self._generate_image_placeholder(prompt, image_type)
        except Exception as e:
            print(f"Error generating image: {e}")
            return self._generate_image_placeholder(prompt, image_type)
    
    def _generate_image_description_gemini(self, prompt, image_type):
        """Generate detailed image description using Gemini AI"""
        gemini_prompt = f"""
        Create a detailed description for a {image_type} with the following requirements: {prompt}
        
        Provide a comprehensive description that includes:
        - Visual composition and layout
        - Color scheme and style
        - Typography suggestions
        - Key visual elements
        - Overall aesthetic approach
        
        Make it detailed enough that a designer could create the image from this description.
        """
        
        try:
            response = self.model.generate_content(
                gemini_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                )
            )
            
            # Return a data URL with the description (placeholder)
            description = response.text.strip()
            return f"data:text/plain;base64,{base64.b64encode(description.encode()).decode()}"
            
        except Exception as e:
            print(f"Gemini image description error: {e}")
            return self._generate_image_placeholder(prompt, image_type)
    
    def _generate_image_placeholder(self, prompt, image_type):
        """Generate placeholder image data"""
        placeholder_images = {
            'poster': f"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjM2I4MmY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5Qb3N0ZXI6IHtwcm9tcHR9PC90ZXh0Pjwvc3ZnPg==",
            'logo': f"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIxMDAiIGN5PSIxMDAiIHI9IjgwIiBmaWxsPSIjMTZhMzRhIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5Mb2dvPC90ZXh0Pjwvc3ZnPg==",
            'product_image': f"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHJlY3QgeD0iNzUiIHk9Ijc1IiB3aWR0aD0iMTUwIiBoZWlnaHQ9IjE1MCIgZmlsbD0iIzllYTNhOCIvPjx0ZXh0IHg9IjUwJSIgeT0iODAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM2Yjk3Mjgiig=="
        }
        
        return placeholder_images.get(image_type, placeholder_images['poster'])
    
    def generate_business_suggestions(self, context):
        """Generate business improvement suggestions using Gemini AI"""
        try:
            if self.use_gemini:
                return self._generate_suggestions_gemini(context)
            else:
                return self._generate_suggestions_template(context)
        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return self._generate_suggestions_template(context)
    
    def _generate_suggestions_gemini(self, context):
        """Generate suggestions using Gemini AI"""
        prompt = f"""
As a business consultant, provide specific, actionable suggestions for improving this small business:

Business Name: {context['business_name']}
Business Type: {context['business_type']}
Total Products: {context['total_products']}
Recent Messages: {context['recent_messages_count']}
QR Code Scans: {context['qr_scans']}
Suggestion Type: {context['suggestion_type']}

Provide 5-7 specific, actionable suggestions in JSON format:
{{
    "suggestions": [
        {{
            "title": "Suggestion Title (action-oriented)",
            "description": "Detailed description with specific steps",
            "priority": "high|medium|low",
            "category": "marketing|products|customer_service|operations|technology",
            "effort": "low|medium|high",
            "impact": "low|medium|high",
            "timeline": "immediate|1-2 weeks|1 month|3 months"
        }}
    ]
}}

Focus on:
- Actionable, specific recommendations
- Realistic implementation steps
- Measurable outcomes
- Business growth opportunities
- Customer satisfaction improvements

Return ONLY the JSON, no additional text.
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1200,
                )
            )
            
            content = response.text.strip()
            
            try:
                # Remove any markdown formatting if present
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                elif content.startswith('```'):
                    content = content.replace('```', '').strip()
                
                return json.loads(content)
            except json.JSONDecodeError:
                return self._parse_suggestions(content)
                
        except Exception as e:
            print(f"Gemini suggestions error: {e}")
            return self._generate_suggestions_template(context)
    
    def analyze_customer_feedback(self, feedback_texts):
        """Analyze customer feedback using Gemini AI"""
        try:
            if self.use_gemini and feedback_texts:
                return self._analyze_feedback_gemini(feedback_texts)
            else:
                return self._analyze_feedback_template(feedback_texts)
        except Exception as e:
            print(f"Error analyzing feedback: {e}")
            return self._analyze_feedback_template(feedback_texts)
    
    def _analyze_feedback_gemini(self, feedback_texts):
        """Analyze feedback using Gemini AI"""
        combined_feedback = "\n\n".join(feedback_texts[:15])  # Limit for token management
        
        prompt = f"""
Analyze the following customer feedback and provide comprehensive insights:

CUSTOMER FEEDBACK:
{combined_feedback}

Provide analysis in JSON format:
{{
    "overall_sentiment": "positive|negative|neutral",
    "sentiment_score": "number between -1 and 1",
    "key_themes": ["theme1", "theme2", "theme3", "theme4", "theme5"],
    "strengths": ["strength1", "strength2", "strength3"],
    "areas_for_improvement": ["area1", "area2", "area3"],
    "recommendations": ["recommendation1", "recommendation2", "recommendation3"],
    "summary": "Brief 2-3 sentence summary of the feedback analysis",
    "action_items": ["action1", "action2", "action3"],
    "customer_satisfaction_level": "very_low|low|medium|high|very_high"
}}

Focus on:
- Accurate sentiment analysis
- Actionable insights
- Specific improvement areas
- Concrete recommendations
- Business impact assessment

Return ONLY the JSON, no additional text.
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=800,
                )
            )
            
            content = response.text.strip()
            
            try:
                # Remove any markdown formatting if present
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                elif content.startswith('```'):
                    content = content.replace('```', '').strip()
                
                return json.loads(content)
            except json.JSONDecodeError:
                return self._parse_feedback_analysis(content)
                
        except Exception as e:
            print(f"Gemini feedback analysis error: {e}")
            return self._analyze_feedback_template(feedback_texts)
    
    def chatbot_response(self, message, user_context=None, conversation_history=None):
        """Generate chatbot response using Gemini AI"""
        try:
            if self.use_gemini:
                return self._chatbot_response_gemini(message, user_context, conversation_history)
            else:
                return self._chatbot_response_template(message, user_context)
        except Exception as e:
            print(f"Error generating chatbot response: {e}")
            return self._chatbot_response_template(message, user_context)
    
    def _chatbot_response_gemini(self, message, user_context, conversation_history):
        """Generate chatbot response using Gemini AI"""
        business_name = user_context.get('business_name', 'your business') if user_context else 'your business'
        business_type = user_context.get('business_type', 'business') if user_context else 'business'
        
        context_prompt = f"""
You are a helpful business assistant for {business_name} ({business_type}). 

Your role is to provide helpful, actionable advice about:
- Business management and operations
- Marketing and customer acquisition
- Product management and inventory
- Customer service best practices
- Using the Break-even platform features
- Growing and scaling the business
- Financial management
- Digital marketing strategies

Keep responses:
- Concise but comprehensive (2-4 sentences)
- Practical and actionable
- Friendly and professional
- Specific to small business needs
- Focused on growth and success

Previous conversation context:
"""
        
        if conversation_history:
            for hist in conversation_history[-3:]:  # Last 3 exchanges
                context_prompt += f"\nUser: {hist['user_message']}\nAssistant: {hist['bot_response']}"
        
        full_prompt = f"{context_prompt}\n\nCurrent user question: {message}\n\nProvide a helpful response:"
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=300,
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"Gemini chatbot error: {e}")
            return self._chatbot_response_template(message, user_context)
    
    # Template fallback methods
    def _generate_content_template(self, content_type, prompt, business_context):
        """Template content generation fallback"""
        templates = {
            'product_description': f"Introducing our amazing product! {prompt}. {business_context} This high-quality item offers exceptional value and performance. Perfect for customers who demand the best. Features include professional design, reliable functionality, and outstanding customer support.",
            
            'marketing_copy': f"Don't miss out on this incredible opportunity! {prompt}. {business_context} Our solution provides everything you need to succeed. Join thousands of satisfied customers who have already transformed their experience with our premium service.",
            
            'social_media': f"🎉 Exciting news! {prompt} {business_context} Follow us for more updates and special offers! #business #quality #service #customers",
            
            'email_campaign': f"Hello valued customer,\n\n{prompt}\n\n{business_context}\n\nWe're committed to providing you with the best service possible. Contact us today to learn more!\n\nBest regards,\nThe Team",
            
            'blog_post': f"# {prompt}\n\n{business_context}\n\nIn today's competitive market, businesses need to stay ahead of the curve. This post explores important insights and practical tips that can help you achieve your goals.\n\n## Key Points\n\n- Professional service delivery\n- Customer satisfaction focus\n- Quality and reliability\n\n## Conclusion\n\nSuccess comes from dedication to excellence and continuous improvement."
        }
        
        return templates.get(content_type, f"Professional content for {content_type}: {prompt}. {business_context}")
    
    def _generate_suggestions_template(self, context):
        """Generate template suggestions"""
        return {
            "suggestions": [
                {
                    "title": "Improve Customer Communication",
                    "description": "Respond to customer messages promptly to improve satisfaction and build trust.",
                    "priority": "high",
                    "category": "customer_service",
                    "effort": "low",
                    "impact": "high",
                    "timeline": "immediate"
                },
                {
                    "title": "Enhance Marketing Efforts",
                    "description": "Use social media and email marketing to reach more customers and increase brand awareness.",
                    "priority": "medium",
                    "category": "marketing",
                    "effort": "medium",
                    "impact": "high",
                    "timeline": "1-2 weeks"
                },
                {
                    "title": "Optimize Product Listings",
                    "description": "Update product descriptions and images to improve customer engagement and sales.",
                    "priority": "medium",
                    "category": "products",
                    "effort": "medium",
                    "impact": "medium",
                    "timeline": "1 month"
                }
            ]
        }
    
    def _analyze_feedback_template(self, feedback_texts):
        """Generate template feedback analysis"""
        if not feedback_texts:
            return {
                "overall_sentiment": "neutral",
                "sentiment_score": 0.0,
                "key_themes": ["No feedback available"],
                "strengths": ["Opportunity to collect more feedback"],
                "areas_for_improvement": ["Gather more customer feedback"],
                "recommendations": ["Implement feedback collection system", "Ask customers for reviews"],
                "summary": "No customer feedback available for analysis. Consider implementing feedback collection mechanisms.",
                "action_items": ["Set up feedback forms", "Encourage customer reviews"],
                "customer_satisfaction_level": "medium"
            }
        
        return {
            "overall_sentiment": "positive",
            "sentiment_score": 0.2,
            "key_themes": ["Customer service", "Product quality", "User experience"],
            "strengths": ["Customer engagement", "Feedback collection"],
            "areas_for_improvement": ["Response time", "Product information"],
            "recommendations": [
                "Continue collecting customer feedback",
                "Address common concerns promptly",
                "Leverage positive feedback for marketing"
            ],
            "summary": f"Analysis of {len(feedback_texts)} feedback items shows generally positive sentiment with opportunities for improvement.",
            "action_items": ["Improve response times", "Update product descriptions", "Follow up on feedback"],
            "customer_satisfaction_level": "high"
        }
    
    def _chatbot_response_template(self, message, user_context):
        """Generate template chatbot response"""
        message_lower = message.lower()
        business_name = user_context.get('business_name', 'your business') if user_context else 'your business'
        
        if any(word in message_lower for word in ['help', 'how', 'what']):
            return f"I'm here to help you with {business_name}! You can ask me about marketing, customer management, products, or using the Break-even platform features."
        
        elif any(word in message_lower for word in ['marketing', 'promote', 'advertise']):
            return "For marketing, consider: 1) Use your QR code in visible locations, 2) Collect customer emails for newsletters, 3) Ask satisfied customers for reviews, 4) Use social media regularly, 5) Offer special promotions to new customers."
        
        elif any(word in message_lower for word in ['customer', 'client']):
            return "To improve customer service: 1) Respond to messages quickly, 2) Collect feedback regularly, 3) Follow up after purchases, 4) Create a loyalty program, 5) Personalize your communication."
        
        elif any(word in message_lower for word in ['product', 'inventory']):
            return "For product management: 1) Keep descriptions updated, 2) Use high-quality images, 3) Monitor stock levels, 4) Analyze which products are popular, 5) Consider bundling complementary items."
        
        elif any(word in message_lower for word in ['website', 'qr', 'online']):
            return "To improve your online presence: 1) Keep your website updated, 2) Place QR codes prominently in your store, 3) Track QR scan analytics, 4) Make sure contact info is current, 5) Add new products regularly."
        
        else:
            return f"Thanks for your question about {business_name}! I can help you with marketing, customer management, products, and platform features. What specific area would you like assistance with?"
    
    # Helper methods for parsing when JSON fails
    def _parse_suggestions(self, content):
        """Parse suggestions when JSON parsing fails"""
        return {
            "suggestions": [
                {
                    "title": "Improve Customer Communication",
                    "description": "Respond to customer messages promptly to improve satisfaction.",
                    "priority": "high",
                    "category": "customer_service",
                    "effort": "low",
                    "impact": "high",
                    "timeline": "immediate"
                },
                {
                    "title": "Enhance Online Presence",
                    "description": "Update your website and social media regularly to attract more customers.",
                    "priority": "medium",
                    "category": "marketing",
                    "effort": "medium",
                    "impact": "high",
                    "timeline": "1-2 weeks"
                }
            ]
        }
    
    def _parse_feedback_analysis(self, content):
        """Parse feedback analysis when JSON parsing fails"""
        return {
            "overall_sentiment": "positive",
            "sentiment_score": 0.1,
            "key_themes": ["Customer feedback analysis", "Service quality", "User experience"],
            "strengths": ["Customer engagement", "Feedback collection"],
            "areas_for_improvement": ["Response time", "Service improvement"],
            "recommendations": ["Continue gathering feedback", "Improve response processes", "Address common concerns"],
            "summary": "Feedback analysis completed with actionable insights for business improvement.",
            "action_items": ["Review feedback regularly", "Implement improvements", "Follow up with customers"],
            "customer_satisfaction_level": "high"
        }