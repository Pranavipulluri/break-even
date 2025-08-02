"""
Stability AI Service for Break-even App
Provides AI-powered image and poster generation using Stability AI
"""

import requests
import base64
import io
from PIL import Image
from flask import current_app
import os
from datetime import datetime

class StabilityAIService:
    
    def __init__(self, api_key=None):
        self._api_key = api_key
        self.base_url = "https://api.stability.ai/v1"
        self.engine_id = "stable-diffusion-xl-1024-v1-0"  # Latest SDXL model
    
    @property
    def api_key(self):
        if self._api_key:
            return self._api_key
        try:
            from flask import current_app
            return current_app.config.get('STABILITY_API_KEY')
        except RuntimeError:
            # Fallback when outside application context
            return 'sk-Ci8STOuJz4ZE1xGzmQXFDoykscMoNFoD4OCQZr5BlWgd83O2'
    
    def generate_business_poster(self, business_name, business_type, style="professional", additional_text=""):
        """Generate a professional business poster"""
        try:
            # Craft detailed prompt for business poster
            prompt = self._create_business_poster_prompt(business_name, business_type, style, additional_text)
            
            print(f"🎨 Generating business poster for: {business_name}")
            print(f"📝 Prompt: {prompt}")
            
            return self._generate_image(
                prompt=prompt,
                width=1024,
                height=1024,
                steps=30,
                cfg_scale=7,
                samples=1
            )
            
        except Exception as e:
            print(f"❌ Error generating business poster: {e}")
            return {
                'success': False,
                'error': f'Failed to generate business poster: {str(e)}'
            }
    
    def generate_product_image(self, product_name, product_description, style="high-quality product photo"):
        """Generate product images for businesses"""
        try:
            # Craft prompt for product photography
            prompt = f"Professional {style} of {product_name}, {product_description}, studio lighting, white background, commercial photography, high resolution, detailed, photorealistic"
            
            print(f"📸 Generating product image for: {product_name}")
            print(f"📝 Prompt: {prompt}")
            
            return self._generate_image(
                prompt=prompt,
                width=1024,
                height=1024,
                steps=25,
                cfg_scale=7,
                samples=1
            )
            
        except Exception as e:
            print(f"❌ Error generating product image: {e}")
            return {
                'success': False,
                'error': f'Failed to generate product image: {str(e)}'
            }
    
    def generate_marketing_banner(self, business_name, message, dimensions="banner", style="modern"):
        """Generate marketing banners and promotional images"""
        try:
            # Set dimensions based on banner type
            width, height = self._get_banner_dimensions(dimensions)
            
            # Craft prompt for marketing banner
            prompt = f"{style} marketing banner for '{business_name}', featuring '{message}', professional design, eye-catching colors, clean typography, commercial quality, no text overlay needed"
            
            print(f"🎯 Generating marketing banner for: {business_name}")
            print(f"📐 Dimensions: {width}x{height}")
            print(f"📝 Prompt: {prompt}")
            
            return self._generate_image(
                prompt=prompt,
                width=width,
                height=height,
                steps=30,
                cfg_scale=7,
                samples=1
            )
            
        except Exception as e:
            print(f"❌ Error generating marketing banner: {e}")
            return {
                'success': False,
                'error': f'Failed to generate marketing banner: {str(e)}'
            }
    
    def generate_website_hero_image(self, business_name, business_type, mood="professional and welcoming"):
        """Generate hero images for websites"""
        try:
            # Craft prompt for website hero image
            prompt = f"Website hero image for {business_name}, a {business_type} business, {mood} atmosphere, modern web design, high quality, professional photography style, suitable for website header"
            
            print(f"🌟 Generating hero image for: {business_name}")
            print(f"📝 Prompt: {prompt}")
            
            return self._generate_image(
                prompt=prompt,
                width=1344,  # Wide format for hero images
                height=768,
                steps=30,
                cfg_scale=7,
                samples=1
            )
            
        except Exception as e:
            print(f"❌ Error generating hero image: {e}")
            return {
                'success': False,
                'error': f'Failed to generate hero image: {str(e)}'
            }
    
    def _generate_image(self, prompt, width=1024, height=1024, steps=30, cfg_scale=7, samples=1):
        """Internal method to generate images via Stability AI API"""
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            body = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1
                    }
                ],
                "cfg_scale": cfg_scale,
                "height": height,
                "width": width,
                "samples": samples,
                "steps": steps,
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/generation/{self.engine_id}/text-to-image",
                headers=headers,
                json=body
            )
            
            if response.status_code != 200:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return {
                    'success': False,
                    'error': f'API request failed: {response.status_code} - {response.text}'
                }
            
            data = response.json()
            
            # Process the generated images
            images = []
            for i, image in enumerate(data["artifacts"]):
                # Decode base64 image
                image_data = base64.b64decode(image["base64"])
                
                # Save image to uploads directory
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"stability_ai_{timestamp}_{i}.png"
                
                # Create uploads directory if it doesn't exist
                uploads_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    'uploads'
                )
                os.makedirs(uploads_dir, exist_ok=True)
                
                filepath = os.path.join(uploads_dir, filename)
                
                # Save image
                with open(filepath, "wb") as f:
                    f.write(image_data)
                
                images.append({
                    'filename': filename,
                    'filepath': filepath,
                    'url': f'/uploads/{filename}',
                    'size': f"{width}x{height}"
                })
                
                print(f"✅ Image saved: {filename}")
            
            return {
                'success': True,
                'images': images,
                'prompt': prompt,
                'dimensions': f"{width}x{height}",
                'model': self.engine_id
            }
            
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return {
                'success': False,
                'error': f'Image generation failed: {str(e)}'
            }
    
    def _create_business_poster_prompt(self, business_name, business_type, style, additional_text):
        """Create detailed prompt for business poster generation"""
        
        style_prompts = {
            "professional": "clean, professional business poster design, corporate style, modern typography",
            "creative": "creative and artistic business poster, unique design elements, vibrant colors",
            "minimal": "minimalist business poster design, clean lines, simple elegant layout",
            "vintage": "vintage-style business poster, retro design elements, classic typography",
            "modern": "modern business poster design, contemporary style, sleek and stylish"
        }
        
        base_prompt = f"Professional business poster for '{business_name}', a {business_type} business"
        style_desc = style_prompts.get(style, style_prompts["professional"])
        
        prompt = f"{base_prompt}, {style_desc}, high quality design, commercial poster, no text overlay needed"
        
        if additional_text:
            prompt += f", incorporating theme: {additional_text}"
        
        return prompt
    
    def _get_banner_dimensions(self, banner_type):
        """Get appropriate dimensions for different banner types"""
        dimensions = {
            "banner": (1344, 448),      # 3:1 ratio - web banner
            "social": (1200, 630),      # Social media post
            "facebook": (1200, 630),    # Facebook post
            "instagram": (1080, 1080),  # Instagram square
            "twitter": (1200, 600),     # Twitter header
            "linkedin": (1200, 627),    # LinkedIn post
            "wide": (1920, 1080),       # Wide screen
            "square": (1024, 1024)      # Square format
        }
        
        return dimensions.get(banner_type, dimensions["banner"])
    
    def get_account_info(self):
        """Get Stability AI account information and credits"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.get(
                f"{self.base_url}/user/account",
                headers=headers
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'account': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to get account info: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Account info error: {str(e)}'
            }
    
    def list_engines(self):
        """List available Stability AI engines/models"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.get(
                f"{self.base_url}/engines/list",
                headers=headers
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'engines': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to list engines: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Engines list error: {str(e)}'
            }
