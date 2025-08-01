
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import mongo
from app.models.user import User
from app.utils.validators import validate_email, validate_password
from bson import ObjectId
from datetime import datetime

auth_bp = Blueprint('auth', _name_)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate input
        if not validate_email(data.get('email')):
            return jsonify({'error': 'Invalid email format'}), 400
            
        if not validate_password(data.get('password')):
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Check if user already exists
        if mongo.db.users.find_one({'email': data['email']}):
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            password=data['password'],
            name=data['name'],
            business_name=data.get('business_name'),
            phone=data.get('phone')
        )
        # Insert user into database
        result = mongo.db.users.insert_one({
            **user.to_dict(),
            'password_hash': user.password_hash
        })
        
        # Create access token
        access_token = create_access_token(identity=str(result.inserted_id))
        
        return jsonify({
            'message': 'User registered successfully',
            'token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user in database
        user_data = mongo.db.users.find_one({'email': email})
        if not user_data:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create user object and check password
        user = User.from_dict(user_data)
        if not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
         # Create access token
        access_token = create_access_token(identity=str(user_data['_id']))
        
        return jsonify({
            'message': 'Login successful',
            'token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    try:
        current_user_id = get_jwt_identity()
        user_data = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        user = User.from_dict(user_data)
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

