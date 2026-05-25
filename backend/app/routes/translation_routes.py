"""
Translation API Routes - Multi-language support for the website builder
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
import traceback

# Import translation service
from app.services.translation_service import TranslationService

logger = logging.getLogger(__name__)

# Create Blueprint
translation_bp = Blueprint('translation', __name__)

# Initialize translation service
translation_service = TranslationService()

@translation_bp.route('/translation/languages', methods=['GET'])
def get_supported_languages():
    """Get list of supported languages"""
    try:
        languages = translation_service.get_supported_languages()
        
        return jsonify({
            "success": True,
            "languages": languages,
            "default_language": "en",
            "total_languages": len(languages)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting languages: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get supported languages"
        }), 500

@translation_bp.route('/translation/translate-text', methods=['POST'])
def translate_text():
    """Translate a single text string"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        text = data.get('text')
        target_lang = data.get('target_lang', 'en')
        source_lang = data.get('source_lang', 'en')
        
        if not text:
            return jsonify({
                "success": False,
                "error": "Text is required"
            }), 400
        
        # Translate the text
        translated_text = translation_service.translate_text(text, target_lang, source_lang)
        
        return jsonify({
            "success": True,
            "original_text": text,
            "translated_text": translated_text,
            "source_language": source_lang,
            "target_language": target_lang
        }), 200
        
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        return jsonify({
            "success": False,
            "error": "Translation failed"
        }), 500

@translation_bp.route('/translation/translate-website', methods=['POST'])
def translate_website():
    """Translate complete website content"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No website data provided"
            }), 400
        
        website_data = data.get('website_data')
        target_lang = data.get('target_lang', 'en')
        
        if not website_data:
            return jsonify({
                "success": False,
                "error": "Website data is required"
            }), 400
        
        # Translate website content
        translated_website = translation_service.translate_website_content(website_data, target_lang)
        
        return jsonify({
            "success": True,
            "translated_website": translated_website,
            "target_language": target_lang,
            "translation_completed": True
        }), 200
        
    except Exception as e:
        logger.error(f"Error translating website: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": "Website translation failed"
        }), 500

@translation_bp.route('/translation/translate-business-card', methods=['POST'])
def translate_business_card():
    """Translate business card content"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No business card data provided"
            }), 400
        
        card_data = data.get('card_data')
        target_lang = data.get('target_lang', 'en')
        
        if not card_data:
            return jsonify({
                "success": False,
                "error": "Business card data is required"
            }), 400
        
        # Translate business card content
        translated_card = translation_service.translate_business_card_content(card_data, target_lang)
        
        return jsonify({
            "success": True,
            "translated_card": translated_card,
            "target_language": target_lang
        }), 200
        
    except Exception as e:
        logger.error(f"Error translating business card: {e}")
        return jsonify({
            "success": False,
            "error": "Business card translation failed"
        }), 500

@translation_bp.route('/translation/get-ui-translations', methods=['GET'])
def get_ui_translations():
    """Get translated UI labels and messages"""
    try:
        target_lang = request.args.get('lang', 'en')
        
        # Get UI translations
        ui_translations = translation_service.get_ui_translations(target_lang)
        
        return jsonify({
            "success": True,
            "ui_translations": ui_translations,
            "language": target_lang
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting UI translations: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get UI translations"
        }), 500

@translation_bp.route('/translation/detect-language', methods=['POST'])
def detect_language():
    """Detect language of given text"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        text = data.get('text')
        
        if not text:
            return jsonify({
                "success": False,
                "error": "Text is required"
            }), 400
        
        # Detect language
        detected_lang = translation_service.detect_language(text)
        
        # Get language info
        languages = translation_service.get_supported_languages()
        lang_info = languages.get(detected_lang, {
            'name': 'Unknown',
            'native': 'Unknown',
            'flag': '❓'
        })
        
        return jsonify({
            "success": True,
            "detected_language": detected_lang,
            "language_info": lang_info,
            "confidence": "medium"  # Simplified confidence
        }), 200
        
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        return jsonify({
            "success": False,
            "error": "Language detection failed"
        }), 500

@translation_bp.route('/translation/translate-law-firm', methods=['POST'])
def translate_law_firm():
    """Translate law firm specific content"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No law firm data provided"
            }), 400
        
        law_firm_data = data.get('law_firm_data')
        target_lang = data.get('target_lang', 'en')
        
        if not law_firm_data:
            return jsonify({
                "success": False,
                "error": "Law firm data is required"
            }), 400
        
        # Translate law firm specific content
        translated_data = translation_service.translate_website_content(law_firm_data, target_lang)
        
        # Add law firm specific translations
        if 'practice_areas' in translated_data:
            translated_data['practice_areas'] = translation_service.translate_object(
                translated_data['practice_areas'], target_lang
            )
        
        return jsonify({
            "success": True,
            "translated_law_firm": translated_data,
            "target_language": target_lang
        }), 200
        
    except Exception as e:
        logger.error(f"Error translating law firm: {e}")
        return jsonify({
            "success": False,
            "error": "Law firm translation failed"
        }), 500

@translation_bp.route('/translation/translate-beauty-salon', methods=['POST'])
def translate_beauty_salon():
    """Translate beauty salon specific content"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No beauty salon data provided"
            }), 400
        
        salon_data = data.get('salon_data')
        target_lang = data.get('target_lang', 'en')
        
        if not salon_data:
            return jsonify({
                "success": False,
                "error": "Beauty salon data is required"
            }), 400
        
        # Translate beauty salon specific content
        translated_data = translation_service.translate_website_content(salon_data, target_lang)
        
        # Add beauty salon specific translations
        if 'services' in translated_data:
            translated_data['services'] = translation_service.translate_object(
                translated_data['services'], target_lang
            )
        
        if 'staff_members' in translated_data:
            translated_data['staff_members'] = translation_service.translate_object(
                translated_data['staff_members'], target_lang
            )
        
        return jsonify({
            "success": True,
            "translated_salon": translated_data,
            "target_language": target_lang
        }), 200
        
    except Exception as e:
        logger.error(f"Error translating beauty salon: {e}")
        return jsonify({
            "success": False,
            "error": "Beauty salon translation failed"
        }), 500

@translation_bp.route('/translation/batch-translate', methods=['POST'])
def batch_translate():
    """Translate multiple items in batch"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        items = data.get('items', [])
        target_lang = data.get('target_lang', 'en')
        source_lang = data.get('source_lang', 'en')
        
        if not items:
            return jsonify({
                "success": False,
                "error": "Items array is required"
            }), 400
        
        # Translate all items
        translated_items = []
        for item in items:
            if isinstance(item, str):
                translated_text = translation_service.translate_text(item, target_lang, source_lang)
                translated_items.append(translated_text)
            elif isinstance(item, dict):
                translated_obj = translation_service.translate_object(item, target_lang, source_lang)
                translated_items.append(translated_obj)
            else:
                translated_items.append(item)
        
        return jsonify({
            "success": True,
            "translated_items": translated_items,
            "total_items": len(translated_items),
            "target_language": target_lang,
            "source_language": source_lang
        }), 200
        
    except Exception as e:
        logger.error(f"Error in batch translation: {e}")
        return jsonify({
            "success": False,
            "error": "Batch translation failed"
        }), 500

# Health check
@translation_bp.route('/translation/health', methods=['GET'])
def health_check():
    """Health check for translation service"""
    try:
        # Test translation service
        test_translation = translation_service.translate_text("Hello", "es")
        
        return jsonify({
            "success": True,
            "message": "Translation service is healthy",
            "test_translation": test_translation,
            "supported_languages": len(translation_service.get_supported_languages()),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Translation health check failed: {e}")
        return jsonify({
            "success": False,
            "error": "Translation service health check failed"
        }), 500

# Error handlers
@translation_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Translation endpoint not found"
    }), 404

@translation_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "Method not allowed"
    }), 405

@translation_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Translation service internal error"
    }), 500