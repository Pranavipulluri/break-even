
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import mongo
from app.models.user import User
from app.utils.validators import validate_email, validate_password
from bson import ObjectId
from datetime import datetime
import requests
import random
import string

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate input data exists
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check required fields
        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
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
        user_data = user.to_dict()
        user_data['password_hash'] = user.password_hash
        
        result = mongo.db.users.insert_one(user_data)
        user_id = str(result.inserted_id)
        
        # Create access token
        access_token = create_access_token(identity=user_id)
        
        response_user = user.to_dict()
        response_user['_id'] = user_id
        
        return jsonify({
            'message': 'User registered successfully',
            'token': access_token,
            'user': response_user
        }), 201
        
    except Exception as e:
        print(f"Registration error: {str(e)}")  # Log the error
        return jsonify({'error': 'Internal server error during registration'}), 500
        
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
        user_id = str(user_data['_id'])
        access_token = create_access_token(identity=user_id)
        
        response_user = user.to_dict()
        response_user['_id'] = user_id
        
        return jsonify({
            'message': 'Login successful',
            'token': access_token,
            'user': response_user
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
        response_user = user.to_dict()
        response_user['_id'] = current_user_id
        return jsonify({'user': response_user}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/google', methods=['POST'])
def google_auth():
    try:
        data = request.get_json()
        id_token = data.get('id_token')
        if not id_token:
            return jsonify({'error': 'ID token is required'}), 400

        # Check for development mock token
        if id_token.startswith("mock_google_"):
            parts = id_token.split("_")
            if len(parts) >= 4:
                name = parts[2]
                email = parts[3]
            else:
                name = "Mock Google User"
                email = "mock.google@example.com"
            token_info = {"email": email, "name": name}
        else:
            # Call Google Tokeninfo API to verify the ID token
            tokeninfo_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
            response = requests.get(tokeninfo_url, timeout=10)
            
            if response.status_code != 200:
                return jsonify({'error': 'Invalid Google token'}), 401
                
            token_info = response.json()
            
        email = token_info.get('email')
        name = token_info.get('name', 'Google User')
        
        if not email:
            return jsonify({'error': 'Email not provided by Google account'}), 400

        # Check if user already exists
        user_data = mongo.db.users.find_one({'email': email})
        
        if not user_data:
            # Create user dynamically without password
            random_pw = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            user = User(
                email=email,
                password=random_pw,
                name=name
            )
            user_dict = user.to_dict()
            user_dict['password_hash'] = user.password_hash
            user_dict['oauth_provider'] = 'google'
            
            result = mongo.db.users.insert_one(user_dict)
            user_id = str(result.inserted_id)
            registered_user = user.to_dict()
            registered_user['_id'] = user_id
        else:
            user_id = str(user_data['_id'])
            registered_user = User.from_dict(user_data).to_dict()
            registered_user['_id'] = user_id
            
        # Create access token
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            'message': 'Google authentication successful',
            'token': access_token,
            'user': registered_user
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/microsoft', methods=['POST'])
def microsoft_auth():
    try:
        data = request.get_json()
        access_token = data.get('access_token')
        if not access_token:
            return jsonify({'error': 'Access token is required'}), 400

        # Check for development mock token
        if access_token.startswith("mock_ms_"):
            parts = access_token.split("_")
            if len(parts) >= 4:
                name = parts[2]
                email = parts[3]
            else:
                name = "Mock Microsoft User"
                email = "mock.ms@example.com"
            user_info = {"displayName": name, "mail": email}
        else:
            # Call Microsoft Graph API to get user details
            graph_url = "https://graph.microsoft.com/v1.0/me"
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(graph_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return jsonify({'error': 'Invalid Microsoft token'}), 401
                
            user_info = response.json()
            
        email = user_info.get('mail') or user_info.get('userPrincipalName')
        name = user_info.get('displayName', 'Microsoft User')
        
        if not email:
            return jsonify({'error': 'Email not provided by Microsoft account'}), 400

        # Check if user already exists
        user_data = mongo.db.users.find_one({'email': email})
        
        if not user_data:
            random_pw = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            user = User(
                email=email,
                password=random_pw,
                name=name
            )
            user_dict = user.to_dict()
            user_dict['password_hash'] = user.password_hash
            user_dict['oauth_provider'] = 'microsoft'
            
            result = mongo.db.users.insert_one(user_dict)
            user_id = str(result.inserted_id)
            registered_user = user.to_dict()
            registered_user['_id'] = user_id
        else:
            user_id = str(user_data['_id'])
            registered_user = User.from_dict(user_data).to_dict()
            registered_user['_id'] = user_id
            
        # Create access token
        access_token_jwt = create_access_token(identity=user_id)
        
        return jsonify({
            'message': 'Microsoft authentication successful',
            'token': access_token_jwt,
            'user': registered_user
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

