#!/usr/bin/env python3
"""
Test User model creation to debug registration issues
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.user import User
from app.utils.validators import validate_email, validate_password

def test_user_creation():
    """Test creating a User object"""
    
    print("🧪 Testing User model creation...")
    
    try:
        # Test data
        test_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User',
            'business_name': 'Test Business',
            'phone': '123-456-7890'
        }
        
        print(f"📧 Email validation: {validate_email(test_data['email'])}")
        print(f"🔒 Password validation: {validate_password(test_data['password'])}")
        
        # Create user
        user = User(
            email=test_data['email'],
            password=test_data['password'],
            name=test_data['name'],
            business_name=test_data['business_name'],
            phone=test_data['phone']
        )
        
        print("✅ User object created successfully!")
        print(f"📋 User dict: {user.to_dict()}")
        print(f"🔑 Has password_hash: {hasattr(user, 'password_hash')}")
        print(f"🔐 Password hash length: {len(user.password_hash) if hasattr(user, 'password_hash') else 'N/A'}")
        
        # Test password check
        print(f"🔍 Password check: {user.check_password('testpass123')}")
        print(f"❌ Wrong password check: {user.check_password('wrongpass')}")
        
        return True
        
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_user_creation()
