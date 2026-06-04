"""
AI Business Chatbot Routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime
from app.services.ai_business_chatbot import ai_business_chatbot
from app import mongo
from bson import ObjectId

ai_chatbot_bp = Blueprint('ai_chatbot', __name__)
logger = logging.getLogger(__name__)

@ai_chatbot_bp.route('/api/ai/business-chat', methods=['POST'])
@jwt_required()
def business_chat():
    """
    AI Business Chatbot endpoint
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        message = data['message']
        language = data.get('language', 'en')
        user_context = data.get('user_context', {})
        conversation_history = data.get('conversation_history', [])
        
        # Get user information for context
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        if user:
            user_context.update({
                'name': user.get('name', 'Business Owner'),
                'business_type': user.get('business_category', 'General Business'),
                'business_name': user.get('business_name', user.get('name', 'Business')),
                'business_id': str(user['_id']),
                'user_id': str(user['_id'])
            })
        
        # Get AI response
        response = ai_business_chatbot.get_business_response(
            message=message,
            language=language,
            user_context=user_context,
            conversation_history=conversation_history
        )
        
        # Log the interaction
        chat_log = {
            'user_id': ObjectId(current_user_id),
            'message': message,
            'response': response,
            'language': language,
            'timestamp': datetime.utcnow(),
            'type': 'business_chat'
        }
        
        try:
            mongo.db.ai_chat_logs.insert_one(chat_log)
        except Exception as e:
            logger.warning(f"Could not log chat interaction: {e}")
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in business chat: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'response': 'I apologize, but I encountered an error. Please try again.'
        }), 500

@ai_chatbot_bp.route('/api/ai/business-insights', methods=['GET'])
@jwt_required()
def get_business_insights():
    """
    Get AI-generated business insights for the user
    """
    try:
        current_user_id = get_jwt_identity()
        language = request.args.get('language', 'en')
        
        # Generate business insights
        insights = ai_business_chatbot.get_business_insights(
            user_id=current_user_id,
            language=language
        )
        
        return jsonify({
            'success': True,
            'insights': insights,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating business insights: {e}")
        return jsonify({
            'success': False,
            'error': 'Could not generate insights'
        }), 500

@ai_chatbot_bp.route('/api/ai/chat-history', methods=['GET'])
@jwt_required()
def get_chat_history():
    """
    Get user's recent chat history with AI business partner
    """
    try:
        current_user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 10))
        
        # Get recent chat logs
        chat_logs = list(mongo.db.ai_chat_logs.find({
            'user_id': ObjectId(current_user_id),
            'type': 'business_chat'
        }).sort('timestamp', -1).limit(limit))
        
        # Format for response
        history = []
        for log in chat_logs:
            history.append({
                'message': log.get('message', ''),
                'response': log.get('response', ''),
                'timestamp': log.get('timestamp', '').isoformat() if log.get('timestamp') else '',
                'language': log.get('language', 'en')
            })
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        return jsonify({
            'success': False,
            'error': 'Could not fetch chat history'
        }), 500