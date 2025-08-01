from datetime import datetime, timezone
from bson import ObjectId
import hashlib
import secrets
import string

def generate_secure_token(length=32):
    """Generate a secure random token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_data(data):
    """Hash data using SHA-256"""
    return hashlib.sha256(str(data).encode()).hexdigest()

def format_datetime(dt):
    """Format datetime for JSON serialization"""
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt

def parse_datetime(dt_string):
    """Parse datetime string"""
    try:
        return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
    except:
        return datetime.utcnow()

def convert_objectid_to_str(document):
    """Convert ObjectId fields to strings in a document"""
    if isinstance(document, dict):
        for key, value in document.items():
            if isinstance(value, ObjectId):
                document[key] = str(value)
            elif isinstance(value, dict):
                convert_objectid_to_str(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        convert_objectid_to_str(item)
    return document

def calculate_pagination(total, page, per_page):
    """Calculate pagination details"""
    pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < pages
    prev_page = page - 1 if has_prev else None
    next_page = page + 1 if has_next else None
    
    return {
        'total': total,
        'pages': pages,
        'page': page,
        'per_page': per_page,
        'has_prev': has_prev,
        'has_next': has_next,
        'prev_page': prev_page,
        'next_page': next_page
    }

def truncate_text(text, max_length=100):
    """Truncate text to specified length"""
    if not text:
        return text
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + '...'

def clean_phone_number(phone):
    """Clean and format phone number"""
    if not phone:
        return phone
    
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Format based on length
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone

def generate_slug(text):
    """Generate URL-friendly slug from text"""
    import re
    
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug[:50]  # Limit length

def calculate_sentiment_score(sentiment_data):
    """Calculate overall sentiment score"""
    if not sentiment_data:
        return 0
    
    total_score = 0
    total_weight = 0
    
    for item in sentiment_data:
        score = item.get('score', 0)
        confidence = item.get('confidence', 1)
        
        total_score += score * confidence
        total_weight += confidence
    
    return total_score / total_weight if total_weight > 0 else 0

def format_currency(amount, currency='USD'):
    """Format currency amount"""
    try:
        amount = float(amount)
        if currency == 'USD':
            return f"${amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"
    except:
        return str(amount)

def get_business_hours_status(hours_config):
    """Check if business is currently open"""
    if not hours_config:
        return {'is_open': False, 'message': 'Hours not specified'}
    
    now = datetime.now()
    current_day = now.strftime('%A').lower()
    current_time = now.time()
    
    if current_day in hours_config:
        day_hours = hours_config[current_day]
        if day_hours.get('closed', False):
            return {'is_open': False, 'message': 'Closed today'}
        
        open_time = day_hours.get('open')
        close_time = day_hours.get('close')
        
        if open_time and close_time:
            # Convert string times to time objects if needed
            if isinstance(open_time, str):
                open_time = datetime.strptime(open_time, '%H:%M').time()
            if isinstance(close_time, str):
                close_time = datetime.strptime(close_time, '%H:%M').time()
            
            if open_time <= current_time <= close_time:
                return {'is_open': True, 'message': f'Open until {close_time.strftime("%I:%M %p")}'}
            else:
                return {'is_open': False, 'message': f'Opens at {open_time.strftime("%I:%M %p")}'}
    
    return {'is_open': False, 'message': 'Hours not available'}

def generate_qr_filename(business_name, size=None):
    """Generate filename for QR code"""
    slug = generate_slug(business_name)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    filename = f"qr_{slug}_{timestamp}"
    if size:
        filename += f"_{size}x{size}"
    
    return f"{filename}.png"

def validate_image_url(url):
    """Validate if URL points to an image"""
    if not url:
        return False
    
    # Check for common image extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
    url_lower = url.lower()
    
    return any(url_lower.endswith(ext) for ext in image_extensions)

def extract_domain_from_email(email):
    """Extract domain from email address"""
    try:
        return email.split('@')[1].lower()
    except:
        return None

def calculate_business_score(metrics):
    """Calculate overall business performance score"""
    if not metrics:
        return 0
    
    # Weights for different metrics
    weights = {
        'total_customers': 0.3,
        'total_messages': 0.2,
        'qr_scans': 0.2,
        'products_count': 0.15,
        'response_rate': 0.15
    }
    
    score = 0
    max_score = 100
    
    # Normalize and weight each metric
    for metric, weight in weights.items():
        value = metrics.get(metric, 0)
        
        # Normalize based on typical ranges
        if metric == 'total_customers':
            normalized = min(value / 100, 1)  # 100 customers = max score
        elif metric == 'total_messages':
            normalized = min(value / 50, 1)   # 50 messages = max score
        elif metric == 'qr_scans':
            normalized = min(value / 200, 1)  # 200 scans = max score
        elif metric == 'products_count':
            normalized = min(value / 20, 1)   # 20 products = max score
        elif metric == 'response_rate':
            normalized = value  # Already a percentage
        else:
            normalized = 0
        
        score += normalized * weight * max_score
    
    return min(int(score), max_score)
