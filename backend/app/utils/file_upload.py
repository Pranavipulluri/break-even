"""
File Upload Utilities
Handles file uploads for law firm websites including attorney photos, documents, and logos.
"""

import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import logging

logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'images': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'documents': {'pdf', 'doc', 'docx', 'txt'},
    'all': {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'doc', 'docx', 'txt'}
}

# Maximum file sizes (in bytes)
MAX_FILE_SIZES = {
    'image': 5 * 1024 * 1024,  # 5MB
    'document': 10 * 1024 * 1024,  # 10MB
}

def allowed_file(filename, file_type='all'):
    """
    Check if file extension is allowed
    
    Args:
        filename (str): The filename to check
        file_type (str): Type of file ('images', 'documents', 'all')
    
    Returns:
        bool: True if file is allowed, False otherwise
    """
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS.get(file_type, ALLOWED_EXTENSIONS['all'])

def get_file_type(filename):
    """
    Determine file type based on extension
    
    Args:
        filename (str): The filename to check
    
    Returns:
        str: File type ('image', 'document', 'unknown')
    """
    if '.' not in filename:
        return 'unknown'
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if extension in ALLOWED_EXTENSIONS['images']:
        return 'image'
    elif extension in ALLOWED_EXTENSIONS['documents']:
        return 'document'
    else:
        return 'unknown'

def generate_unique_filename(original_filename):
    """
    Generate a unique filename while preserving the extension
    
    Args:
        original_filename (str): Original filename
    
    Returns:
        str: Unique filename
    """
    filename = secure_filename(original_filename)
    name, extension = os.path.splitext(filename)
    unique_id = str(uuid.uuid4())[:8]
    return f"{name}_{unique_id}{extension}"

def validate_file_size(file, max_size=None):
    """
    Validate file size
    
    Args:
        file: File object
        max_size (int): Maximum allowed size in bytes
    
    Returns:
        bool: True if file size is acceptable, False otherwise
    """
    if not max_size:
        file_type = get_file_type(file.filename)
        max_size = MAX_FILE_SIZES.get(file_type, MAX_FILE_SIZES['document'])
    
    # Get file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    return file_size <= max_size

def optimize_image(image_path, max_width=800, max_height=600, quality=85):
    """
    Optimize image for web use
    
    Args:
        image_path (str): Path to the image file
        max_width (int): Maximum width
        max_height (int): Maximum height
        quality (int): JPEG quality (1-100)
    
    Returns:
        bool: True if optimization successful, False otherwise
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Calculate new dimensions while maintaining aspect ratio
            width, height = img.size
            aspect_ratio = width / height
            
            if width > max_width:
                width = max_width
                height = int(width / aspect_ratio)
            
            if height > max_height:
                height = max_height
                width = int(height * aspect_ratio)
            
            # Resize image
            if (width, height) != img.size:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            if image_path.lower().endswith('.png'):
                img.save(image_path, 'PNG', optimize=True)
            else:
                img.save(image_path, 'JPEG', quality=quality, optimize=True)
            
            return True
            
    except Exception as e:
        logger.error(f"Error optimizing image {image_path}: {e}")
        return False

def handle_file_upload(file, upload_dir, file_type='all', optimize_images=True):
    """
    Handle file upload with validation, unique naming, and optimization
    
    Args:
        file: File object from request
        upload_dir (str): Directory to save the file
        file_type (str): Type of file to validate against
        optimize_images (bool): Whether to optimize images
    
    Returns:
        dict: Result with success status, filename, and path or error message
    """
    try:
        # Validate file
        if not file or file.filename == '':
            return {
                'success': False,
                'error': 'No file provided'
            }
        
        if not allowed_file(file.filename, file_type):
            return {
                'success': False,
                'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS[file_type])}'
            }
        
        if not validate_file_size(file):
            file_type_detected = get_file_type(file.filename)
            max_size_mb = MAX_FILE_SIZES.get(file_type_detected, MAX_FILE_SIZES['document']) / (1024 * 1024)
            return {
                'success': False,
                'error': f'File too large. Maximum size: {max_size_mb}MB'
            }
        
        # Create upload directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Optimize image if applicable
        if optimize_images and get_file_type(file.filename) == 'image':
            optimize_image(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        
        return {
            'success': True,
            'filename': unique_filename,
            'original_filename': file.filename,
            'file_path': file_path,
            'file_size': file_size,
            'file_type': get_file_type(file.filename)
        }
        
    except Exception as e:
        logger.error(f"Error handling file upload: {e}")
        return {
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }

def delete_file(file_path):
    """
    Safely delete a file
    
    Args:
        file_path (str): Path to the file to delete
    
    Returns:
        bool: True if deletion successful, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return False

def get_file_url(filename, base_url, upload_type='general'):
    """
    Generate URL for uploaded file
    
    Args:
        filename (str): Name of the file
        base_url (str): Base URL of the application
        upload_type (str): Type of upload ('attorney_photos', 'business_cards', etc.)
    
    Returns:
        str: Full URL to the file
    """
    return f"{base_url}/static/{upload_type}/{filename}"

def create_upload_directories(base_static_dir):
    """
    Create all necessary upload directories
    
    Args:
        base_static_dir (str): Base static directory path
    """
    directories = [
        'attorney_photos',
        'business_cards',
        'qr_codes',
        'firm_logos',
        'documents'
    ]
    
    for directory in directories:
        dir_path = os.path.join(base_static_dir, directory)
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")