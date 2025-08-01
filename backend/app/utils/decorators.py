from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app import mongo
from bson import ObjectId

def require_json(f):
    """Decorator to require JSON content type"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        return f(*args, **kwargs)
    return decorated_function

def validate_business_owner(f):
    """Decorator to validate that current user owns the business/website"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        # Get business_owner_id from request data or URL params
        business_owner_id = None
        
        if request.method in ['POST', 'PUT', 'PATCH']:
            data = request.get_json()
            business_owner_id = data.get('business_owner_id')
        elif 'business_id' in kwargs:
            business_owner_id = kwargs['business_id']
        
        if business_owner_id and str(business_owner_id) != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests=100, per_minutes=60):
    """Simple rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This is a simple implementation
            # In production, use Redis or similar for distributed rate limiting
            client_ip = request.remote_addr
            current_user_id = None
            
            try:
                verify_jwt_in_request(optional=True)
                current_user_id = get_jwt_identity()
            except:
                pass
            
            # Use user ID if available, otherwise IP
            rate_limit_key = current_user_id or client_ip
            
            # For now, just log the rate limit attempt
            # Implement actual rate limiting with Redis in production
            print(f"Rate limit check for {rate_limit_key}: {max_requests} requests per {per_minutes} minutes")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_ownership(collection_name, id_field='_id', owner_field='user_id'):
    """Decorator to validate resource ownership"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            # Get resource ID from URL parameters
            resource_id = None
            for key, value in kwargs.items():
                if key.endswith('_id'):
                    resource_id = value
                    break
            
            if not resource_id:
                return jsonify({'error': 'Resource ID not found'}), 400
            
            # Check if resource exists and belongs to current user
            collection = getattr(mongo.db, collection_name)
            resource = collection.find_one({
                id_field: ObjectId(resource_id),
                owner_field: ObjectId(current_user_id)
            })
            
            if not resource:
                return jsonify({'error': 'Resource not found or access denied'}), 404
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_api_access(f):
    """Decorator to log API access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        import logging
        
        # Get user info if available
        current_user_id = None
        try:
            verify_jwt_in_request(optional=True)
            current_user_id = get_jwt_identity()
        except:
            pass
        
        # Log the request
        logging.info(f"API Access: {request.method} {request.endpoint} - User: {current_user_id} - IP: {request.remote_addr}")
        
        return f(*args, **kwargs)
    return decorated_function

def handle_exceptions(f):
    """Decorator to handle common exceptions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': f'Invalid data: {str(e)}'}), 400
        except KeyError as e:
            return jsonify({'error': f'Missing required field: {str(e)}'}), 400
        except Exception as e:
            import logging
            logging.error(f"Unexpected error in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    return decorated_function
