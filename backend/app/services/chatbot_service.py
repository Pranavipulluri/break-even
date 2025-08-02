"""
AI Chatbot Service for Break-Even Application
Provides intelligent customer support and business assistance using Gemini AI
"""

import json
from datetime import datetime, timedelta
from flask import current_app
from app import mongo
from app.services.gemini_service import get_gemini_service
from bson import ObjectId
import logging

class ChatbotService:
    def __init__(self):
        self.gemini_service = get_gemini_service()
        self.conversation_limit = 10  # Keep last 10 messages for context
        
    def get_chat_response(self, message, user_id, business_id=None, conversation_id=None):
        """Generate intelligent chat response using Gemini AI with business context"""
        try:
            # Get or create conversation
            if not conversation_id:
                conversation_id = self._create_conversation(user_id, business_id)
            
            # Get conversation history
            conversation_history = self._get_conversation_history(conversation_id)
            
            # Get business context
            business_context = self._get_business_context(user_id, business_id)
            
            # Get customer context
            customer_context = self._get_customer_context(user_id)
            
            # Generate response using Gemini AI
            response = self._generate_ai_response(
                message, 
                business_context, 
                customer_context, 
                conversation_history
            )
            
            # Save message and response to conversation
            self._save_message_to_conversation(conversation_id, message, response, user_id)
            
            # Analyze message sentiment and intent
            message_analysis = self._analyze_message(message)
            
            return {
                'success': True,
                'response': response,
                'conversation_id': conversation_id,
                'analysis': message_analysis,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Chatbot error: {str(e)}")
            return {
                'success': False,
                'response': "I apologize, but I'm having trouble processing your request right now. Please try again or contact support.",
                'error': str(e)
            }
    
    def _create_conversation(self, user_id, business_id=None):
        """Create a new conversation record"""
        conversation = {
            'user_id': ObjectId(user_id) if user_id else None,
            'business_id': ObjectId(business_id) if business_id else None,
            'created_at': datetime.utcnow(),
            'last_message_at': datetime.utcnow(),
            'message_count': 0,
            'status': 'active'
        }
        
        result = mongo.db.chatbot_conversations.insert_one(conversation)
        return str(result.inserted_id)
    
    def _get_conversation_history(self, conversation_id):
        """Get recent conversation history for context"""
        messages = list(mongo.db.chatbot_messages.find({
            'conversation_id': ObjectId(conversation_id)
        }).sort('created_at', -1).limit(self.conversation_limit))
        
        # Reverse to get chronological order
        messages.reverse()
        
        return [
            {
                'user_message': msg['user_message'],
                'bot_response': msg['bot_response'],
                'timestamp': msg['created_at']
            }
            for msg in messages
        ]
    
    def _get_business_context(self, user_id, business_id=None):
        """Get business context for personalized responses"""
        try:
            # Get user's business information
            user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if not user:
                return {}
            
            # Get business data
            business_data = {
                'business_name': user.get('business_name', 'your business'),
                'business_type': user.get('business_type', 'business'),
                'industry': user.get('industry', 'general'),
                'location': user.get('area', 'N/A')
            }
            
            # Get recent analytics
            analytics = self._get_recent_analytics(user_id)
            business_data.update(analytics)
            
            # Get product information
            products = list(mongo.db.products.find({
                'user_id': ObjectId(user_id),
                'is_active': True
            }).limit(10))
            
            business_data['products'] = [
                {
                    'name': p['name'],
                    'category': p.get('category', 'N/A'),
                    'price': p.get('price', 0)
                }
                for p in products
            ]
            
            return business_data
            
        except Exception as e:
            logging.error(f"Error getting business context: {str(e)}")
            return {}
    
    def _get_customer_context(self, user_id):
        """Get customer interaction context"""
        try:
            # Get recent customer messages
            recent_messages = mongo.db.messages.count_documents({
                'recipient_id': ObjectId(user_id),
                'created_at': {'$gte': datetime.utcnow() - timedelta(days=7)}
            })
            
            # Get recent feedback
            recent_feedback = list(mongo.db.customer_feedback.find({
                'business_owner_id': ObjectId(user_id),
                'created_at': {'$gte': datetime.utcnow() - timedelta(days=30)}
            }).limit(5))
            
            # Get customer registrations
            new_customers = mongo.db.child_customers.count_documents({
                'business_owner_id': ObjectId(user_id),
                'created_at': {'$gte': datetime.utcnow() - timedelta(days=7)}
            })
            
            return {
                'recent_messages': recent_messages,
                'recent_feedback_count': len(recent_feedback),
                'new_customers_week': new_customers,
                'recent_feedback_summary': self._summarize_feedback(recent_feedback)
            }
            
        except Exception as e:
            logging.error(f"Error getting customer context: {str(e)}")
            return {}
    
    def _get_recent_analytics(self, user_id):
        """Get recent business analytics"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            # QR scans
            qr_analytics = mongo.db.qr_analytics.find_one({'user_id': ObjectId(user_id)})
            total_scans = qr_analytics.get('total_scans', 0) if qr_analytics else 0
            
            # Website visits
            website_visits = mongo.db.website_analytics.count_documents({
                'business_owner_id': ObjectId(user_id),
                'visited_at': {'$gte': start_date}
            })
            
            # Product interactions
            product_interactions = mongo.db.product_interactions.count_documents({
                'business_owner_id': ObjectId(user_id),
                'created_at': {'$gte': start_date}
            })
            
            return {
                'total_qr_scans': total_scans,
                'website_visits_month': website_visits,
                'product_interactions_month': product_interactions
            }
            
        except Exception as e:
            logging.error(f"Error getting analytics: {str(e)}")
            return {}
    
    def _summarize_feedback(self, feedback_list):
        """Summarize recent feedback"""
        if not feedback_list:
            return "No recent feedback"
        
        positive = sum(1 for f in feedback_list if f.get('sentiment', {}).get('label') == 'positive')
        negative = sum(1 for f in feedback_list if f.get('sentiment', {}).get('label') == 'negative')
        
        return f"{positive} positive, {negative} negative out of {len(feedback_list)} recent feedback"
    
    def _generate_ai_response(self, message, business_context, customer_context, conversation_history):
        """Generate AI response using Gemini with comprehensive context"""
        
        # Build comprehensive prompt
        system_prompt = f"""
You are an intelligent business assistant for {business_context.get('business_name', 'this business')}, 
a {business_context.get('business_type', 'business')} operating in {business_context.get('location', 'the market')}.

BUSINESS CONTEXT:
- Business Type: {business_context.get('business_type', 'N/A')}
- Industry: {business_context.get('industry', 'N/A')}
- Products: {len(business_context.get('products', []))} active products
- Recent Performance:
  - QR Scans: {business_context.get('total_qr_scans', 0)}
  - Website Visits (30 days): {business_context.get('website_visits_month', 0)}
  - Product Interactions: {business_context.get('product_interactions_month', 0)}

CUSTOMER INSIGHTS:
- Recent Messages: {customer_context.get('recent_messages', 0)}
- New Customers (7 days): {customer_context.get('new_customers_week', 0)}
- Feedback Summary: {customer_context.get('recent_feedback_summary', 'N/A')}

YOUR CAPABILITIES:
1. Business Strategy & Growth Advice
2. Marketing & Customer Acquisition
3. Product Management & Optimization  
4. Customer Service Best Practices
5. Platform Feature Guidance
6. Financial Planning & Analysis
7. Digital Marketing Strategies
8. Operational Efficiency Tips

RESPONSE GUIDELINES:
- Be helpful, professional, and actionable
- Use the business context to provide personalized advice
- Keep responses concise but comprehensive (2-5 sentences)
- Provide specific, implementable suggestions
- Reference the user's actual business data when relevant
- Ask clarifying questions when needed
- Encourage use of platform features

CONVERSATION HISTORY:
"""
        
        # Add conversation history
        if conversation_history:
            for hist in conversation_history[-5:]:  # Last 5 exchanges
                system_prompt += f"\nUser: {hist['user_message']}\nAssistant: {hist['bot_response']}"
        
        # Add current message
        full_prompt = f"{system_prompt}\n\nCurrent User Message: {message}\n\nYour Response:"
        
        # Generate response using Gemini
        result = self.gemini_service.generate_content(full_prompt, max_tokens=400)
        
        if result.get('success'):
            return result['content']
        else:
            return self._get_fallback_response(message, business_context)
    
    def _get_fallback_response(self, message, business_context):
        """Provide fallback response when AI is unavailable"""
        business_name = business_context.get('business_name', 'your business')
        
        # Simple keyword-based responses
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['help', 'support', 'how']):
            return f"I'm here to help you grow {business_name}! I can assist with marketing strategies, customer management, product optimization, and platform features. What specific area would you like guidance on?"
        
        elif any(word in message_lower for word in ['customers', 'customer', 'client']):
            return f"Customer growth is crucial for {business_name}! Consider optimizing your QR code placement, improving your website content, and engaging with recent feedback. Would you like specific customer acquisition strategies?"
        
        elif any(word in message_lower for word in ['marketing', 'promote', 'advertise']):
            return f"Great question about marketing {business_name}! Focus on your unique value proposition, leverage customer testimonials, and use social media consistently. What marketing channels are you currently using?"
        
        elif any(word in message_lower for word in ['product', 'inventory', 'stock']):
            return f"Product management is key to {business_name}'s success! Analyze your product performance data, optimize descriptions, and consider customer feedback for improvements. Need help with specific products?"
        
        else:
            return f"Thank you for your question about {business_name}! I can help with business strategy, marketing, customer management, and platform optimization. Could you be more specific about what you'd like assistance with?"
    
    def _analyze_message(self, message):
        """Analyze message sentiment and intent"""
        try:
            analysis_prompt = f"""
Analyze this customer message for sentiment and intent:
"{message}"

Return JSON with:
{{
    "sentiment": "positive|negative|neutral",
    "intent": "question|complaint|compliment|request|other",
    "topic": "marketing|customers|products|support|general",
    "urgency": "low|medium|high"
}}
"""
            
            result = self.gemini_service.generate_content(analysis_prompt, max_tokens=100)
            
            if result.get('success'):
                try:
                    content = result['content'].strip()
                    if content.startswith('```json'):
                        content = content.replace('```json', '').replace('```', '').strip()
                    return json.loads(content)
                except json.JSONDecodeError:
                    pass
            
            # Fallback analysis
            return {
                "sentiment": "neutral",
                "intent": "question",
                "topic": "general",
                "urgency": "low"
            }
            
        except Exception as e:
            logging.error(f"Message analysis error: {str(e)}")
            return {
                "sentiment": "neutral",
                "intent": "question", 
                "topic": "general",
                "urgency": "low"
            }
    
    def _save_message_to_conversation(self, conversation_id, user_message, bot_response, user_id):
        """Save message exchange to database"""
        try:
            # Save message
            message_record = {
                'conversation_id': ObjectId(conversation_id),
                'user_id': ObjectId(user_id) if user_id else None,
                'user_message': user_message,
                'bot_response': bot_response,
                'created_at': datetime.utcnow()
            }
            
            mongo.db.chatbot_messages.insert_one(message_record)
            
            # Update conversation
            mongo.db.chatbot_conversations.update_one(
                {'_id': ObjectId(conversation_id)},
                {
                    '$set': {'last_message_at': datetime.utcnow()},
                    '$inc': {'message_count': 1}
                }
            )
            
        except Exception as e:
            logging.error(f"Error saving message: {str(e)}")
    
    def get_conversation_summary(self, conversation_id):
        """Get conversation summary and insights"""
        try:
            conversation = mongo.db.chatbot_conversations.find_one({
                '_id': ObjectId(conversation_id)
            })
            
            if not conversation:
                return None
            
            messages = list(mongo.db.chatbot_messages.find({
                'conversation_id': ObjectId(conversation_id)
            }).sort('created_at', 1))
            
            # Analyze conversation themes
            all_messages = [msg['user_message'] for msg in messages]
            themes = self._analyze_conversation_themes(all_messages)
            
            return {
                'conversation_id': conversation_id,
                'created_at': conversation['created_at'],
                'message_count': len(messages),
                'themes': themes,
                'duration': (datetime.utcnow() - conversation['created_at']).total_seconds() / 60,  # minutes
                'last_activity': conversation['last_message_at']
            }
            
        except Exception as e:
            logging.error(f"Error getting conversation summary: {str(e)}")
            return None
    
    def _analyze_conversation_themes(self, messages):
        """Analyze conversation themes using AI"""
        if not messages:
            return []
        
        try:
            combined_messages = "\n".join(messages[-10:])  # Last 10 messages
            
            theme_prompt = f"""
Analyze these conversation messages and identify the main themes/topics discussed:
{combined_messages}

Return the top 3 themes as a JSON array of strings.
Example: ["marketing advice", "customer service", "product optimization"]
"""
            
            result = self.gemini_service.generate_content(theme_prompt, max_tokens=100)
            
            if result.get('success'):
                try:
                    content = result['content'].strip()
                    if content.startswith('```json'):
                        content = content.replace('```json', '').replace('```', '').strip()
                    elif content.startswith('['):
                        return json.loads(content)
                    else:
                        # Parse as simple list
                        themes = [theme.strip('"') for theme in content.split(',')]
                        return themes[:3]
                except:
                    pass
            
            return ["general business discussion"]
            
        except Exception as e:
            logging.error(f"Theme analysis error: {str(e)}")
            return ["general business discussion"]
    
    def train_from_feedback(self, user_id):
        """Train chatbot responses based on user feedback and interactions"""
        try:
            # Get recent customer feedback
            feedback = list(mongo.db.customer_feedback.find({
                'business_owner_id': ObjectId(user_id),
                'created_at': {'$gte': datetime.utcnow() - timedelta(days=90)}
            }))
            
            # Get frequently asked questions from messages
            messages = list(mongo.db.messages.find({
                'recipient_id': ObjectId(user_id),
                'created_at': {'$gte': datetime.utcnow() - timedelta(days=60)}
            }))
            
            # Generate training insights
            training_data = {
                'common_customer_concerns': self._extract_common_concerns(feedback),
                'frequently_asked_questions': self._extract_faqs(messages),
                'business_strengths': self._extract_strengths(feedback),
                'improvement_areas': self._extract_improvement_areas(feedback),
                'generated_at': datetime.utcnow()
            }
            
            # Save training data
            mongo.db.chatbot_training.update_one(
                {'user_id': ObjectId(user_id)},
                {'$set': training_data},
                upsert=True
            )
            
            return {
                'success': True,
                'message': 'Chatbot training updated successfully',
                'insights_count': len(training_data['common_customer_concerns']) + len(training_data['frequently_asked_questions'])
            }
            
        except Exception as e:
            logging.error(f"Training error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_common_concerns(self, feedback):
        """Extract common customer concerns from feedback"""
        if not feedback:
            return []
        
        try:
            feedback_texts = [f.get('feedback_text', '') for f in feedback if f.get('feedback_text')]
            
            if not feedback_texts:
                return []
            
            combined_feedback = "\n".join(feedback_texts[:20])  # Limit for API
            
            prompt = f"""
Analyze this customer feedback and identify the top 5 common concerns or issues:
{combined_feedback}

Return as JSON array of concern descriptions.
Example: ["slow delivery times", "product quality issues", "unclear pricing"]
"""
            
            result = self.gemini_service.generate_content(prompt, max_tokens=200)
            
            if result.get('success'):
                try:
                    content = result['content'].strip()
                    if content.startswith('```json'):
                        content = content.replace('```json', '').replace('```', '').strip()
                    return json.loads(content)
                except:
                    pass
            
            return []
            
        except Exception as e:
            logging.error(f"Concern extraction error: {str(e)}")
            return []
    
    def _extract_faqs(self, messages):
        """Extract frequently asked questions from customer messages"""
        if not messages:
            return []
        
        try:
            question_messages = []
            for msg in messages:
                content = msg.get('content', '').strip()
                if content and ('?' in content or any(word in content.lower() for word in ['how', 'what', 'when', 'where', 'why', 'can you'])):
                    question_messages.append(content)
            
            if not question_messages:
                return []
            
            combined_questions = "\n".join(question_messages[:15])
            
            prompt = f"""
Analyze these customer questions and identify the top 5 most common types of questions:
{combined_questions}

Return as JSON array of generalized question types.
Example: ["How do I place an order?", "What are your business hours?", "Do you offer delivery?"]
"""
            
            result = self.gemini_service.generate_content(prompt, max_tokens=200)
            
            if result.get('success'):
                try:
                    content = result['content'].strip()
                    if content.startswith('```json'):
                        content = content.replace('```json', '').replace('```', '').strip()
                    return json.loads(content)
                except:
                    pass
            
            return []
            
        except Exception as e:
            logging.error(f"FAQ extraction error: {str(e)}")
            return []
    
    def _extract_strengths(self, feedback):
        """Extract business strengths from positive feedback"""
        if not feedback:
            return []
        
        try:
            positive_feedback = [
                f.get('feedback_text', '') 
                for f in feedback 
                if f.get('sentiment', {}).get('label') == 'positive' and f.get('feedback_text')
            ]
            
            if not positive_feedback:
                return []
            
            combined_positive = "\n".join(positive_feedback[:15])
            
            prompt = f"""
Analyze this positive customer feedback and identify the top 3 business strengths mentioned:
{combined_positive}

Return as JSON array of strength descriptions.
Example: ["excellent customer service", "high quality products", "fast delivery"]
"""
            
            result = self.gemini_service.generate_content(prompt, max_tokens=150)
            
            if result.get('success'):
                try:
                    content = result['content'].strip()
                    if content.startswith('```json'):
                        content = content.replace('```json', '').replace('```', '').strip()
                    return json.loads(content)
                except:
                    pass
            
            return []
            
        except Exception as e:
            logging.error(f"Strengths extraction error: {str(e)}")
            return []
    
    def _extract_improvement_areas(self, feedback):
        """Extract improvement areas from negative feedback"""
        if not feedback:
            return []
        
        try:
            negative_feedback = [
                f.get('feedback_text', '') 
                for f in feedback 
                if f.get('sentiment', {}).get('label') == 'negative' and f.get('feedback_text')
            ]
            
            if not negative_feedback:
                return []
            
            combined_negative = "\n".join(negative_feedback[:15])
            
            prompt = f"""
Analyze this negative customer feedback and identify the top 3 areas for improvement:
{combined_negative}

Return as JSON array of improvement area descriptions.
Example: ["improve response time", "better product descriptions", "clearer pricing"]
"""
            
            result = self.gemini_service.generate_content(prompt, max_tokens=150)
            
            if result.get('success'):
                try:
                    content = result['content'].strip()
                    if content.startswith('```json'):
                        content = content.replace('```json', '').replace('```', '').strip()
                    return json.loads(content)
                except:
                    pass
            
            return []
            
        except Exception as e:
            logging.error(f"Improvement areas extraction error: {str(e)}")
            return []


# Global service instance
chatbot_service = None

def get_chatbot_service():
    """Get or create chatbot service instance"""
    global chatbot_service
    if chatbot_service is None:
        chatbot_service = ChatbotService()
    return chatbot_service
