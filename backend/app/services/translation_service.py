"""
Translation Service - Multi-language support using Gemini API for Telugu and Hindi
"""

import requests
import logging
from typing import Dict, Any
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class TranslationService:
    """Service for handling translations using Gemini API with local storage cache"""
    
    def __init__(self):
        """Initialize the translation service with Gemini API"""
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        
        # Only support 3 languages as requested
        self.supported_languages = {
            'en': {'name': 'English', 'native': 'English', 'flag': '🇺🇸'},
            'te': {'name': 'Telugu', 'native': 'తెలుగు', 'flag': '🇮🇳'},
            'hi': {'name': 'Hindi', 'native': 'हिंदी', 'flag': '🇮🇳'}
        }
        
        # Cache for translations to avoid repeated API calls
        self.translation_cache = {}
        
        # Load existing cache from file if available
        self._load_cache_from_file()
        
        logger.info(f"Gemini Translation Service initialized with {len(self.supported_languages)} languages")
    
    def _load_cache_from_file(self):
        """Load translation cache from file"""
        try:
            cache_file = 'translation_cache.json'
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.translation_cache = json.load(f)
                logger.info(f"Loaded {len(self.translation_cache)} cached translations")
        except Exception as e:
            logger.warning(f"Could not load translation cache: {e}")
            self.translation_cache = {}
    
    def _save_cache_to_file(self):
        """Save translation cache to file"""
        try:
            cache_file = 'translation_cache.json'
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.translation_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Could not save translation cache: {e}")
    
    def get_supported_languages(self) -> Dict:
        """Get list of supported languages"""
        return self.supported_languages
    
    def translate_text(self, text, target_lang='en', source_lang='en'):
        """
        Translate text using Gemini API with local storage cache
        """
        if not text or target_lang == source_lang:
            return text
            
        # Check cache first
        cache_key = f"{source_lang}:{target_lang}:{text}"
        if cache_key in self.translation_cache:
            logger.info(f"Cache hit for: {text[:50]}...")
            return self.translation_cache[cache_key]
        
        # If target language is not supported, return original text
        if target_lang not in self.supported_languages:
            logger.warning(f"Unsupported language: {target_lang}")
            return text
        
        # If source is English and target is English, return as-is
        if source_lang == 'en' and target_lang == 'en':
            return text
        
        try:
            # Use Gemini API for translation
            logger.info(f"Translating with Gemini: '{text}' from {source_lang} to {target_lang}")
            translated_text = self._translate_with_gemini(text, target_lang, source_lang)
            
            # Cache the result
            self.translation_cache[cache_key] = translated_text
            self._save_cache_to_file()
            
            return translated_text
                
        except Exception as e:
            logger.warning(f"Gemini API translation failed: {e}")
            
            # Fallback to basic translations for common terms
            translated_text = self._fallback_translate(text, target_lang)
            self.translation_cache[cache_key] = translated_text
            return translated_text
    
    def _translate_with_gemini(self, text, target_lang, source_lang='en'):
        """Translate text using Gemini API"""
        try:
            # Language names for Gemini
            lang_names = {
                'en': 'English',
                'te': 'Telugu',
                'hi': 'Hindi'
            }
            
            source_name = lang_names.get(source_lang, 'English')
            target_name = lang_names.get(target_lang, 'English')
            
            # Create the prompt for Gemini
            prompt = f"""Translate the following text from {source_name} to {target_name}. 
Return only the translated text, no explanations or additional content.

Text to translate: {text}"""

            # Prepare the request payload
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            # Make the API request
            headers = {
                'Content-Type': 'application/json'
            }
            
            url = f"{self.gemini_api_url}?key={self.gemini_api_key}"
            
            logger.info(f"Making Gemini API request for: {text[:50]}...")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract the translated text from Gemini response
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        translated_text = candidate['content']['parts'][0]['text'].strip()
                        logger.info(f"Gemini translation successful: {text[:30]} -> {translated_text[:30]}")
                        return translated_text
                
                logger.warning("Unexpected Gemini API response format")
                return text
                
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return text
                
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return text
    
    def _fallback_translate(self, text, target_lang):
        """Fallback translations for common UI elements"""
        fallback_translations = {
            'te': {
                # Common UI elements
                'Home': 'హోమ్',
                'About': 'గురించి',
                'Services': 'సేవలు',
                'Contact': 'సంప్రదింపు',
                'Menu': 'మెను',
                'Book Now': 'ఇప్పుడే బుక్ చేయండి',
                'Call': 'కాల్ చేయండి',
                'Email': 'ఇమెయిల్',
                'Address': 'చిరునామా',
                'Phone': 'ఫోన్',
                'Welcome': 'స్వాగతం',
                'Gallery': 'గ్యాలరీ',
                'Testimonials': 'సాక్ష్యాలు',
                'FAQ': 'తరచుగా అడిగే ప్రశ్నలు',
                'Blog': 'బ్లాగ్',
                'Subscribe': 'సబ్‌స్క్రైబ్ చేయండి'
            },
            'hi': {
                # Common UI elements
                'Home': 'होम',
                'About': 'के बारे में',
                'Services': 'सेवाएं',
                'Contact': 'संपर्क',
                'Menu': 'मेनू',
                'Book Now': 'अभी बुक करें',
                'Call': 'कॉल करें',
                'Email': 'ईमेल',
                'Address': 'पता',
                'Phone': 'फोन',
                'Welcome': 'स्वागत',
                'Gallery': 'गैलरी',
                'Testimonials': 'प्रशंसापत्र',
                'FAQ': 'अक्सर पूछे जाने वाले प्रश्न',
                'Blog': 'ब्लॉग',
                'Subscribe': 'सब्सक्राइब करें'
            }
        }
        
        if target_lang in fallback_translations:
            return fallback_translations[target_lang].get(text, text)
        return text
    
    def translate_object(self, obj: Any, target_lang: str, source_lang: str = 'en') -> Any:
        """
        Recursively translate all strings in an object (dict, list, or string)
        """
        if isinstance(obj, str):
            return self.translate_text(obj, target_lang, source_lang)
        elif isinstance(obj, dict):
            return {key: self.translate_object(value, target_lang, source_lang) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.translate_object(item, target_lang, source_lang) for item in obj]
        else:
            return obj
    
    def translate_website_content(self, content: Dict, target_lang: str, source_lang: str = 'en') -> Dict:
        """
        Translate website content structure
        """
        translated_content = {}
        
        for section, data in content.items():
            logger.info(f"Translating section: {section}")
            translated_content[section] = self.translate_object(data, target_lang, source_lang)
        
        return translated_content
    
    def get_ui_translations(self, target_lang: str) -> Dict[str, str]:
        """
        Get UI translations for common interface elements
        """
        ui_elements = [
            'Home', 'About', 'Services', 'Contact', 'Menu', 'Book Now',
            'Call', 'Email', 'Address', 'Phone', 'Welcome', 'Gallery',
            'Testimonials', 'FAQ', 'Blog', 'Subscribe'
        ]
        
        translations = {}
        for element in ui_elements:
            translations[element] = self.translate_text(element, target_lang, 'en')
        
        return translations
    
    def bulk_translate(self, texts: list, target_lang: str, source_lang: str = 'en') -> Dict[str, str]:
        """
        Translate multiple texts at once and return a mapping
        """
        translations = {}
        for text in texts:
            if text:
                translations[text] = self.translate_text(text, target_lang, source_lang)
        return translations
    
    def clear_cache(self):
        """Clear the translation cache"""
        self.translation_cache = {}
        try:
            if os.path.exists('translation_cache.json'):
                os.remove('translation_cache.json')
            logger.info("Translation cache cleared")
        except Exception as e:
            logger.warning(f"Could not clear cache file: {e}")
    
    def get_cache_stats(self):
        """Get cache statistics"""
        total_translations = len(self.translation_cache)
        by_language = {}
        
        for key in self.translation_cache.keys():
            parts = key.split(':', 2)
            if len(parts) >= 2:
                target_lang = parts[1]
                by_language[target_lang] = by_language.get(target_lang, 0) + 1
        
        return {
            'total_translations': total_translations,
            'by_language': by_language,
            'supported_languages': list(self.supported_languages.keys())
        }

# Create a global instance
translation_service = TranslationService()