from flask import Blueprint, request, jsonify
from app import mongo
from bson import ObjectId
from datetime import datetime

public_api_bp = Blueprint('public_api', __name__)

@public_api_bp.route('/public/products/<business_id>', methods=['GET'])
def get_public_products(business_id):
    """
    Public endpoint to fetch products for mini-websites
    No authentication required - for display on child websites
    """
    try:
        # Convert business_id to ObjectId
        user_id = ObjectId(business_id)
        
        # Get products for this business
        products = list(mongo.db.products.find({
            'user_id': user_id,
            'is_active': True
        }).sort('created_at', -1).limit(20))  # Limit to 20 products
        
        # Convert ObjectId to string for JSON serialization
        for product in products:
            product['_id'] = str(product['_id'])
            product['user_id'] = str(product['user_id'])
            
            # Remove sensitive information
            if 'cost' in product:
                del product['cost']
        
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching products: {str(e)}',
            'products': []
        }), 500

@public_api_bp.route('/public/business/<business_id>', methods=['GET'])
def get_public_business_info(business_id):
    """
    Public endpoint to fetch business information for mini-websites
    """
    try:
        # Convert business_id to ObjectId
        user_id = ObjectId(business_id)
        
        # Get user/business information
        user = mongo.db.users.find_one({'_id': user_id})
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Business not found'
            }), 404
        
        # Return public business information
        business_info = {
            'name': user.get('name', 'Our Business'),
            'email': user.get('email', ''),
            'phone': user.get('phone', ''),
            'address': user.get('address', ''),
            'description': user.get('business_description', 'Welcome to our business!'),
            'website': user.get('website', ''),
            'social_media': user.get('social_media', {})
        }
        
        return jsonify({
            'success': True,
            'business': business_info
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching business info: {str(e)}'
        }), 500

@public_api_bp.route('/public/track-visit', methods=['POST'])
def track_website_visit():
    """
    Track visits to mini-websites for analytics
    """
    try:
        data = request.get_json()
        
        visit_data = {
            'business_id': data.get('business_id'),
            'website_source': data.get('website_source'),
            'visitor_ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'timestamp': datetime.utcnow(),
            'page_url': data.get('page_url'),
            'referrer': data.get('referrer')
        }
        
        # Insert visit tracking
        mongo.db.website_visits.insert_one(visit_data)
        
        return jsonify({
            'success': True,
            'message': 'Visit tracked'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error tracking visit: {str(e)}'
        }), 500
