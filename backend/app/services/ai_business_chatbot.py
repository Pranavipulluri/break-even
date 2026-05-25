"""
AI Business Chatbot Service using Gemini API
Acts as a business co-partner providing insights, advice, and assistance
"""

import requests
import logging
import os
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class AIBusinessChatbotService:
    """AI Business Chatbot that acts as a co-partner"""
    
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
        
        # Business co-partner personality and knowledge base
        self.system_prompt = """You are an AI business co-partner and advisor for Break-even platform users. You have extensive knowledge about:

- Business strategy and growth
- Marketing and customer acquisition  
- Financial planning and analysis
- Digital marketing and social media
- E-commerce and online presence
- Customer service excellence
- Operational efficiency
- Industry trends and insights

Your personality:
- Supportive and encouraging business partner
- Data-driven but approachable
- Practical and actionable advice
- Enthusiastic about helping businesses succeed
- Professional yet friendly tone

Always provide:
- Specific, actionable advice
- Ask clarifying questions when needed
- Reference relevant business metrics or KPIs
- Suggest Break-even platform features when appropriate
- Be concise but comprehensive
- Use emojis sparingly but effectively

Respond in the user's language if they write in a different language.
"""

    def get_business_response(self, message, language='en', user_context=None, conversation_history=None):
        """
        Get AI business partner response using Gemini API
        """
        try:
            # Build context from user information
            context_info = ""
            if user_context:
                context_info = f"""
User Context:
- Business Owner: {user_context.get('name', 'Business Owner')}
- Business Type: {user_context.get('business_type', 'General Business')}
- Business Name: {user_context.get('business_name', 'Their Business')}
"""

            # Build conversation context
            conversation_context = ""
            if conversation_history:
                recent_messages = conversation_history[-3:]  # Last 3 messages
                conversation_context = "\nRecent conversation:\n"
                for msg in recent_messages:
                    role = "User" if msg.get('type') == 'user' else "Assistant"
                    conversation_context += f"{role}: {msg.get('content', '')}\n"

            # Create the prompt
            prompt = f"""{self.system_prompt}

{context_info}

{conversation_context}

Language: Respond in {self._get_language_name(language)}

User Message: {message}

Provide a helpful, business-focused response as their AI co-partner:"""

            # Prepare Gemini API request
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024
                }
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            url = f"{self.gemini_api_url}?key={self.gemini_api_key}"
            
            logger.info(f"Making Gemini API request for business chat")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        ai_response = candidate['content']['parts'][0]['text'].strip()
                        logger.info(f"Gemini business chat response generated successfully")
                        return ai_response
                
                logger.warning("Unexpected Gemini API response format")
                return self._get_fallback_response(message, language)
                
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return self._get_fallback_response(message, language)
                
        except Exception as e:
            logger.error(f"Error calling Gemini API for business chat: {e}")
            return self._get_fallback_response(message, language)

    def _get_language_name(self, language_code):
        """Convert language code to full name"""
        languages = {
            'en': 'English',
            'te': 'Telugu',
            'hi': 'Hindi',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German'
        }
        return languages.get(language_code, 'English')

    def _get_fallback_response(self, message, language='en'):
        """Provide fallback responses when API fails"""
        fallback_responses = {
            'en': {
                'default': "I'm here to help with your business! While I'm experiencing some technical difficulties, I'd love to assist you with business strategy, marketing ideas, or growth opportunities. Could you tell me more about what specific area you'd like help with?",
                'sales': "For sales growth, consider: 1) Improving your online presence 2) Customer referral programs 3) Social media marketing 4) Email campaigns. What's your current biggest sales challenge?",
                'marketing': "Great marketing strategies include: 1) Content marketing 2) Social media engagement 3) Local SEO 4) Customer testimonials. Which area interests you most?",
                'financial': "For financial success: 1) Track key metrics 2) Control costs 3) Improve cash flow 4) Plan for growth. What financial aspect concerns you most?"
            },
            'te': {
                'default': "మీ వ్యాపారంలో సహాయం చేయడానికి నేను ఇక్కడ ఉన్నాను! సాంకేతిక సమస్యలు ఉన్నప్పటికీ, వ్యాపార వ్యూహం, మార్కెటింగ్ ఆలోచనలు లేదా వృద్ధి అవకాశాలతో మీకు సహాయం చేయాలని అనుకుంటున్నాను।",
                'sales': "అమ్మకాల వృద్ధికి: 1) ఆన్‌లైన్ ప్రాతినిధ్యం మెరుగుపరచండి 2) కస్టమర్ రెఫరల్ ప్రోగ్రామ్‌లు 3) సోషల్ మీడియా మార్కెటింగ్ 4) ఇమెయిల్ ప్రచారాలు",
                'marketing': "గొప్ప మార్కెటింగ్ వ్యూహాలు: 1) కంటెంట్ మార్కెటింగ్ 2) సోషల్ మీడియా ఎంగేజ్‌మెంట్ 3) స్థానిక SEO 4) కస్టమర్ టెస్టిమోనియల్స్"
            },
            'hi': {
                'default': "मैं आपके व्यापार में मदद के लिए यहाँ हूँ! तकनीकी कठिनाइयों के बावजूद, मैं व्यापारिक रणनीति, मार्केटिंग विचार, या विकास के अवसरों में आपकी सहायता करना चाहूँगा।",
                'sales': "बिक्री वृद्धि के लिए: 1) ऑनलाइन उपस्थिति सुधारें 2) ग्राहक रेफरल प्रोग्राम 3) सोशल मीडिया मार्केटिंग 4) ईमेल अभियान",
                'marketing': "बेहतरीन मार्केटिंग रणनीतियां: 1) कंटेंट मार्केटिंग 2) सोशल मीडिया एंगेजमेंट 3) स्थानीय SEO 4) ग्राहक प्रशंसापत्र"
            }
        }
        
        # Determine response category based on message content
        message_lower = message.lower()
        if any(word in message_lower for word in ['sales', 'sell', 'revenue', 'income']):
            category = 'sales'
        elif any(word in message_lower for word in ['marketing', 'promotion', 'advertise', 'brand']):
            category = 'marketing'
        elif any(word in message_lower for word in ['money', 'profit', 'cost', 'finance', 'budget']):
            category = 'financial'
        else:
            category = 'default'
        
        responses = fallback_responses.get(language, fallback_responses['en'])
        return responses.get(category, responses['default'])

    def get_business_insights(self, user_id, language='en'):
        """
        Generate business insights based on user's data
        """
        try:
            # This would typically fetch user's business data
            # For now, provide general insights
            
            prompt = f"""As an AI business advisor, provide 3-5 key business insights and recommendations for a Break-even platform user. 

Include insights about:
- Growth opportunities
- Marketing strategies  
- Customer engagement
- Performance optimization
- Industry trends

Respond in {self._get_language_name(language)}.
Format as bullet points with actionable advice.
Be encouraging and specific."""

            return self.get_business_response(prompt, language)
            
        except Exception as e:
            logger.error(f"Error generating business insights: {e}")
            return self._get_fallback_response("insights", language)

# Global instance
ai_business_chatbot = AIBusinessChatbotService()