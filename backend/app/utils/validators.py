#### app/utils/validators.py

import re
from datetime import datetime

def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if not password:
        return False
    
    # At least 8 characters long
    if len(password) < 8:
        return False
    
    # Contains at least one letter and one number
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    return has_letter and has_number

def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return True  # Phone is optional
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (10-15 digits)
    return 10 <= len(digits_only) <= 15

def validate_url(url):
    """Validate URL format"""
    if not url:
        return False
    
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
    return re.match(pattern, url) is not None

def validate_business_data(data):
    """Validate business website creation data"""
    errors = []
    
    required_fields = ['website_name', 'business_type', 'color_theme', 'contact_info', 'area']
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f'{field} is required')
    
    # Validate contact info structure
    if 'contact_info' in data and isinstance(data['contact_info'], dict):
        contact_info = data['contact_info']
        
        if 'email' in contact_info and not validate_email(contact_info['email']):
            errors.append('Invalid email in contact information')
        
        if 'phone' in contact_info and not validate_phone(contact_info['phone']):
            errors.append('Invalid phone number in contact information')
    
    # Validate website name length
    if 'website_name' in data and len(data['website_name']) > 100:
        errors.append('Website name must be less than 100 characters')
    
    # Validate color theme
    valid_themes = ['warm', 'fresh', 'elegant', 'modern', 'classic', 'bold', 
                   'corporate', 'minimal', 'trust', 'soft', 'luxurious', 
                   'tech', 'futuristic', 'neutral', 'business', 'friendly']
    
    if 'color_theme' in data and data['color_theme'] not in valid_themes:
        errors.append('Invalid color theme selected')
    
    return errors

def validate_product_data(data):
    """Validate product data"""
    errors = []
    
    required_fields = ['name', 'description', 'price', 'stock', 'category']
    
    for field in required_fields:
        if field not in data:
            errors.append(f'{field} is required')
    
    # Validate price
    if 'price' in data:
        try:
            price = float(data['price'])
            if price < 0:
                errors.append('Price must be non-negative')
        except (ValueError, TypeError):
            errors.append('Price must be a valid number')
    
    # Validate stock
    if 'stock' in data:
        try:
            stock = int(data['stock'])
            if stock < 0:
                errors.append('Stock must be non-negative')
        except (ValueError, TypeError):
            errors.append('Stock must be a valid integer')
    
    # Validate name length
    if 'name' in data and len(data['name']) > 200:
        errors.append('Product name must be less than 200 characters')
    
    # Validate description length
    if 'description' in data and len(data['description']) > 2000:
        errors.append('Product description must be less than 2000 characters')
    
    return errors

def sanitize_input(text):
    """Sanitize text input to prevent XSS"""
    if not text:
        return text
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', str(text))
    
    # Remove script tags completely
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Limit length
    return text[:5000] if len(text) > 5000 else text

def validate_message_data(data):
    """Validate message data"""
    errors = []
    
    required_fields = ['recipient_id', 'content', 'customer_name', 'customer_email']
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f'{field} is required')
    
    # Validate email
    if 'customer_email' in data and not validate_email(data['customer_email']):
        errors.append('Invalid customer email')
    
    # Validate content length
    if 'content' in data and len(data['content']) > 5000:
        errors.append('Message content must be less than 5000 characters')
    
    # Validate customer name length
    if 'customer_name' in data and len(data['customer_name']) > 100:
        errors.append('Customer name must be less than 100 characters')
    
    return errors

