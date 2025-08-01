
from flask import Blueprint, request, jsonify, render_template_string
from app import mongo
from app.services.website_service import WebsiteService
from bson import ObjectId
from datetime import datetime

child_website_bp = Blueprint('child_website', __name__)

@child_website_bp.route('/site/<website_id>')
def serve_child_website(website_id):
    """Serve the generated child website"""
    try:
        # Get website data
        website = mongo.db.child_websites.find_one({'_id': ObjectId(website_id)})
        if not website:
            return "Website not found", 404
        
        if not website.get('is_active', True):
            return "Website is not active", 404
        
        # Get business owner's products
        products = list(mongo.db.products.find({
            'user_id': website['owner_id'],
            'is_active': True
        }))
        
        # Generate HTML
        website_service = WebsiteService()
        html_content = website_service.generate_website_html(
            website, 
            website.get('generated_content', {}),
            products
        )
        
        # Track visit
        visit_data = {
            'website_id': str(website['_id']),
            'business_owner_id': website['owner_id'],
            'visitor_ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'visited_at': datetime.utcnow(),
            'page': '/',
            'referrer': request.referrer
        }
        
        mongo.db.website_analytics.insert_one(visit_data)
        
        return html_content
        
    except Exception as e:
        return f"Error loading website: {str(e)}", 500

@child_website_bp.route('/site/<website_id>/api/contact', methods=['POST'])
def handle_contact_form(website_id):
    """Handle contact form submissions from child website"""
    try:
        data = request.get_json()
        
        # Get website data
        website = mongo.db.child_websites.find_one({'_id': ObjectId(website_id)})
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        # Create message
        message_data = {
            'recipient_id': website['owner_id'],
            'content': data.get('message', ''),
            'customer_name': data.get('name', ''),
            'customer_email': data.get('email', ''),
            'customer_phone': data.get('phone'),
            'website_id': website_id,
            'message_type': 'contact_form',
            'created_at': datetime.utcnow(),
            'is_read': False,
            'status': 'new'
        }
        
        result = mongo.db.messages.insert_one(message_data)
        
        # Register customer if not exists
        if data.get('email'):
            existing_customer = mongo.db.child_customers.find_one({
                'business_owner_id': website['owner_id'],
                'email': data['email']
            })
            
            if not existing_customer:
                customer_data = {
                    'business_owner_id': website['owner_id'],
                    'name': data.get('name', ''),
                    'email': data['email'],
                    'phone': data.get('phone'),
                    'website_id': website_id,
                    'registration_source': 'contact_form',
                    'created_at': datetime.utcnow(),
                    'last_interaction': datetime.utcnow(),
                    'is_subscribed': True
                }
                
                mongo.db.child_customers.insert_one(customer_data)
        
        return jsonify({'message': 'Message sent successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@child_website_bp.route('/site/<website_id>/api/newsletter', methods=['POST'])
def handle_newsletter_signup(website_id):
    """Handle newsletter signups from child website"""
    try:
        data = request.get_json()
        
        # Get website data
        website = mongo.db.child_websites.find_one({'_id': ObjectId(website_id)})
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        email = data.get('email')
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Check if customer already exists
        existing_customer = mongo.db.child_customers.find_one({
            'business_owner_id': website['owner_id'],
            'email': email
        })
        
        if existing_customer:
            # Update subscription status
            mongo.db.child_customers.update_one(
                {'_id': existing_customer['_id']},
                {
                    '$set': {
                        'is_subscribed': True,
                        'last_interaction': datetime.utcnow()
                    }
                }
            )
        else:
            # Create new customer
            customer_data = {
                'business_owner_id': website['owner_id'],
                'name': data.get('name', 'Newsletter Subscriber'),
                'email': email,
                'website_id': website_id,
                'registration_source': 'newsletter',
                'created_at': datetime.utcnow(),
                'last_interaction': datetime.utcnow(),
                'is_subscribed': True
            }
            
            mongo.db.child_customers.insert_one(customer_data)
        
        return jsonify({'message': 'Successfully subscribed to newsletter'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@child_website_bp.route('/site/<website_id>/api/feedback', methods=['POST'])
def handle_feedback_submission(website_id):
    """Handle feedback submissions from child website"""
    try:
        data = request.get_json()
        
        # Get website data
        website = mongo.db.child_websites.find_one({'_id': ObjectId(website_id)})
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        # Create feedback entry
        feedback_data = {
            'business_owner_id': website['owner_id'],  
            'customer_email': data.get('email', ''),
            'customer_name': data.get('name', 'Anonymous'),
            'rating': int(data.get('rating', 5)),
            'feedback_text': data.get('feedback', ''),
            'website_id': website_id,
            'created_at': datetime.utcnow()
        }
        
        mongo.db.customer_feedback.insert_one(feedback_data)
        
        return jsonify({'message': 'Feedback submitted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@child_website_bp.route('/site/<website_id>/products')
def get_website_products(website_id):
    """Get products for child website"""
    try:
        # Get website data
        website = mongo.db.child_websites.find_one({'_id': ObjectId(website_id)})
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        # Get products
        products = list(mongo.db.products.find({
            'user_id': website['owner_id'],
            'is_active': True
        }))
        
        # Convert ObjectId to string
        for product in products:
            product['_id'] = str(product['_id'])
            product['user_id'] = str(product['user_id'])
        
        return jsonify({'products': products}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@child_website_bp.route('/site/<website_id>/track-interaction', methods=['POST'])
def track_product_interaction(website_id):
    """Track product interactions on child website"""
    try:
        data = request.get_json()
        
        # Get website data
        website = mongo.db.child_websites.find_one({'_id': ObjectId(website_id)})
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        # Track interaction
        interaction_data = {
            'business_owner_id': website['owner_id'],
            'website_id': website_id,
            'product_id': ObjectId(data.get('product_id')) if data.get('product_id') else None,
            'interaction_type': data.get('type', 'view'),  # view, inquiry, click
            'visitor_ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'created_at': datetime.utcnow()
        }
        
        mongo.db.product_interactions.insert_one(interaction_data)
        
        return jsonify({'message': 'Interaction tracked'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
