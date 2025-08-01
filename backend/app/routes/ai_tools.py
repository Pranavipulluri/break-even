#### app/routes/ai_tools.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.services.ai_service import AIService
from app.services.gemini_service import get_gemini_service
from app.services.github_service import get_github_service
from app.services.netlify_service import get_netlify_service
from bson import ObjectId
from datetime import datetime
import base64
import io

ai_bp = Blueprint('ai_tools', __name__)

# Development endpoints (no auth required)
@ai_bp.route('/ai-tools/dev/test', methods=['GET'])
def dev_test():
    """Development test endpoint"""
    return jsonify({
        'message': 'AI tools development test successful',
        'services': ['gemini', 'github', 'netlify'],
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@ai_bp.route('/ai-tools/dev/gemini-test', methods=['POST'])
def dev_gemini_test():
    """Test Gemini AI without authentication"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'Say hello and confirm you are working!')
        
        result = get_gemini_service().generate_content(prompt)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@ai_bp.route('/ai-tools/dev/netlify-deploy', methods=['POST'])
def dev_netlify_deploy():
    """Test Netlify deployment without authentication"""
    try:
        data = request.get_json()
        site_name = data.get('site_name', 'Test Site')
        business_info = data.get('business_info', {
            'hero_title': 'Test Website',
            'hero_subtitle': 'Testing deployment',
            'about_us': 'This is a test.',
            'contact_cta': 'Contact us!'
        })
        
        result = get_netlify_service().create_and_deploy_website(site_name, business_info)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@ai_bp.route('/ai-tools/dev/github-deploy', methods=['POST'])
def dev_github_deploy():
    """Test GitHub deployment without authentication"""
    try:
        data = request.get_json()
        site_name = data.get('site_name', 'Test Site')
        business_info = data.get('business_info', {
            'hero_title': 'Test Website',
            'hero_subtitle': 'Testing deployment',
            'about_us': 'This is a test.',
            'contact_cta': 'Contact us!'
        })
        
        result = get_github_service().create_website_repository(site_name, business_info)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# Production endpoints (auth required)
@ai_bp.route('/ai-tools/gemini/generate-content', methods=['POST'])
@jwt_required()
def gemini_generate_content():
    """Generate content using Gemini AI"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        prompt = data.get('prompt')
        max_tokens = data.get('max_tokens', 1000)
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        result = get_gemini_service().generate_content(prompt, max_tokens)
        
        # Save generation to database
        generation_record = {
            'user_id': ObjectId(current_user_id),
            'service': 'gemini',
            'prompt': prompt,
            'result': result,
            'created_at': datetime.utcnow()
        }
        mongo.db.ai_generations.insert_one(generation_record)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/gemini/business-description', methods=['POST'])
@jwt_required()
def gemini_business_description():
    """Generate business description using Gemini AI"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        business_name = data.get('business_name')
        business_type = data.get('business_type')
        key_features = data.get('key_features')
        
        if not business_name or not business_type:
            return jsonify({'error': 'Business name and type are required'}), 400
        
        result = get_gemini_service().generate_business_description(
            business_name, business_type, key_features
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/gemini/website-content', methods=['POST'])
@jwt_required()
def gemini_website_content():
    """Generate website content using Gemini AI"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        business_info = data.get('business_info', {})
        
        if not business_info.get('name'):
            return jsonify({'error': 'Business name is required'}), 400
        
        result = get_gemini_service().generate_website_content(business_info)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/gemini/social-media', methods=['POST'])
@jwt_required()
def gemini_social_media():
    """Generate social media content using Gemini AI"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        business_name = data.get('business_name')
        business_type = data.get('business_type')
        occasion = data.get('occasion')
        
        if not business_name or not business_type:
            return jsonify({'error': 'Business name and type are required'}), 400
        
        result = get_gemini_service().generate_social_media_content(
            business_name, business_type, occasion
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/github/create-website', methods=['POST'])
@jwt_required()
def github_create_website():
    """Create and deploy website using GitHub Pages"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        business_name = data.get('business_name')
        website_content = data.get('website_content', {})
        
        if not business_name:
            return jsonify({'error': 'Business name is required'}), 400
        
        result = get_github_service().create_website_repository(business_name, website_content)
        
        # Save deployment record
        if result['success']:
            deployment_record = {
                'user_id': ObjectId(current_user_id),
                'service': 'github',
                'business_name': business_name,
                'repository': result['repository'],
                'website_url': result['website_url'],
                'created_at': datetime.utcnow()
            }
            mongo.db.deployments.insert_one(deployment_record)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/netlify/deploy-website', methods=['POST'])
@jwt_required()
def netlify_deploy_website():
    """Deploy website using Netlify"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        business_name = data.get('business_name')
        website_content = data.get('website_content', {})
        
        if not business_name:
            return jsonify({'error': 'Business name is required'}), 400
        
        result = get_netlify_service().create_and_deploy_website(business_name, website_content)
        
        # Save deployment record
        if result['success']:
            deployment_record = {
                'user_id': ObjectId(current_user_id),
                'service': 'netlify',
                'business_name': business_name,
                'site_info': result['site'],
                'website_url': result['website_url'],
                'created_at': datetime.utcnow()
            }
            mongo.db.deployments.insert_one(deployment_record)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/deployments', methods=['GET'])
@jwt_required()
def get_user_deployments():
    """Get user's deployment history"""
    try:
        current_user_id = get_jwt_identity()
        
        deployments = list(mongo.db.deployments.find(
            {'user_id': ObjectId(current_user_id)},
            {'_id': 0}
        ).sort('created_at', -1).limit(10))
        
        return jsonify({
            'success': True,
            'deployments': deployments
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/generate-content', methods=['POST'])
@jwt_required()
def generate_content():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        content_type = data.get('content_type')  # 'product_description', 'marketing_copy', 'social_media'
        prompt = data.get('prompt')
        business_context = data.get('business_context', '')
        
        if not content_type or not prompt:
            return jsonify({'error': 'Content type and prompt are required'}), 400
        
        # Get user's business info for context
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        if user:
            business_context += f" Business: {user.get('business_name', '')}. "
        
        ai_service = AIService()
        generated_content = ai_service.generate_content(content_type, prompt, business_context)
        
        # Save generation history
        mongo.db.ai_generations.insert_one({
            'user_id': ObjectId(current_user_id),
            'content_type': content_type,
            'prompt': prompt,
            'generated_content': generated_content,
            'created_at': datetime.utcnow()
        })
        
        return jsonify({
            'content': generated_content,
            'type': content_type
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/generate-image', methods=['POST'])
@jwt_required()
def generate_image():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        prompt = data.get('prompt')
        image_type = data.get('image_type', 'poster')  # 'poster', 'logo', 'product_image'
        style = data.get('style', 'modern')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        ai_service = AIService()
        
        # Enhance prompt based on business context
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        business_context = ""
        if user:
            business_context = f"for {user.get('business_name', '')} business"
        
        enhanced_prompt = f"{prompt} {business_context}, {style} style, high quality, professional"
        
        # Generate image
        image_data = ai_service.generate_image(enhanced_prompt, image_type)
        
        if image_data:
            # Save generation record
            mongo.db.ai_image_generations.insert_one({
                'user_id': ObjectId(current_user_id),
                'prompt': prompt,
                'enhanced_prompt': enhanced_prompt,
                'image_type': image_type,
                'style': style,
                'image_data': image_data,
                'created_at': datetime.utcnow()
            })
            
            return jsonify({
                'image_data': image_data,
                'prompt': prompt,
                'type': image_type
            }), 200
        else:
            return jsonify({'error': 'Failed to generate image'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/business-suggestions', methods=['POST'])
@jwt_required()
def get_business_suggestions():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        suggestion_type = data.get('type', 'general')  # 'marketing', 'products', 'website', 'general'
        
        # Get user's business data
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        website = mongo.db.child_websites.find_one({'owner_id': ObjectId(current_user_id)})
        
        # Get recent analytics
        recent_messages = list(mongo.db.messages.find({
            'recipient_id': ObjectId(current_user_id)
        }).sort('created_at', -1).limit(10))
        
        products = list(mongo.db.products.find({
            'user_id': ObjectId(current_user_id),
            'is_active': True
        }).limit(10))
        
        qr_analytics = mongo.db.qr_analytics.find_one({
            'user_id': ObjectId(current_user_id)
        })
        
        # Prepare context for AI
        context = {
            'business_name': user.get('business_name', '') if user else '',
            'business_type': website.get('business_type', '') if website else '',
            'total_products': len(products),
            'recent_messages_count': len(recent_messages),
            'qr_scans': qr_analytics.get('total_scans', 0) if qr_analytics else 0,
            'suggestion_type': suggestion_type
        }
        
        ai_service = AIService()
        suggestions = ai_service.generate_business_suggestions(context)
        
        # Save suggestions
        mongo.db.ai_suggestions.insert_one({
            'user_id': ObjectId(current_user_id),
            'suggestion_type': suggestion_type,
            'suggestions': suggestions,
            'context': context,
            'created_at': datetime.utcnow()
        })
        
        return jsonify({
            'suggestions': suggestions,
            'type': suggestion_type
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/analyze-feedback', methods=['POST'])
@jwt_required()
def analyze_feedback():
    try:
        current_user_id = get_jwt_identity()
        
        # Get all messages and feedback
        messages = list(mongo.db.messages.find({
            'recipient_id': ObjectId(current_user_id)
        }))
        
        feedback_entries = list(mongo.db.customer_feedback.find({
            'business_owner_id': ObjectId(current_user_id)
        }))
        
        if not messages and not feedback_entries:
            return jsonify({
                'analysis': 'No feedback data available for analysis.',
                'insights': [],
                'recommendations': []
            }), 200
        
        # Prepare feedback text for analysis
        feedback_texts = []
        for message in messages:
            if message.get('content'):
                feedback_texts.append(message['content'])
        
        for feedback in feedback_entries:
            if feedback.get('feedback_text'):
                feedback_texts.append(feedback['feedback_text'])
        
        ai_service = AIService()
        analysis = ai_service.analyze_customer_feedback(feedback_texts)
        
        # Save analysis
        mongo.db.feedback_analysis.insert_one({
            'user_id': ObjectId(current_user_id),
            'analysis': analysis,
            'total_feedback_items': len(feedback_texts),
            'created_at': datetime.utcnow()
        })
        
        return jsonify(analysis), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/generation-history', methods=['GET'])
@jwt_required()
def get_generation_history():
    try:
        current_user_id = get_jwt_identity()
        history_type = request.args.get('type', 'all')  # 'content', 'image', 'suggestions', 'all'
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        skip = (page - 1) * per_page
        
        history = []
        
        if history_type in ['content', 'all']:
            content_history = list(mongo.db.ai_generations.find({
                'user_id': ObjectId(current_user_id)
            }).sort('created_at', -1).skip(skip).limit(per_page))
            
            for item in content_history:
                history.append({
                    'id': str(item['_id']),
                    'type': 'content',
                    'content_type': item['content_type'],
                    'prompt': item['prompt'],
                    'result': item['generated_content'],
                    'created_at': item['created_at']
                })
        
        if history_type in ['image', 'all']:
            image_history = list(mongo.db.ai_image_generations.find({
                'user_id': ObjectId(current_user_id)
            }).sort('created_at', -1).skip(skip).limit(per_page))
            
            for item in image_history:
                history.append({
                    'id': str(item['_id']),
                    'type': 'image',
                    'image_type': item['image_type'],
                    'prompt': item['prompt'],
                    'style': item['style'],
                    'image_data': item['image_data'],
                    'created_at': item['created_at']
                })
        
        if history_type in ['suggestions', 'all']:
            suggestions_history = list(mongo.db.ai_suggestions.find({
                'user_id': ObjectId(current_user_id)
            }).sort('created_at', -1).skip(skip).limit(per_page))
            
            for item in suggestions_history:
                history.append({
                    'id': str(item['_id']),
                    'type': 'suggestions',
                    'suggestion_type': item['suggestion_type'],
                    'suggestions': item['suggestions'],
                    'created_at': item['created_at']
                })
        
        # Sort by created_at
        history.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'history': history[:per_page],
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/chatbot', methods=['POST'])
@jwt_required()
def chatbot():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        message = data.get('message')
        conversation_id = data.get('conversation_id')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get user context
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        website = mongo.db.child_websites.find_one({'owner_id': ObjectId(current_user_id)})
        
        # Get conversation history if exists
        conversation_history = []
        if conversation_id:
            chat_history = mongo.db.chatbot_conversations.find_one({
                '_id': ObjectId(conversation_id),
                'user_id': ObjectId(current_user_id)
            })
            if chat_history:
                conversation_history = chat_history.get('messages', [])
        
        ai_service = AIService()
        response = ai_service.chatbot_response(
            message, 
            user_context={
                'business_name': user.get('business_name', '') if user else '',
                'business_type': website.get('business_type', '') if website else ''
            },
            conversation_history=conversation_history
        )
        
        # Save conversation
        new_message = {
            'user_message': message,
            'bot_response': response,
            'timestamp': datetime.utcnow()
        }
        
        if conversation_id:
            # Update existing conversation
            mongo.db.chatbot_conversations.update_one(
                {'_id': ObjectId(conversation_id)},
                {'$push': {'messages': new_message}, '$set': {'updated_at': datetime.utcnow()}}
            )
        else:
            # Create new conversation
            result = mongo.db.chatbot_conversations.insert_one({
                'user_id': ObjectId(current_user_id),
                'messages': [new_message],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
            conversation_id = str(result.inserted_id)
        
        return jsonify({
            'response': response,
            'conversation_id': conversation_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#### app/routes/customers.py



#### app/services/ai_service.py

