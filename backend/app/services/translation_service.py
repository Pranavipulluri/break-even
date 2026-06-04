"""
Translation Service - Multi-language support using Gemini API for Telugu and Hindi.

Cache layer:
    Primary:  Small LRU in-memory cache (last 200 entries) for hot-path speed.
    Backend:  MongoDB `translation_cache` collection for persistence across restarts
              and cross-user scaling. TTL index auto-expires entries after 30 days.
"""

import requests
import logging
from typing import Dict, Any
from collections import OrderedDict
import json
import os
from datetime import datetime, timezone
from app import mongo

logger = logging.getLogger(__name__)

LRU_MAX_SIZE = 200


class TranslationService:
    """Service for handling translations using Gemini API with MongoDB + LRU cache"""

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

        # Small LRU in-memory cache for hot-path performance
        self._lru_cache = OrderedDict()

        logger.info(f"Gemini Translation Service initialized with {len(self.supported_languages)} languages (MongoDB + LRU cache)")

    # ================================================================
    # Cache layer — LRU in-memory + MongoDB backend
    # ================================================================

    def _cache_key(self, source_lang, target_lang, text):
        return f"{source_lang}:{target_lang}:{text}"

    def _get_from_cache(self, source_lang, target_lang, text):
        """Check LRU first, then MongoDB."""
        key = self._cache_key(source_lang, target_lang, text)

        # LRU hit
        if key in self._lru_cache:
            self._lru_cache.move_to_end(key)
            return self._lru_cache[key]

        # MongoDB hit
        try:
            doc = mongo.db.translation_cache.find_one(
                {"source_lang": source_lang, "target_lang": target_lang, "source_text": text},
                {"translated_text": 1}
            )
            if doc:
                translated = doc["translated_text"]
                self._put_lru(key, translated)
                # Bump hit_count
                mongo.db.translation_cache.update_one(
                    {"_id": doc["_id"]},
                    {"$inc": {"hit_count": 1}},
                )
                return translated
        except Exception as e:
            logger.warning(f"MongoDB translation cache lookup failed: {e}")

        return None

    def _put_to_cache(self, source_lang, target_lang, text, translated_text):
        """Write to both LRU and MongoDB."""
        key = self._cache_key(source_lang, target_lang, text)
        self._put_lru(key, translated_text)

        try:
            mongo.db.translation_cache.update_one(
                {"source_lang": source_lang, "target_lang": target_lang, "source_text": text},
                {"$set": {
                    "translated_text": translated_text,
                    "created_at": datetime.now(timezone.utc),
                    "hit_count": 1,
                }},
                upsert=True,
            )
        except Exception as e:
            logger.warning(f"MongoDB translation cache write failed: {e}")

    def _put_lru(self, key, value):
        """Add to LRU, evicting oldest if full."""
        if key in self._lru_cache:
            self._lru_cache.move_to_end(key)
        self._lru_cache[key] = value
        while len(self._lru_cache) > LRU_MAX_SIZE:
            self._lru_cache.popitem(last=False)

    # ================================================================
    # Core translation
    # ================================================================

    def get_supported_languages(self) -> Dict:
        """Get list of supported languages"""
        return self.supported_languages

    def translate_text(self, text, target_lang='en', source_lang='en'):
        """
        Translate text using Gemini API with MongoDB + LRU cache
        """
        if not text or target_lang == source_lang:
            return text

        # Check cache first
        cached = self._get_from_cache(source_lang, target_lang, text)
        if cached:
            logger.info(f"Cache hit for: {text[:50]}...")
            return cached

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
            self._put_to_cache(source_lang, target_lang, text, translated_text)

            return translated_text

        except Exception as e:
            logger.warning(f"Gemini API translation failed: {e}")

            # Fallback to basic translations for common terms
            translated_text = self._fallback_translate(text, target_lang)
            self._put_to_cache(source_lang, target_lang, text, translated_text)
            return translated_text

    def _translate_with_gemini(self, text, target_lang, source_lang='en'):
        """Translate text using Gemini API"""
        try:
            lang_names = {
                'en': 'English',
                'te': 'Telugu',
                'hi': 'Hindi'
            }

            source_name = lang_names.get(source_lang, 'English')
            target_name = lang_names.get(target_lang, 'English')

            prompt = f"""Translate the following text from {source_name} to {target_name}. 
Return only the translated text, no explanations or additional content.

Text to translate: {text}"""

            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }

            headers = {
                'Content-Type': 'application/json'
            }

            url = f"{self.gemini_api_url}?key={self.gemini_api_key}"

            logger.info(f"Making Gemini API request for: {text[:50]}...")
            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                result = response.json()

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

    # ================================================================
    # Bulk / recursive translation
    # ================================================================

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
        """Clear the translation cache (both LRU and MongoDB)"""
        self._lru_cache.clear()
        try:
            mongo.db.translation_cache.delete_many({})
            logger.info("Translation cache cleared (LRU + MongoDB)")
        except Exception as e:
            logger.warning(f"Could not clear MongoDB translation cache: {e}")

    def get_cache_stats(self):
        """Get cache statistics"""
        try:
            total_mongo = mongo.db.translation_cache.count_documents({})

            pipeline = [
                {"$group": {"_id": "$target_lang", "count": {"$sum": 1}}}
            ]
            by_language = {}
            for doc in mongo.db.translation_cache.aggregate(pipeline):
                by_language[doc["_id"]] = doc["count"]

        except Exception:
            total_mongo = 0
            by_language = {}

        return {
            'total_translations_mongodb': total_mongo,
            'lru_cache_size': len(self._lru_cache),
            'lru_cache_max': LRU_MAX_SIZE,
            'by_language': by_language,
            'supported_languages': list(self.supported_languages.keys())
        }


# Create a global instance
translation_service = TranslationService()