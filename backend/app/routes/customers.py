
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.models.customer import ChildCustomer
from app.services.email_service import EmailService
from bson import ObjectId
from datetime import datetime

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customers/register', methods=['POST'])
def register_customer():
    """Register customer from child website"""
    try:
        data = request.get_json()
        
        required_fields = ['business_owner_id', 'name', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if customer already exists for this business
        existing_customer = mongo.db.child_customers.find_one({
            'business_owner_id': ObjectId(data['business_owner_id']),
            'email': data['email']
        })
        
        if existing_customer:
            # Update last interaction
            mongo.db.child_customers.update_one(
                {'_id': existing_customer['_id']},
                {'$set': {'last_interaction': datetime.utcnow()}}
            )
            
            existing_customer['_id'] = str(existing_customer['_id'])
            existing_customer['business_owner_id'] = str(existing_customer['business_owner_id'])
            
            return jsonify({
                'message': 'Customer already registered',
                'customer': existing_customer
            }), 200
        
        # Create new customer
        customer = ChildCustomer(
            business_owner_id=data['business_owner_id'],
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            location=data.get('location'),
            website_id=data.get('website_id'),
            registration_source=data.get('registration_source', 'website')
        )
        
        # Insert into database
        result = mongo.db.child_customers.insert_one(customer.to_dict())
        
        # Get business owner info for welcome email
        business_owner = mongo.db.users.find_one({
            '_id': ObjectId(data['business_owner_id'])
        })
        
        # Send welcome email
        if business_owner:
            try:
                email_service = EmailService()
                email_service.send_customer_welcome_email(
                    data['email'],
                    data['name'],
                    business_owner.get('business_name', 'Our Business'),
                    business_owner['name']
                )
            except Exception as email_error:
                print(f"Failed to send welcome email: {email_error}")
        
        # Get the created customer
        created_customer = mongo.db.child_customers.find_one({'_id': result.inserted_id})
        created_customer['_id'] = str(created_customer['_id'])
        created_customer['business_owner_id'] = str(created_customer['business_owner_id'])
        
        return jsonify({
            'message': 'Customer registered successfully',
            'customer': created_customer
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/customers', methods=['GET'])
@jwt_required()
def get_customers():
    try:
        current_user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        search = request.args.get('search', '')
        
        skip = (page - 1) * per_page
        
        # Build query
        query = {'business_owner_id': ObjectId(current_user_id)}
        if search:
            query['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'email': {'$regex': search, '$options': 'i'}}
            ]
        
        customers = list(mongo.db.child_customers.find(query)
                        .sort('created_at', -1)
                        .skip(skip)
                        .limit(per_page))
        
        total = mongo.db.child_customers.count_documents(query)
        
        # Convert ObjectId to string
        for customer in customers:
            customer['_id'] = str(customer['_id'])
            customer['business_owner_id'] = str(customer['business_owner_id'])
        
        return jsonify({
            'customers': customers,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/customers/<customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Check if customer belongs to current user
        customer = mongo.db.child_customers.find_one({
            '_id': ObjectId(customer_id),
            'business_owner_id': ObjectId(current_user_id)
        })
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Update customer
        update_data = {
            'updated_at': datetime.utcnow()
        }
        
        allowed_fields = ['name', 'phone', 'location', 'tags', 'notes', 'is_subscribed']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        mongo.db.child_customers.update_one(
            {'_id': ObjectId(customer_id)},
            {'$set': update_data}
        )
        
        # Get updated customer
        updated_customer = mongo.db.child_customers.find_one({'_id': ObjectId(customer_id)})
        updated_customer['_id'] = str(updated_customer['_id'])
        updated_customer['business_owner_id'] = str(updated_customer['business_owner_id'])
        
        return jsonify({
            'message': 'Customer updated successfully',
            'customer': updated_customer
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/customers/<customer_id>', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    try:
        current_user_id = get_jwt_identity()
        
        # Check if customer belongs to current user
        result = mongo.db.child_customers.delete_one({
            '_id': ObjectId(customer_id),
            'business_owner_id': ObjectId(current_user_id)
        })
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Customer not found'}), 404
        
        return jsonify({'message': 'Customer deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/customers/feedback', methods=['POST'])
def submit_feedback():
    """Submit customer feedback from child website"""
    try:
        data = request.get_json()
        
        required_fields = ['business_owner_id', 'customer_email', 'rating']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create feedback entry
        feedback_data = {
            'business_owner_id': ObjectId(data['business_owner_id']),
            'customer_email': data['customer_email'],
            'customer_name': data.get('customer_name', 'Anonymous'),
            'rating': int(data['rating']),
            'feedback_text': data.get('feedback_text', ''),
            'website_id': data.get('website_id'),
            'created_at': datetime.utcnow()
        }
        
        result = mongo.db.customer_feedback.insert_one(feedback_data)
        
        # Update customer's last interaction
        mongo.db.child_customers.update_one(
            {
                'business_owner_id': ObjectId(data['business_owner_id']),
                'email': data['customer_email']
            },
            {'$set': {'last_interaction': datetime.utcnow()}},
            upsert=False
        )
        
        return jsonify({
            'message': 'Feedback submitted successfully',
            'feedback_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/customers/feedback', methods=['GET'])
@jwt_required()
def get_feedback():
    try:
        current_user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        skip = (page - 1) * per_page
        
        feedback_entries = list(mongo.db.customer_feedback.find({
            'business_owner_id': ObjectId(current_user_id)
        }).sort('created_at', -1).skip(skip).limit(per_page))
        
        total = mongo.db.customer_feedback.count_documents({
            'business_owner_id': ObjectId(current_user_id)
        })
        
        # Convert ObjectId to string
        for feedback in feedback_entries:
            feedback['_id'] = str(feedback['_id'])
            feedback['business_owner_id'] = str(feedback['business_owner_id'])
        
        return jsonify({
            'feedback': feedback_entries,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/customers/send-bulk-email', methods=['POST'])
@jwt_required()
def send_bulk_email():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        subject = data.get('subject')
        content = data.get('content')
        target_customers = data.get('target_customers')  # List of customer IDs, or None for all
        
        if not subject or not content:
            return jsonify({'error': 'Subject and content are required'}), 400
        
        email_service = EmailService()
        result = email_service.send_bulk_email_to_customers(
            current_user_id,
            subject,
            content,
            target_customers
        )
        
        if result:
            return jsonify({
                'message': 'Bulk email sent successfully',
                'sent': result['sent'],
                'total': result['total'],
                'failed': result['failed']
            }), 200
        else:
            return jsonify({'error': 'Failed to send bulk email'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

