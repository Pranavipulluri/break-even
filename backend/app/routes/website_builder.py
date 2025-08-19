from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.services.website_service import WebsiteService
from app.models.child_website import ChildWebsite
from bson import ObjectId
from datetime import datetime


website_bp = Blueprint('website_builder', __name__)

@website_bp.route('/website-builder/health', methods=['GET'])
def health_check():
    """Simple health check endpoint that doesn't require authentication"""
    return jsonify({
        'status': 'healthy',
        'message': 'Website builder API is running',
        'timestamp': datetime.now().isoformat()
    }), 200

@website_bp.route('/website-builder/test-auth', methods=['GET'])
@jwt_required()
def test_auth():
    """Simple endpoint to test if authentication is working"""
    try:
        current_user_id = get_jwt_identity()
        return jsonify({
            'message': 'Authentication successful',
            'user_id': current_user_id
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@website_bp.route('/website-builder/dev-test', methods=['GET'])
def dev_test():
    """Development endpoint that doesn't require authentication"""
    return jsonify({
        'message': 'Development test successful',
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    }), 200

@website_bp.route('/website-builder/dev-create', methods=['POST'])
def dev_create_website():
    """Development endpoint to create website without authentication"""
    try:
        data = request.get_json()
        
        # Simulate website creation for development
        website_data = {
            'id': 'dev-' + str(int(datetime.now().timestamp())),
            'website_name': data.get('website_name', 'Test Website'),
            'business_type': data.get('business_type', 'Business'),
            'area': data.get('area', 'Local Area'),
            'theme': data.get('theme', 'modern'),
            'created_at': datetime.now().isoformat(),
            'status': 'created'
        }
        
        return jsonify({
            'message': 'Website created successfully (development mode)',
            'website': website_data,
            'success': True
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@website_bp.route('/website-builder/create', methods=['POST'])
@jwt_required()
def create_website():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['website_name', 'business_type', 'color_theme', 'contact_info', 'area']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already has a website
        existing_website = mongo.db.child_websites.find_one({
            'owner_id': ObjectId(current_user_id)
        })
        
        if existing_website:
            return jsonify({'error': 'You already have a website. Please update your existing website.'}), 400
        
        # Create website
        website = ChildWebsite(
            owner_id=current_user_id,
            website_name=data['website_name'],
            business_type=data['business_type'],
            color_theme=data['color_theme'],
            contact_info=data['contact_info'],
            area=data['area'],
            description=data.get('description', ''),
            logo_url=data.get('logo_url'),
            custom_css=data.get('custom_css'),
            custom_domain=data.get('custom_domain')
        )
        
        # Generate website content using AI
        website_service = WebsiteService()
        generated_content = website_service.generate_website_content(
            business_type=data['business_type'],
            business_name=data['website_name'],
            description=data.get('description', ''),
            area=data['area']
        )
        
        # Update website with generated content
        website.generated_content = generated_content
        
        # Insert into database
        result = mongo.db.child_websites.insert_one({
            **website.to_dict(),
            'owner_id': ObjectId(current_user_id)
        })
        
        # Generate website URL
        website_url = f"{current_app.config['WEBSITE_BASE_URL']}/{current_user_id}"
        
        # Update user with website URL
        mongo.db.users.update_one(
            {'_id': ObjectId(current_user_id)},
            {'$set': {'website_url': website_url, 'has_website': True}}
        )
        
        # Create QR analytics entry
        mongo.db.qr_analytics.update_one(
            {'user_id': ObjectId(current_user_id)},
            {
                '$set': {
                    'user_id': ObjectId(current_user_id),
                    'website_url': website_url,
                    'total_scans': 0,
                    'scans_today': 0,
                    'created_at': datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return jsonify({
            'message': 'Website created successfully',
            'website_id': str(result.inserted_id),
            'website_url': website_url,
            'generated_content': generated_content
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@website_bp.route('/website-builder/update', methods=['PUT'])
@jwt_required()
def update_website():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Find existing website
        website = mongo.db.child_websites.find_one({
            'owner_id': ObjectId(current_user_id)
        })
        
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        # Update website data
        update_data = {
            'updated_at': datetime.utcnow()
        }
        
        # Update allowed fields
        allowed_fields = [
            'website_name', 'business_type', 'color_theme', 'contact_info',
            'area', 'description', 'logo_url', 'custom_css', 'custom_domain'
        ]
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        # If business type or description changed, regenerate content
        if 'business_type' in data or 'description' in data:
            website_service = WebsiteService()
            generated_content = website_service.generate_website_content(
                business_type=data.get('business_type', website['business_type']),
                business_name=data.get('website_name', website['website_name']),
                description=data.get('description', website.get('description', '')),
                area=data.get('area', website['area'])
            )
            update_data['generated_content'] = generated_content
        
        # Update in database
        mongo.db.child_websites.update_one(
            {'owner_id': ObjectId(current_user_id)},
            {'$set': update_data}
        )
        
        # Get updated website
        updated_website = mongo.db.child_websites.find_one({
            'owner_id': ObjectId(current_user_id)
        })
        updated_website['_id'] = str(updated_website['_id'])
        updated_website['owner_id'] = str(updated_website['owner_id'])
        
        return jsonify({
            'message': 'Website updated successfully',
            'website': updated_website
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@website_bp.route('/website-builder/my-website', methods=['GET'])
@jwt_required()
def get_my_website():
    try:
        current_user_id = get_jwt_identity()
        
        website = mongo.db.child_websites.find_one({
            'owner_id': ObjectId(current_user_id)
        })
        
        if not website:
            # Return empty result instead of 404 to avoid frontend errors
            return jsonify({
                'message': 'No website found for this user',
                'website': None,
                'analytics': {
                    'total_views': 0,
                    'total_clicks': 0,
                    'total_contacts': 0
                }
            }), 200
        
        website['_id'] = str(website['_id'])
        website['owner_id'] = str(website['owner_id'])
        
        # Get website analytics
        analytics = mongo.db.website_analytics.aggregate([
            {'$match': {'website_id': website['_id']}},
            {'$group': {
                '_id': None,
                'total_visits': {'$sum': 1},
                'unique_visitors': {'$addToSet': '$visitor_ip'},
                'last_visit': {'$max': '$visited_at'}
            }}
        ])
        
        analytics_data = list(analytics)
        if analytics_data:
            analytics_result = analytics_data[0]
            website['analytics'] = {
                'total_visits': analytics_result['total_visits'],
                'unique_visitors': len(analytics_result['unique_visitors']),
                'last_visit': analytics_result['last_visit']
            }
        else:
            website['analytics'] = {
                'total_visits': 0,
                'unique_visitors': 0,
                'last_visit': None
            }
        
        return jsonify({'website': website}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@website_bp.route('/website-builder/themes', methods=['GET'])
def get_themes():
    """Get available website themes"""
    themes = {
        'food_store': {
            'name': 'Food Store',
            'description': 'Perfect for restaurants, cafes, and food businesses',
            'color_schemes': ['warm', 'fresh', 'elegant'],
            'features': ['menu_display', 'order_form', 'gallery', 'reviews']
        },
        'fashion': {
            'name': 'Fashion & Clothing',
            'description': 'Ideal for clothing stores and fashion brands',
            'color_schemes': ['modern', 'classic', 'bold'],
            'features': ['product_gallery', 'size_guide', 'wishlist', 'collections']
        },
        'professional': {
            'name': 'Professional Services',
            'description': 'Great for consultants, lawyers, and service providers',
            'color_schemes': ['corporate', 'minimal', 'trust'],
            'features': ['service_list', 'appointment_booking', 'testimonials', 'contact_form']
        },
        'beauty': {
            'name': 'Beauty & Wellness',
            'description': 'Perfect for salons, spas, and beauty services',
            'color_schemes': ['elegant', 'soft', 'luxurious'],
            'features': ['service_booking', 'gallery', 'staff_profiles', 'packages']
        },
        'technology': {
            'name': 'Technology',
            'description': 'Suitable for tech companies and IT services',
            'color_schemes': ['tech', 'modern', 'futuristic'],
            'features': ['portfolio', 'case_studies', 'tech_specs', 'contact']
        },
        'general': {
            'name': 'General Business',
            'description': 'Versatile theme for any type of business',
            'color_schemes': ['neutral', 'business', 'friendly'],
            'features': ['about_us', 'services', 'contact', 'gallery']
        }
    }
    
    color_schemes = {
        'warm': {'primary': '#FF6B35', 'secondary': '#F7931E', 'background': '#FFF8F0'},
        'fresh': {'primary': '#4CAF50', 'secondary': '#8BC34A', 'background': '#F1F8E9'},
        'elegant': {'primary': '#6A0DAD', 'secondary': '#9932CC', 'background': '#FAF0FF'},
        'modern': {'primary': '#2196F3', 'secondary': '#03DAC6', 'background': '#F0F8FF'},
        'classic': {'primary': '#212121', 'secondary': '#757575', 'background': '#FAFAFA'},
        'bold': {'primary': '#E91E63', 'secondary': '#FF5722', 'background': '#FFF5F5'},
        'corporate': {'primary': '#1565C0', 'secondary': '#42A5F5', 'background': '#E3F2FD'},
        'minimal': {'primary': '#37474F', 'secondary': '#78909C', 'background': '#FAFAFA'},
        'trust': {'primary': '#2E7D32', 'secondary': '#66BB6A', 'background': '#E8F5E8'},
        'soft': {'primary': '#F8BBD9', 'secondary': '#F48FB1', 'background': '#FCE4EC'},
        'luxurious': {'primary': '#4A148C', 'secondary': '#7B1FA2', 'background': '#F3E5F5'},
        'tech': {'primary': '#0D47A1', 'secondary': '#1976D2', 'background': '#E1F5FE'},
        'futuristic': {'primary': '#00BCD4', 'secondary': '#00E676', 'background': '#E0F8FF'},
        'neutral': {'primary': '#5E4037', 'secondary': '#8D6E63', 'background': '#EFEBE9'},
        'business': {'primary': '#1A237E', 'secondary': '#3F51B5', 'background': '#E8EAF6'},
        'friendly': {'primary': '#FF9800', 'secondary': '#FFC107', 'background': '#FFF8E1'}
    }
    
    return jsonify({
        'themes': themes,
        'colorSchemes': color_schemes
    }), 200

@website_bp.route('/website/<website_id>/visit', methods=['POST'])
def track_website_visit(website_id):
    """Track website visits from child websites"""
    try:
        data = request.get_json()
        visitor_ip = request.remote_addr
        
        # Get website info
        website = mongo.db.child_websites.find_one({'_id': ObjectId(website_id)})
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        # Track visit
        visit_data = {
            'website_id': website_id,
            'business_owner_id': website['owner_id'],
            'visitor_ip': visitor_ip,
            'user_agent': request.headers.get('User-Agent'),
            'visited_at': datetime.utcnow(),
            'page': data.get('page', '/'),
            'referrer': data.get('referrer')
        }
        
        mongo.db.website_analytics.insert_one(visit_data)
        
        return jsonify({'message': 'Visit tracked successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@website_bp.route('/website-builder/create-enhanced', methods=['POST'])
@jwt_required()
def create_enhanced_website():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['website_name', 'business_type', 'color_theme', 'contact_info', 'area']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already has a website
        existing_website = mongo.db.child_websites.find_one({
            'owner_id': ObjectId(current_user_id)
        })
        
        if existing_website:
            return jsonify({'error': 'You already have a website. Please update your existing website.'}), 400
        
        # Get user context for personalization
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        user_context = {
            'user_experience': 'new' if not user.get('has_website') else 'experienced',
            'previous_businesses': user.get('business_history', []),
            'preferences': user.get('preferences', {}),
            'location': data['area']
        }
        
        # Generate enhanced content using Gemini
        gemini_service = GeminiWebsiteService()
        generated_content = gemini_service.generate_enhanced_website_content(data, user_context)
        
        # Create website with enhanced content
        website = ChildWebsite(
            owner_id=current_user_id,
            website_name=data['website_name'],
            business_type=data['business_type'],
            color_theme=data['color_theme'],
            contact_info=data['contact_info'],
            area=data['area'],
            description=data.get('description', ''),
            logo_url=data.get('logo_url'),
            custom_css=data.get('custom_css'),
            custom_domain=data.get('custom_domain')
        )
        
        # Add enhanced content
        website.generated_content = generated_content
        website.generation_method = 'gemini_enhanced'
        website.user_context = user_context
        
        # Insert into database
        result = mongo.db.child_websites.insert_one({
            **website.to_dict(),
            'owner_id': ObjectId(current_user_id)
        })
        
        # Generate website URL
        website_url = f"{current_app.config['WEBSITE_BASE_URL']}/{current_user_id}"
        
        # Update user with website URL
        mongo.db.users.update_one(
            {'_id': ObjectId(current_user_id)},
            {'$set': {'website_url': website_url, 'has_website': True}}
        )
        
        # Store in training data
        training_service = WebsiteTrainingService()
        mongo.db.website_training_data.insert_one({
            'website_id': result.inserted_id,
            'user_id': ObjectId(current_user_id),
            'business_type': data['business_type'],
            'area': data['area'],
            'business_name': data['website_name'],
            'input_data': data,
            'generated_content': generated_content,
            'user_context': user_context,
            'created_at': datetime.utcnow(),
            'performance_score': 0.0,
            'feedback_count': 0
        })
        
        return jsonify({
            'message': 'Enhanced website created successfully',
            'website_id': str(result.inserted_id),
            'website_url': website_url,
            'generated_content': generated_content,
            'personalization_applied': True
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@website_bp.route('/website-builder/feedback', methods=['POST'])
@jwt_required()
def submit_website_feedback():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        website = mongo.db.child_websites.find_one({
            'owner_id': ObjectId(current_user_id)
        })
        
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        # Collect feedback for training
        training_service = WebsiteTrainingService()
        training_service.collect_user_feedback(website['_id'], data)
        
        return jsonify({'message': 'Feedback collected successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@website_bp.route('/website-builder/recommendations/<business_type>')
@jwt_required()
def get_content_recommendations(business_type):
    try:
        current_user_id = get_jwt_identity()
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        area = request.args.get('area', user.get('area', ''))
        
        training_service = WebsiteTrainingService()
        recommendations = training_service.get_content_recommendations(business_type, area)
        
        return jsonify({
            'recommendations': recommendations,
            'business_type': business_type,
            'area': area
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@website_bp.route('/website-builder/analytics/patterns')
@jwt_required()
def get_successful_patterns():
    try:
        business_type = request.args.get('business_type')
        
        training_service = WebsiteTrainingService()
        patterns = training_service.analyze_successful_patterns(business_type)
        
        return jsonify({
            'patterns': patterns,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500