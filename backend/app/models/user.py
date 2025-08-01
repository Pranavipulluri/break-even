
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson import ObjectId

class User:
    def __init__(self, email, password, name, business_name=None, phone=None):
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.business_name = business_name
        self.phone = phone
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_active = True
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'email': self.email,
            'name': self.name,
            'business_name': self.business_name,
            'phone': self.phone,
            'created_at': self.created_at,
            'is_active': self.is_active
        }
    
    @staticmethod
    def from_dict(data):
        user = User(
            email=data['email'],
            password='',  # Will be set separately
            name=data['name'],
            business_name=data.get('business_name'),
            phone=data.get('phone')
        )
        user.password_hash = data['password_hash']
        user.created_at = data.get('created_at', datetime.utcnow())
        user.updated_at = data.get('updated_at', datetime.utcnow())
        user.is_active = data.get('is_active', True)
        return user
