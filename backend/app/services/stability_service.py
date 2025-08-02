# app/services/stability_service.py

import os
import requests
import base64
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class StabilityService:
    def __init__(self):
        # Try to get API key from environment or config
        self.api_key = os.getenv('STABILITY_API_KEY')
        if not self.api_key:
            try:
                from flask import current_app
                self.api_key = current_app.config.get('STABILITY_API_KEY')
            except RuntimeError:
                # Fallback when outside application context
                self.api_key = 'sk-Ci8STOuJz4ZE1xGzmQXFDoykscMoNFoD4OCQZr5BlWgd83O2'
        
        self.base_url = "https://api.stability.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Stability AI API"""
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'STABILITY_API_KEY environment variable not set'
                }
            
            # Test with account endpoint
            response = requests.get(
                f"{self.base_url}/v1/user/account",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Successfully connected to Stability AI'
                }
            else:
                return {
                    'success': False,
                    'error': f'API returned status {response.status_code}: {response.text}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Connection timeout - API may be unavailable'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Connection error - Check internet connection'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def generate_image(self, prompt: str, style: str = "professional", image_type: str = "general") -> Dict[str, Any]:
        """Generate a general image"""
        try:
            if not self.api_key:
                raise Exception("API key not configured")
            
            # Enhance prompt based on style and type
            enhanced_prompt = self._enhance_prompt(prompt, style, image_type)
            
            payload = {
                "text_prompts": [
                    {
                        "text": enhanced_prompt,
                        "weight": 1.0
                    }
                ],
                "cfg_scale": 7,
                "height": 512,
                "width": 512,
                "samples": 1,
                "steps": 30,
                "style_preset": self._get_style_preset(style)
            }
            
            response = requests.post(
                f"{self.base_url}/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('artifacts') and len(data['artifacts']) > 0:
                    image_base64 = data['artifacts'][0]['base64']
                    image_data_url = f"data:image/png;base64,{image_base64}"
                    
                    return {
                        'success': True,
                        'image_data': image_data_url,
                        'enhanced_prompt': enhanced_prompt
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No image generated'
                    }
            else:
                return {
                    'success': False,
                    'error': f'API error {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_business_poster(self, business_name: str, business_type: str, message: str, style: str = "professional") -> Dict[str, Any]:
        """Generate a business poster"""
        prompt = f"Professional business poster for {business_name}, a {business_type}. {message}. Clean layout, readable text, corporate design."
        return self.generate_image(prompt, style, "poster")
    
    def generate_product_image(self, product_name: str, product_description: str = "", style: str = "professional") -> Dict[str, Any]:
        """Generate a product image"""
        prompt = f"High-quality product photo of {product_name}. {product_description}. Professional lighting, clean background."
        return self.generate_image(prompt, style, "product")
    
    def generate_marketing_banner(self, business_name: str, message: str, style: str = "professional") -> Dict[str, Any]:
        """Generate a marketing banner"""
        prompt = f"Marketing banner for {business_name}. {message}. Eye-catching design, professional layout."
        return self.generate_image(prompt, style, "banner")
    
    def _enhance_prompt(self, prompt: str, style: str, image_type: str) -> str:
        """Enhance the prompt based on style and type"""
        style_modifiers = {
            "professional": "professional, clean, corporate, high-quality",
            "modern": "modern, sleek, contemporary, trendy",
            "creative": "creative, artistic, unique, innovative", 
            "minimal": "minimal, simple, clean, elegant",
            "vintage": "vintage, retro, classic, nostalgic"
        }
        
        type_modifiers = {
            "poster": "poster design, marketing material, professional layout",
            "product": "product photography, commercial quality, professional lighting",
            "banner": "banner design, marketing banner, promotional material",
            "general": "high-quality image"
        }
        
        enhanced = f"{prompt}, {style_modifiers.get(style, 'professional')}, {type_modifiers.get(image_type, 'high-quality image')}"
        return enhanced
    
    def _get_style_preset(self, style: str) -> Optional[str]:
        """Get Stability AI style preset based on our style"""
        style_mapping = {
            "professional": "photographic",
            "modern": "digital-art", 
            "creative": "comic-book",
            "minimal": "line-art",
            "vintage": "analog-film"
        }
        return style_mapping.get(style)