"""
Image Generation Routes using Stability AI
"""

from flask import Blueprint, request, jsonify, current_app, send_from_directory
from app.services.stability_ai_service import StabilityAIService
import os

images_bp = Blueprint('images', __name__)

@images_bp.route('/api/images/generate-business-poster', methods=['POST'])
def generate_business_poster():
    """Generate a business poster using Stability AI"""
    try:
        data = request.get_json()
        
        business_name = data.get('business_name', '')
        business_type = data.get('business_type', '')
        style = data.get('style', 'professional')
        additional_text = data.get('additional_text', '')
        
        if not business_name or not business_type:
            return jsonify({
                'success': False,
                'error': 'Business name and type are required'
            }), 400
        
        # Initialize Stability AI service
        stability_service = StabilityAIService()
        
        # Generate poster
        result = stability_service.generate_business_poster(
            business_name=business_name,
            business_type=business_type,
            style=style,
            additional_text=additional_text
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate business poster: {str(e)}'
        }), 500

@images_bp.route('/api/images/generate-product-image', methods=['POST'])
def generate_product_image():
    """Generate a product image using Stability AI"""
    try:
        data = request.get_json()
        
        product_name = data.get('product_name', '')
        product_description = data.get('product_description', '')
        style = data.get('style', 'high-quality product photo')
        
        if not product_name:
            return jsonify({
                'success': False,
                'error': 'Product name is required'
            }), 400
        
        # Initialize Stability AI service
        stability_service = StabilityAIService()
        
        # Generate product image
        result = stability_service.generate_product_image(
            product_name=product_name,
            product_description=product_description,
            style=style
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate product image: {str(e)}'
        }), 500

@images_bp.route('/api/images/generate-marketing-banner', methods=['POST'])
def generate_marketing_banner():
    """Generate a marketing banner using Stability AI"""
    try:
        data = request.get_json()
        
        business_name = data.get('business_name', '')
        message = data.get('message', '')
        dimensions = data.get('dimensions', 'banner')
        style = data.get('style', 'modern')
        
        if not business_name or not message:
            return jsonify({
                'success': False,
                'error': 'Business name and message are required'
            }), 400
        
        # Initialize Stability AI service
        stability_service = StabilityAIService()
        
        # Generate marketing banner
        result = stability_service.generate_marketing_banner(
            business_name=business_name,
            message=message,
            dimensions=dimensions,
            style=style
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate marketing banner: {str(e)}'
        }), 500

@images_bp.route('/api/images/generate-hero-image', methods=['POST'])
def generate_hero_image():
    """Generate a website hero image using Stability AI"""
    try:
        data = request.get_json()
        
        business_name = data.get('business_name', '')
        business_type = data.get('business_type', '')
        mood = data.get('mood', 'professional and welcoming')
        
        if not business_name or not business_type:
            return jsonify({
                'success': False,
                'error': 'Business name and type are required'
            }), 400
        
        # Initialize Stability AI service
        stability_service = StabilityAIService()
        
        # Generate hero image
        result = stability_service.generate_hero_image(
            business_name=business_name,
            business_type=business_type,
            mood=mood
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate hero image: {str(e)}'
        }), 500

@images_bp.route('/api/images/account-info', methods=['GET'])
def get_account_info():
    """Get Stability AI account information"""
    try:
        stability_service = StabilityAIService()
        result = stability_service.get_account_info()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get account info: {str(e)}'
        }), 500

@images_bp.route('/api/images/engines', methods=['GET'])
def list_engines():
    """List available Stability AI engines"""
    try:
        stability_service = StabilityAIService()
        result = stability_service.list_engines()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to list engines: {str(e)}'
        }), 500

@images_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded images"""
    try:
        uploads_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'uploads'
        )
        return send_from_directory(uploads_dir, filename)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'File not found: {str(e)}'
        }), 404

# Image generation presets for different business types
@images_bp.route('/api/images/business-presets', methods=['GET'])
def get_business_presets():
    """Get predefined image generation presets for different business types"""
    presets = {
        'bakery': {
            'poster_styles': ['warm and inviting', 'artisanal', 'cozy'],
            'hero_moods': ['warm and welcoming', 'cozy bakery atmosphere', 'artisanal craftsmanship'],
            'product_styles': ['fresh baked goods photography', 'artisanal bread styling', 'dessert photography']
        },
        'restaurant': {
            'poster_styles': ['elegant dining', 'casual friendly', 'gourmet'],
            'hero_moods': ['inviting dining atmosphere', 'elegant restaurant interior', 'cozy dining experience'],
            'product_styles': ['gourmet food photography', 'restaurant plating', 'culinary presentation']
        },
        'retail': {
            'poster_styles': ['modern retail', 'boutique style', 'trendy shopping'],
            'hero_moods': ['modern shopping experience', 'boutique atmosphere', 'trendy retail space'],
            'product_styles': ['product showcase', 'retail display', 'lifestyle photography']
        },
        'service': {
            'poster_styles': ['professional service', 'trustworthy', 'expert'],
            'hero_moods': ['professional and reliable', 'trustworthy service', 'expert consultation'],
            'product_styles': ['service illustration', 'professional presentation', 'consultation setup']
        },
        'beauty': {
            'poster_styles': ['elegant beauty', 'spa relaxation', 'glamorous'],
            'hero_moods': ['luxurious spa atmosphere', 'elegant beauty salon', 'relaxing treatment space'],
            'product_styles': ['beauty product photography', 'cosmetic styling', 'spa treatment setup']
        },
        'fitness': {
            'poster_styles': ['energetic fitness', 'motivational', 'healthy lifestyle'],
            'hero_moods': ['energetic gym atmosphere', 'motivational fitness space', 'healthy lifestyle'],
            'product_styles': ['fitness equipment photography', 'workout gear styling', 'health supplement display']
        }
    }
    
    return jsonify({
        'success': True,
        'presets': presets
    })

# Batch image generation for complete business branding
@images_bp.route('/api/images/generate-business-branding', methods=['POST'])
def generate_business_branding():
    """Generate a complete set of images for business branding"""
    try:
        data = request.get_json()
        
        business_name = data.get('business_name', '')
        business_type = data.get('business_type', '')
        style = data.get('style', 'professional')
        
        if not business_name or not business_type:
            return jsonify({
                'success': False,
                'error': 'Business name and type are required'
            }), 400
        
        stability_service = StabilityAIService()
        results = {}
        
        # Generate business poster
        print("🎨 Generating business poster...")
        results['poster'] = stability_service.generate_business_poster(
            business_name=business_name,
            business_type=business_type,
            style=style
        )
        
        # Generate hero image
        print("🌟 Generating hero image...")
        results['hero'] = stability_service.generate_website_hero_image(
            business_name=business_name,
            business_type=business_type
        )
        
        # Generate marketing banner
        print("🎯 Generating marketing banner...")
        results['banner'] = stability_service.generate_marketing_banner(
            business_name=business_name,
            message=f"Welcome to {business_name}",
            style=style
        )
        
        # Count successful generations
        successful_generations = sum(1 for result in results.values() if result.get('success'))
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': {
                'total_requested': 3,
                'successful': successful_generations,
                'failed': 3 - successful_generations
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate business branding: {str(e)}'
        }), 500
