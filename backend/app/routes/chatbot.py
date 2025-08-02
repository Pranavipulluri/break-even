"""
AI Chatbot API Routes for Break-Even Application
Provides intelligent business assistance and customer support
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.services.chatbot_service import get_chatbot_service
from bson import ObjectId
from datetime import datetime, timedelta
import logging

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chatbot/chat', methods=['POST'])
@jwt_required()
def chat_with_assistant():
    """Send message to AI business assistant"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        business_id = data.get('business_id')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Get chatbot service
        chatbot_service = get_chatbot_service()
        
        # Generate response
        result = chatbot_service.get_chat_response(
            message=message,
            user_id=current_user_id,
            business_id=business_id,
            conversation_id=conversation_id
        )
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        logging.error(f"Chat endpoint error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'Please try again later'
        }), 500

@chatbot_bp.route('/chatbot/conversations', methods=['GET'])
@jwt_required()
def get_user_conversations():
    """Get user's chat conversations"""
    try:
        current_user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Get conversations
        conversations = list(mongo.db.chatbot_conversations.find({
            'user_id': ObjectId(current_user_id)
        }).sort('last_message_at', -1).skip((page - 1) * limit).limit(limit))
        
        # Get message counts and last messages
        conversation_list = []
        for conv in conversations:
            # Get last message
            last_message = mongo.db.chatbot_messages.find_one({
                'conversation_id': conv['_id']
            }, sort=[('created_at', -1)])
            
            conversation_list.append({
                'id': str(conv['_id']),
                'created_at': conv['created_at'].isoformat(),
                'last_message_at': conv['last_message_at'].isoformat(),
                'message_count': conv.get('message_count', 0),
                'status': conv.get('status', 'active'),
                'last_message_preview': last_message['user_message'][:100] + '...' if last_message and len(last_message['user_message']) > 100 else last_message['user_message'] if last_message else 'No messages'
            })
        
        # Get total count for pagination
        total_conversations = mongo.db.chatbot_conversations.count_documents({
            'user_id': ObjectId(current_user_id)
        })
        
        return jsonify({
            'success': True,
            'conversations': conversation_list,
            'pagination': {
                'current_page': page,
                'total_pages': (total_conversations + limit - 1) // limit,
                'total_conversations': total_conversations,
                'has_next': page * limit < total_conversations,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Get conversations error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch conversations'
        }), 500

@chatbot_bp.route('/chatbot/conversations/<conversation_id>/messages', methods=['GET'])
@jwt_required()
def get_conversation_messages(conversation_id):
    """Get messages from a specific conversation"""
    try:
        current_user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        
        # Verify conversation belongs to user
        conversation = mongo.db.chatbot_conversations.find_one({
            '_id': ObjectId(conversation_id),
            'user_id': ObjectId(current_user_id)
        })
        
        if not conversation:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        # Get messages
        messages = list(mongo.db.chatbot_messages.find({
            'conversation_id': ObjectId(conversation_id)
        }).sort('created_at', -1).skip((page - 1) * limit).limit(limit))
        
        # Reverse for chronological order
        messages.reverse()
        
        message_list = []
        for msg in messages:
            message_list.append({
                'id': str(msg['_id']),
                'user_message': msg['user_message'],
                'bot_response': msg['bot_response'],
                'created_at': msg['created_at'].isoformat()
            })
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'messages': message_list,
            'conversation_info': {
                'created_at': conversation['created_at'].isoformat(),
                'message_count': conversation.get('message_count', 0),
                'status': conversation.get('status', 'active')
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Get messages error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch messages'
        }), 500

@chatbot_bp.route('/chatbot/conversations/<conversation_id>/summary', methods=['GET'])
@jwt_required()
def get_conversation_summary(conversation_id):
    """Get conversation summary and insights"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify conversation belongs to user
        conversation = mongo.db.chatbot_conversations.find_one({
            '_id': ObjectId(conversation_id),
            'user_id': ObjectId(current_user_id)
        })
        
        if not conversation:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        # Get summary from chatbot service
        chatbot_service = get_chatbot_service()
        summary = chatbot_service.get_conversation_summary(conversation_id)
        
        if summary:
            return jsonify({
                'success': True,
                'summary': summary
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate summary'
            }), 500
        
    except Exception as e:
        logging.error(f"Get summary error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch conversation summary'
        }), 500

@chatbot_bp.route('/chatbot/train', methods=['POST'])
@jwt_required()
def train_chatbot():
    """Train chatbot with user's business data"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get chatbot service
        chatbot_service = get_chatbot_service()
        
        # Train with user's data
        result = chatbot_service.train_from_feedback(current_user_id)
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        logging.error(f"Train chatbot error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to train chatbot'
        }), 500

@chatbot_bp.route('/chatbot/analytics', methods=['GET'])
@jwt_required()
def get_chatbot_analytics():
    """Get chatbot usage analytics"""
    try:
        current_user_id = get_jwt_identity()
        days = int(request.args.get('days', 30))
        
        # Date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get conversations in date range
        conversations = list(mongo.db.chatbot_conversations.find({
            'user_id': ObjectId(current_user_id),
            'created_at': {'$gte': start_date, '$lte': end_date}
        }))
        
        # Get messages in date range
        total_messages = mongo.db.chatbot_messages.count_documents({
            'user_id': ObjectId(current_user_id),
            'created_at': {'$gte': start_date, '$lte': end_date}
        })
        
        # Calculate analytics
        total_conversations = len(conversations)
        active_conversations = sum(1 for c in conversations if c.get('status') == 'active')
        
        # Average messages per conversation
        avg_messages_per_conversation = (
            sum(c.get('message_count', 0) for c in conversations) / total_conversations
            if total_conversations > 0 else 0
        )
        
        # Get conversation duration analytics
        durations = []
        for conv in conversations:
            if conv.get('last_message_at'):
                duration = (conv['last_message_at'] - conv['created_at']).total_seconds() / 60
                durations.append(duration)
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Get recent training data
        training_data = mongo.db.chatbot_training.find_one({
            'user_id': ObjectId(current_user_id)
        })
        
        # Daily usage trend
        daily_usage = []
        for i in range(days):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_conversations = mongo.db.chatbot_conversations.count_documents({
                'user_id': ObjectId(current_user_id),
                'created_at': {'$gte': day_start, '$lt': day_end}
            })
            
            day_messages = mongo.db.chatbot_messages.count_documents({
                'user_id': ObjectId(current_user_id),
                'created_at': {'$gte': day_start, '$lt': day_end}
            })
            
            daily_usage.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'conversations': day_conversations,
                'messages': day_messages
            })
        
        return jsonify({
            'success': True,
            'analytics': {
                'total_conversations': total_conversations,
                'active_conversations': active_conversations,
                'total_messages': total_messages,
                'avg_messages_per_conversation': round(avg_messages_per_conversation, 2),
                'avg_conversation_duration_minutes': round(avg_duration, 2),
                'daily_usage': daily_usage,
                'training_status': {
                    'last_trained': training_data['generated_at'].isoformat() if training_data else None,
                    'insights_available': bool(training_data),
                    'common_concerns_count': len(training_data.get('common_customer_concerns', [])) if training_data else 0,
                    'faq_count': len(training_data.get('frequently_asked_questions', [])) if training_data else 0
                }
            },
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Get analytics error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch chatbot analytics'
        }), 500

@chatbot_bp.route('/chatbot/suggestions', methods=['GET'])
@jwt_required()
def get_chatbot_suggestions():
    """Get AI-powered business suggestions"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get business context
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get recent analytics
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Get recent customer feedback
        recent_feedback = list(mongo.db.customer_feedback.find({
            'business_owner_id': ObjectId(current_user_id),
            'created_at': {'$gte': start_date}
        }).limit(10))
        
        # Get recent messages
        recent_messages = mongo.db.messages.count_documents({
            'recipient_id': ObjectId(current_user_id),
            'created_at': {'$gte': start_date}
        })
        
        # Get product count
        product_count = mongo.db.products.count_documents({
            'user_id': ObjectId(current_user_id),
            'is_active': True
        })
        
        # Get QR scans
        qr_analytics = mongo.db.qr_analytics.find_one({'user_id': ObjectId(current_user_id)})
        qr_scans = qr_analytics.get('total_scans', 0) if qr_analytics else 0
        
        # Build context for AI suggestions
        context = {
            'business_name': user.get('business_name', 'Your Business'),
            'business_type': user.get('business_type', 'business'),
            'total_products': product_count,
            'recent_messages_count': recent_messages,
            'qr_scans': qr_scans,
            'suggestion_type': 'general_business_improvement',
            'recent_feedback_sentiment': 'mixed' if recent_feedback else 'none'
        }
        
        # Get AI service and generate suggestions
        from app.services.ai_service import AIService
        ai_service = AIService()
        suggestions = ai_service.generate_business_suggestions(context)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions.get('suggestions', []),
            'context': context,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"Get suggestions error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate suggestions'
        }), 500

@chatbot_bp.route('/chatbot/quick-help', methods=['POST'])
@jwt_required()
def quick_help():
    """Get quick help for common business topics"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        topic = data.get('topic', '').lower()
        
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic is required'
            }), 400
        
        # Get user context
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        business_name = user.get('business_name', 'your business') if user else 'your business'
        business_type = user.get('business_type', 'business') if user else 'business'
        
        # Topic-specific help responses
        help_responses = {
            'marketing': f"Here are some marketing strategies for {business_name}:\n\n1. **Social Media Presence**: Post regularly about your {business_type} services and engage with customers\n2. **Customer Reviews**: Encourage satisfied customers to leave reviews\n3. **QR Code Promotion**: Place your QR code in high-visibility areas\n4. **Email Marketing**: Collect customer emails through your website forms\n5. **Local SEO**: Optimize your business for local searches\n\nWould you like specific advice on any of these areas?",
            
            'customers': f"Customer management tips for {business_name}:\n\n1. **Response Time**: Reply to customer messages within 24 hours\n2. **Feedback Collection**: Use your website forms to gather customer feedback\n3. **Customer Database**: Maintain detailed records of customer interactions\n4. **Loyalty Programs**: Consider rewards for repeat customers\n5. **Personal Touch**: Address customers by name in communications\n\nNeed help with a specific customer situation?",
            
            'products': f"Product optimization for {business_name}:\n\n1. **Product Descriptions**: Write clear, benefit-focused descriptions\n2. **Pricing Strategy**: Research competitor pricing regularly\n3. **Inventory Management**: Track stock levels and popular items\n4. **Product Photos**: Use high-quality images in your listings\n5. **Customer Feedback**: Use reviews to improve product offerings\n\nWhat specific product challenge can I help with?",
            
            'analytics': f"Understanding your {business_name} analytics:\n\n1. **QR Code Scans**: Track which locations generate most scans\n2. **Website Visits**: Monitor traffic patterns and popular pages\n3. **Customer Messages**: Analyze inquiry types and response times\n4. **Feedback Trends**: Review sentiment patterns over time\n5. **Growth Metrics**: Compare monthly performance indicators\n\nWhich analytics would you like to explore?",
            
            'website': f"Optimizing your {business_name} website:\n\n1. **Content Updates**: Keep business information current\n2. **Contact Forms**: Ensure forms are working and user-friendly\n3. **Mobile Optimization**: Test website on mobile devices\n4. **Loading Speed**: Optimize images and content for fast loading\n5. **Call-to-Actions**: Make it easy for customers to contact you\n\nWhat aspect of your website needs attention?",
            
            'finance': f"Financial management for {business_name}:\n\n1. **Break-even Analysis**: Calculate your break-even point regularly\n2. **Cash Flow**: Monitor daily/weekly cash flow patterns\n3. **Expense Tracking**: Categorize and track all business expenses\n4. **Pricing Review**: Ensure prices cover costs and desired profit\n5. **Growth Investment**: Allocate budget for marketing and improvements\n\nWhat financial area would you like guidance on?"
        }
        
        # Get response or provide general help
        response = help_responses.get(topic, f"I can help you with {business_name} in several areas:\n\n• **Marketing** - Social media, advertising, customer acquisition\n• **Customers** - Service, feedback, relationship management\n• **Products** - Optimization, pricing, inventory\n• **Analytics** - Understanding your business data\n• **Website** - Optimization and maintenance\n• **Finance** - Budgeting and profitability\n\nWhat specific area would you like help with?")
        
        return jsonify({
            'success': True,
            'topic': topic,
            'response': response,
            'business_context': {
                'business_name': business_name,
                'business_type': business_type
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Quick help error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get help information'
        }), 500

# WebSocket support for real-time chat (if using Flask-SocketIO)
try:
    from flask_socketio import emit, join_room, leave_room
    from app import socketio
    
    @socketio.on('join_chat')
    def on_join_chat(data):
        """Join chat room for real-time messaging"""
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        
        if user_id and conversation_id:
            room = f"chat_{user_id}_{conversation_id}"
            join_room(room)
            emit('chat_joined', {'room': room})
    
    @socketio.on('leave_chat')
    def on_leave_chat(data):
        """Leave chat room"""
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        
        if user_id and conversation_id:
            room = f"chat_{user_id}_{conversation_id}"
            leave_room(room)
            emit('chat_left', {'room': room})
    
    @socketio.on('typing')
    def on_typing(data):
        """Handle typing indicators"""
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        is_typing = data.get('is_typing', False)
        
        if user_id and conversation_id:
            room = f"chat_{user_id}_{conversation_id}"
            emit('user_typing', {'is_typing': is_typing}, room=room, include_self=False)

except ImportError:
    # Flask-SocketIO not available
    pass
