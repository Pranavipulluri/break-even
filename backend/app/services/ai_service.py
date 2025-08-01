
import openai
from flask import current_app
import json
import random
from datetime import datetime

class AIService:
    def __init__(self):
        openai.api_key = current_app.config.get('OPENAI_API_KEY')
        self.use_openai = bool(openai.api_key)
    
    def generate_content(self, content_type, prompt, business_context=''):
        """Generate content using AI"""
        try:
            if self.use_openai:
                return self._generate_content_openai(content_type, prompt, business_context)
            else:
                return self._generate_content_template(content_type, prompt, business_context)
        except Exception as e:
            print(f"Error generating content: {e}")
            return self._generate_content_template(content_type, prompt, business_context)
    
    def _generate_content_openai(self, content_type, prompt, business_context):
        """Generate content using OpenAI"""
        system_prompts = {
            'product_description': 'You are a professional copywriter specializing in product descriptions. Create engaging, SEO-friendly product descriptions that highlight benefits and features.',
            'marketing_copy': 'You are a marketing expert. Create compelling marketing copy that converts readers into customers.',
            'social_media': 'You are a social media specialist. Create engaging social media posts that drive engagement and brand awareness.',
            'email_campaign': 'You are an email marketing expert. Create compelling email content that drives opens, clicks, and conversions.',
            'blog_post': 'You are a professional blog writer. Create informative, engaging blog posts that provide value to readers.'
        }
        
        system_prompt = system_prompts.get(content_type, 'You are a professional content writer. Create high-quality, engaging content.')
        
        user_prompt = f"""
        Business context: {business_context}
        
        Content type: {content_type}
        
        Request: {prompt}
        
        Please create professional, engaging content that is appropriate for the business context and content type.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._generate_content_template(content_type, prompt, business_context)
    
    def _generate_content_template(self, content_type, prompt, business_context):
        """Generate template content without AI"""
        templates = {
            'product_description': f"Introducing our amazing product! {prompt}. {business_context} This high-quality item offers exceptional value and performance. Perfect for customers who demand the best. Features include professional design, reliable functionality, and outstanding customer support.",
            
            'marketing_copy': f"Don't miss out on this incredible opportunity! {prompt}. {business_context} Our solution provides everything you need to succeed. Join thousands of satisfied customers who have already transformed their experience with our premium service.",
            
            'social_media': f"🎉 Exciting news! {prompt} {business_context} Follow us for more updates and special offers! #business #quality #service #customers",
            
            'email_campaign': f"Hello valued customer,\n\n{prompt}\n\n{business_context}\n\nWe're committed to providing you with the best service possible. Contact us today to learn more!\n\nBest regards,\nThe Team",
            
            'blog_post': f"# {prompt}\n\n{business_context}\n\nIn today's competitive market, businesses need to stay ahead of the curve. This post explores important insights and practical tips that can help you achieve your goals.\n\n## Key Points\n\n- Professional service delivery\n- Customer satisfaction focus\n- Quality and reliability\n\n## Conclusion\n\nSuccess comes from dedication to excellence and continuous improvement."
        }
        
        return templates.get(content_type, f"Professional content for {content_type}: {prompt}. {business_context}")
    
    def generate_image(self, prompt, image_type='poster'):
        """Generate image using AI (placeholder for DALL-E integration)"""
        try:
            if self.use_openai:
                return self._generate_image_openai(prompt, image_type)
            else:
                return self._generate_image_placeholder(prompt, image_type)
        except Exception as e:
            print(f"Error generating image: {e}")
            return self._generate_image_placeholder(prompt, image_type)
    
    def _generate_image_openai(self, prompt, image_type):
        """Generate image using DALL-E (requires DALL-E API access)"""
        try:
            # Enhanced prompt based on image type
            enhanced_prompts = {
                'poster': f"Professional marketing poster: {prompt}, clean design, modern typography, eye-catching colors",
                'logo': f"Professional business logo: {prompt}, simple, memorable, scalable vector design",
                'product_image': f"Product photography: {prompt}, professional lighting, clean background, high quality",
                'social_media': f"Social media graphics: {prompt}, engaging visual, appropriate for social platforms"
            }
            
            final_prompt = enhanced_prompts.get(image_type, prompt)
            
            # Note: This requires DALL-E API access
            response = openai.Image.create(
                prompt=final_prompt,
                n=1,
                size="1024x1024"
            )
            
            return response['data'][0]['url']
            
        except Exception as e:
            print(f"DALL-E API error: {e}")
            return self._generate_image_placeholder(prompt, image_type)
    
    def _generate_image_placeholder(self, prompt, image_type):
        """Generate placeholder image data"""
        # This would integrate with other image generation services or return placeholder
        placeholder_images = {
            'poster': f"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjM2I4MmY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5Qb3N0ZXI6IHtwcm9tcHR9PC90ZXh0Pjwvc3ZnPg==",
            'logo': f"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIxMDAiIGN5PSIxMDAiIHI9IjgwIiBmaWxsPSIjMTZhMzRhIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5Mb2dvPC90ZXh0Pjwvc3ZnPg==",
            'product_image': f"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHJlY3QgeD0iNzUiIHk9Ijc1IiB3aWR0aD0iMTUwIiBoZWlnaHQ9IjE1MCIgZmlsbD0iIzllYTNhOCIvPjx0ZXh0IHg9IjUwJSIgeT0iODAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM2Yjk3Mjgiig=="
        }
        
        return placeholder_images.get(image_type, placeholder_images['poster'])
    
    def generate_business_suggestions(self, context):
        """Generate business improvement suggestions"""
        try:
            if self.use_openai:
                return self._generate_suggestions_openai(context)
            else:
                return self._generate_suggestions_template(context)
        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return self._generate_suggestions_template(context)
    
    def _generate_suggestions_openai(self, context):
        """Generate suggestions using OpenAI"""
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
                    "title": "Suggestion Title",
                    "description": "Detailed description",
                    "priority": "high|medium|low",
                    "category": "marketing|products|customer_service|operations",
                    "effort": "low|medium|high"
                }}
            ]
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert business consultant providing actionable advice for small businesses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Parse manually if JSON fails
                return self._parse_suggestions(content)
                
        except Exception as e:
            print(f"OpenAI suggestions error: {e}")
            return self._generate_suggestions_template(context)
    
    def _generate_suggestions_template(self, context):
        """Generate template suggestions"""
        suggestion_templates = {
            'marketing': [
                {
                    "title": "Improve Social Media Presence",
                    "description": f"Create regular social media posts showcasing your {context['business_type']} products and services. Share behind-the-scenes content and customer testimonials.",
                    "priority": "high",
                    "category": "marketing",
                    "effort": "medium"
                },
                {
                    "title": "Implement Email Marketing",
                    "description": "Start collecting customer emails and send regular newsletters with special offers and updates about your business.",
                    "priority": "medium",
                    "category": "marketing",
                    "effort": "low"
                }
            ],
            'products': [
                {
                    "title": "Expand Product Range",
                    "description": f"Consider adding complementary products to your current {context['total_products']} product offerings to increase average order value.",
                    "priority": "medium",
                    "category": "products",
                    "effort": "high"
                },
                {
                    "title": "Optimize Product Descriptions",
                    "description": "Update product descriptions with more details, benefits, and high-quality images to improve conversion rates.",
                    "priority": "high",
                    "category": "products",
                    "effort": "low"
                }
            ],
            'general': [
                {
                    "title": "Increase QR Code Visibility",
                    "description": f"Your QR code has been scanned {context['qr_scans']} times. Place QR codes in more visible locations to drive more traffic to your website.",
                    "priority": "high",
                    "category": "marketing",
                    "effort": "low"
                },
                {
                    "title": "Respond to Customer Messages Quickly",
                    "description": f"You have {context['recent_messages_count']} recent messages. Quick responses improve customer satisfaction and conversion rates.",
                    "priority": "high",
                    "category": "customer_service",
                    "effort": "low"
                }
            ]
        }
        
        suggestions = suggestion_templates.get(context['suggestion_type'], suggestion_templates['general'])
        
        # Add some general suggestions
        general_suggestions = [
            {
                "title": "Collect Customer Reviews",
                "description": "Actively ask satisfied customers to leave reviews on your website and social media platforms.",
                "priority": "medium",
                "category": "marketing",
                "effort": "low"
            },
            {
                "title": "Offer Loyalty Program",
                "description": "Create a simple loyalty program to encourage repeat customers and increase customer lifetime value.",
                "priority": "medium",
                "category": "customer_service",
                "effort": "medium"
            }
        ]
        
        return {
            "suggestions": suggestions + random.sample(general_suggestions, min(2, len(general_suggestions)))
        }
    
    def analyze_customer_feedback(self, feedback_texts):
        """Analyze customer feedback for insights"""
        try:
            if self.use_openai and feedback_texts:
                return self._analyze_feedback_openai(feedback_texts)
            else:
                return self._analyze_feedback_template(feedback_texts)
        except Exception as e:
            print(f"Error analyzing feedback: {e}")
            return self._analyze_feedback_template(feedback_texts)
    
    def _analyze_feedback_openai(self, feedback_texts):
        """Analyze feedback using OpenAI"""
        combined_feedback = "\n\n".join(feedback_texts[:20])  # Limit to first 20 for token limits
        
        prompt = f"""
        Analyze the following customer feedback and provide insights:
        
        {combined_feedback}
        
        Provide analysis in JSON format:
        {{
            "overall_sentiment": "positive|negative|neutral",
            "key_themes": ["theme1", "theme2", "theme3"],
            "strengths": ["strength1", "strength2"],
            "areas_for_improvement": ["area1", "area2"],
            "recommendations": ["recommendation1", "recommendation2"],
            "summary": "Brief summary of the feedback analysis"
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a customer feedback analyst providing actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return self._parse_feedback_analysis(content)
                
        except Exception as e:
            print(f"OpenAI feedback analysis error: {e}")
            return self._analyze_feedback_template(feedback_texts)
    
    def _analyze_feedback_template(self, feedback_texts):
        """Generate template feedback analysis"""
        if not feedback_texts:
            return {
                "overall_sentiment": "neutral",
                "key_themes": ["No feedback available"],
                "strengths": ["Opportunity to collect more feedback"],
                "areas_for_improvement": ["Gather more customer feedback"],
                "recommendations": ["Implement feedback collection system", "Ask customers for reviews"],
                "summary": "No customer feedback available for analysis. Consider implementing feedback collection mechanisms."
            }
        
        # Simple keyword analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'perfect', 'wonderful']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disappointing']
        
        all_text = ' '.join(feedback_texts).lower()
        positive_count = sum(word in all_text for word in positive_words)
        negative_count = sum(word in all_text for word in negative_words)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "overall_sentiment": sentiment,
            "key_themes": ["Customer service", "Product quality", "User experience"],
            "strengths": ["Customer engagement", "Feedback collection"],
            "areas_for_improvement": ["Response time", "Product information"],
            "recommendations": [
                "Continue collecting customer feedback",
                "Address common concerns promptly",
                "Leverage positive feedback for marketing"
            ],
            "summary": f"Analysis of {len(feedback_texts)} feedback items shows {sentiment} sentiment overall."
        }
    
    def chatbot_response(self, message, user_context=None, conversation_history=None):
        """Generate chatbot response for business assistance"""
        try:
            if self.use_openai:
                return self._chatbot_response_openai(message, user_context, conversation_history)
            else:
                return self._chatbot_response_template(message, user_context)
        except Exception as e:
            print(f"Error generating chatbot response: {e}")
            return self._chatbot_response_template(message, user_context)
    
    def _chatbot_response_openai(self, message, user_context, conversation_history):
        """Generate chatbot response using OpenAI"""
        system_prompt = f"""
        You are a helpful business assistant for {user_context.get('business_name', 'a small business')} 
        ({user_context.get('business_type', 'business')}). 
        
        Provide helpful, actionable advice about:
        - Business management and operations
        - Marketing and customer acquisition
        - Product management
        - Customer service
        - Using the Break-even platform features
        
        Keep responses concise, practical, and friendly.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        if conversation_history:
            for hist in conversation_history[-5:]:  # Last 5 exchanges
                messages.append({"role": "user", "content": hist['user_message']})
                messages.append({"role": "assistant", "content": hist['bot_response']})
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI chatbot error: {e}")
            return self._chatbot_response_template(message, user_context)
    
    def _chatbot_response_template(self, message, user_context):
        """Generate template chatbot response"""
        message_lower = message.lower()
        
        # Simple keyword-based responses
        if any(word in message_lower for word in ['help', 'how', 'what']):
            return f"I'm here to help you with your {user_context.get('business_type', 'business')}! You can ask me about marketing, customer management, products, or using the Break-even platform features."
        
        elif any(word in message_lower for word in ['marketing', 'promote', 'advertise']):
            return "For marketing, consider: 1) Use your QR code in visible locations, 2) Collect customer emails for newsletters, 3) Ask satisfied customers for reviews, 4) Use social media regularly, 5) Offer special promotions to new customers."
        
        elif any(word in message_lower for word in ['customer', 'client']):
            return "To improve customer service: 1) Respond to messages quickly, 2) Collect feedback regularly, 3) Follow up after purchases, 4) Create a loyalty program, 5) Personalize your communication."
        
        elif any(word in message_lower for word in ['product', 'inventory']):
            return "For product management: 1) Keep descriptions updated, 2) Use high-quality images, 3) Monitor stock levels, 4) Analyze which products are popular, 5) Consider bundling complementary items."
        
        elif any(word in message_lower for word in ['website', 'qr', 'online']):
            return "To improve your online presence: 1) Keep your website updated, 2) Place QR codes prominently in your store, 3) Track QR scan analytics, 4) Make sure contact info is current, 5) Add new products regularly."
        
        else:
            return f"Thanks for your question about {user_context.get('business_name', 'your business')}! I can help you with marketing, customer management, products, and platform features. What specific area would you like assistance with?"
    
    def _parse_suggestions(self, content):
        """Parse suggestions from text if JSON parsing fails"""
        # Basic parsing logic - you can improve this
        return {
            "suggestions": [
                {
                    "title": "Improve Customer Communication",
                    "description": "Respond to customer messages promptly to improve satisfaction.",
                    "priority": "high",
                    "category": "customer_service",
                    "effort": "low"
                },
                {
                    "title": "Enhance Marketing Efforts",
                    "description": "Use social media and email marketing to reach more customers.",
                    "priority": "medium",
                    "category": "marketing",
                    "effort": "medium"
                }
            ]
        }
    
    def _parse_feedback_analysis(self, content):
        """Parse feedback analysis from text if JSON parsing fails"""
        return {
            "overall_sentiment": "neutral",
            "key_themes": ["Customer feedback analysis"],
            "strengths": ["Customer engagement"],
            "areas_for_improvement": ["Feedback processing"],
            "recommendations": ["Continue gathering feedback", "Improve response processes"],
            "summary": "Feedback analysis completed with actionable insights."
        }
