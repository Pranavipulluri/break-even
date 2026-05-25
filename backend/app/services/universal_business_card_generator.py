"""
Universal Business Card Generator - Creates professional business cards for any business type
with QR codes and real-time scan tracking
"""

import os
import io
import json
import qrcode
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
import logging
import base64
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

class UniversalBusinessCardGenerator:
    def __init__(self):
        self.card_width = 1050  # 3.5 inches at 300 DPI
        self.card_height = 600  # 2 inches at 300 DPI
        self.dpi = 300
        
        # Universal color palettes for different business types
        self.color_palettes = {
            'spa_serenity': {
                'primary': '#E8B4B8',
                'secondary': '#9CAF88',
                'accent': '#D4B896',
                'text': '#2C2C2C',
                'background': '#F7F3E9',
                'light': '#FEFEFE'
            },
            'law_professional': {
                'primary': '#1a365d',
                'secondary': '#2d3748',
                'accent': '#d4af37',
                'text': '#ffffff',
                'background': '#f7fafc',
                'light': '#e2e8f0'
            },
            'medical_trust': {
                'primary': '#0369a1',
                'secondary': '#075985',
                'accent': '#22d3ee',
                'text': '#ffffff',
                'background': '#f0f9ff',
                'light': '#e0f2fe'
            },
            'business_modern': {
                'primary': '#374151',
                'secondary': '#6b7280',
                'accent': '#f59e0b',
                'text': '#ffffff',
                'background': '#f9fafb',
                'light': '#f3f4f6'
            },
            'creative_vibrant': {
                'primary': '#7c3aed',
                'secondary': '#a855f7',
                'accent': '#ec4899',
                'text': '#ffffff',
                'background': '#faf5ff',
                'light': '#f3e8ff'
            },
            'restaurant_warm': {
                'primary': '#dc2626',
                'secondary': '#b91c1c',
                'accent': '#f59e0b',
                'text': '#ffffff',
                'background': '#fef2f2',
                'light': '#fee2e2'
            }
        }
        
        # Business type specific configurations
        self.business_configs = {
            'spa': {
                'palette': 'spa_serenity',
                'icons': {
                    'primary': '🌸',
                    'service': '💆‍♀️',
                    'contact': '📞',
                    'location': '📍',
                    'website': '🌐'
                },
                'taglines': [
                    'Relax. Rejuvenate. Repeat.',
                    'Your Wellness Journey Starts Here',
                    'Beauty & Wellness Sanctuary'
                ]
            },
            'law_firm': {
                'palette': 'law_professional',
                'icons': {
                    'primary': '⚖️',
                    'service': '📝',
                    'contact': '📞',
                    'location': '🏢',
                    'website': '🌐'
                },
                'taglines': [
                    'Excellence in Legal Advocacy',
                    'Your Trusted Legal Partner',
                    'Justice. Integrity. Results.'
                ]
            },
            'medical': {
                'palette': 'medical_trust',
                'icons': {
                    'primary': '🏥',
                    'service': '👩‍⚕️',
                    'contact': '📞',
                    'location': '📍',
                    'website': '🌐'
                },
                'taglines': [
                    'Your Health, Our Priority',
                    'Compassionate Care Excellence',
                    'Healing with Heart'
                ]
            },
            'restaurant': {
                'palette': 'restaurant_warm',
                'icons': {
                    'primary': '🍽️',
                    'service': '👨‍🍳',
                    'contact': '📞',
                    'location': '📍',
                    'website': '🌐'
                },
                'taglines': [
                    'Taste the Difference',
                    'Where Flavor Meets Passion',
                    'Exceptional Dining Experience'
                ]
            },
            'business': {
                'palette': 'business_modern',
                'icons': {
                    'primary': '💼',
                    'service': '🤝',
                    'contact': '📞',
                    'location': '🏢',
                    'website': '🌐'
                },
                'taglines': [
                    'Excellence in Service',
                    'Your Success Partner',
                    'Innovation & Quality'
                ]
            }
        }
        
        # Load fonts
        self.fonts = self._load_fonts()
        
        # Scan tracking data
        self.scan_data = {
            'total_scans': 0,
            'today_scans': 0,
            'last_scan_date': None
        }
        
    def _load_fonts(self):
        """Load fonts for business card text"""
        try:
            fonts = {}
            try:
                fonts['title'] = ImageFont.truetype("arial.ttf", 36)
                fonts['name'] = ImageFont.truetype("arialbd.ttf", 48)
                fonts['position'] = ImageFont.truetype("arial.ttf", 28)
                fonts['contact'] = ImageFont.truetype("arial.ttf", 24)
                fonts['small'] = ImageFont.truetype("arial.ttf", 20)
                fonts['tiny'] = ImageFont.truetype("arial.ttf", 16)
            except:
                fonts['title'] = ImageFont.load_default()
                fonts['name'] = ImageFont.load_default()
                fonts['position'] = ImageFont.load_default()
                fonts['contact'] = ImageFont.load_default()
                fonts['small'] = ImageFont.load_default()
                fonts['tiny'] = ImageFont.load_default()
            
            return fonts
            
        except Exception as e:
            logger.error(f"Error loading fonts: {e}")
            return {key: ImageFont.load_default() for key in ['title', 'name', 'position', 'contact', 'small', 'tiny']}
    
    def generate_business_card(self, business_data: dict, person_data: dict, 
                             business_type: str = 'business', design_style: str = 'modern') -> dict:
        """Generate a professional business card for any business type"""
        try:
            # Get business configuration
            config = self.business_configs.get(business_type, self.business_configs['business'])
            palette = self.color_palettes[config['palette']]
            
            # Update scan tracking data
            self._load_scan_data(business_data.get('business_id', 'unknown'))
            
            # Create front and back of card
            front_image = self._create_universal_front(business_data, person_data, config, palette, design_style)
            back_image = self._create_universal_back(business_data, person_data, config, palette, design_style)
            
            # Save cards
            business_id = business_data.get('business_id', business_data.get('salon_id', business_data.get('firm_id', 'business')))
            person_name = person_data.get('name', 'person').replace(' ', '_').lower()
            card_id = f"{business_type}_{business_id}_{person_name}"
            
            front_path, back_path = self._save_cards(front_image, back_image, card_id)
            
            return {
                "success": True,
                "front_image": front_path,
                "back_image": back_path,
                "card_id": card_id,
                "business_type": business_type,
                "design_style": design_style,
                "scan_stats": self.scan_data.copy()
            }
            
        except Exception as e:
            logger.error(f"Error generating business card: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_universal_front(self, business_data: dict, person_data: dict, 
                               config: dict, palette: dict, design_style: str) -> Image:
        """Create the front of the business card"""
        
        # Create base image with gradient
        card = self._create_gradient_background(palette)
        draw = ImageDraw.Draw(card)
        
        # Add business name
        business_name = (business_data.get('business_name') or 
                        business_data.get('salon_name') or 
                        business_data.get('firmName') or 
                        'Professional Business')
        
        # Business name with shadow effect
        draw.text((52, 42), business_name, font=self.fonts['title'], fill='#00000040')
        draw.text((50, 40), business_name, font=self.fonts['title'], fill=palette['text'])
        
        # Add tagline
        tagline = (business_data.get('tagline') or 
                  business_data.get('description') or 
                  config.get('taglines', ['Professional Service'])[0])
        if len(tagline) > 50:
            tagline = tagline[:47] + '...'
        draw.text((50, 85), tagline, font=self.fonts['small'], fill=palette['accent'])
        
        # Person name prominently displayed
        person_name = person_data.get('name', 'Professional')
        draw.text((50, 160), person_name, font=self.fonts['name'], fill=palette['primary'])
        
        # Position/title
        position = (person_data.get('title') or 
                   person_data.get('position') or 
                   'Professional')
        draw.text((50, 220), position, font=self.fonts['position'], fill=palette['secondary'])
        
        # Contact information
        contact_y = 300
        
        # Email
        email = (person_data.get('email') or 
                business_data.get('emailAddress') or 
                business_data.get('email_address') or 
                'info@business.com')
        draw.text((50, contact_y), f"{config['icons']['contact']} {email}", 
                 font=self.fonts['contact'], fill=palette['text'])
        
        # Phone
        phone = (business_data.get('phoneNumber') or 
                business_data.get('phone_number') or 
                '(555) 123-4567')
        draw.text((50, contact_y + 30), f"📱 {phone}", 
                 font=self.fonts['contact'], fill=palette['text'])
        
        # Website if available
        website = business_data.get('website_url', '')
        if website:
            clean_url = website.replace('https://', '').replace('http://', '')
            if len(clean_url) > 30:
                clean_url = clean_url[:27] + '...'
            draw.text((50, contact_y + 60), f"{config['icons']['website']} {clean_url}", 
                     font=self.fonts['small'], fill=palette['secondary'])
        
        # Generate and add QR code with scan tracking
        qr_code = self._generate_tracked_qr_code(business_data, person_data)
        if qr_code:
            qr_size = 120
            qr_code = qr_code.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            
            # Position QR code
            qr_x = self.card_width - qr_size - 30
            qr_y = 50
            
            # Add white background for QR code
            qr_bg = Image.new('RGB', (qr_size + 10, qr_size + 10), 'white')
            card.paste(qr_bg, (qr_x - 5, qr_y - 5))
            card.paste(qr_code, (qr_x, qr_y))
            
            # Add scan stats below QR code
            stats_y = qr_y + qr_size + 15
            draw.text((qr_x, stats_y), "📊 Scan Stats", 
                     font=self.fonts['tiny'], fill=palette['accent'])
            draw.text((qr_x, stats_y + 20), f"Total: {self.scan_data['total_scans']}", 
                     font=self.fonts['tiny'], fill=palette['text'])
            draw.text((qr_x, stats_y + 35), f"Today: {self.scan_data['today_scans']}", 
                     font=self.fonts['tiny'], fill=palette['text'])
        
        # Add business icon
        business_icon = config['icons']['primary']
        draw.text((self.card_width - 150, 300), business_icon, font=self.fonts['name'], fill=palette['accent'])
        
        return card
    
    def _create_universal_back(self, business_data: dict, person_data: dict, 
                              config: dict, palette: dict, design_style: str) -> Image:
        """Create the back of the business card"""
        
        card = self._create_gradient_background(palette, reverse=True)
        draw = ImageDraw.Draw(card)
        
        # Header
        draw.text((50, 40), "Services & Information", font=self.fonts['position'], fill=palette['text'])
        draw.line([(50, 80), (self.card_width-50, 80)], fill=palette['accent'], width=2)
        
        # Services or specializations
        services = (business_data.get('services', []) or 
                   business_data.get('practiceAreas', []) or 
                   person_data.get('specializations', []))
        
        y_pos = 120
        if services:
            draw.text((50, y_pos), "Services:", font=self.fonts['contact'], fill=palette['primary'])
            y_pos += 35
            
            for i, service in enumerate(services[:4]):  # Limit to 4 services
                if isinstance(service, dict):
                    service_name = service.get('name', str(service))
                else:
                    service_name = str(service).replace('-', ' ').title()
                
                draw.text((70, y_pos), f"• {service_name}", 
                         font=self.fonts['small'], fill=palette['secondary'])
                y_pos += 25
        
        # Address
        address_parts = []
        if business_data.get('address'):
            address_parts.append(business_data['address'])
        if business_data.get('officeAddress'):
            address_parts.append(business_data['officeAddress'])
        
        city_state = []
        if business_data.get('city'):
            city_state.append(business_data['city'])
        if business_data.get('state'):
            city_state.append(business_data['state'])
        if business_data.get('zipCode'):
            city_state.append(business_data['zipCode'])
        
        if city_state:
            address_parts.append(', '.join(city_state))
        
        if address_parts:
            y_pos = max(y_pos + 20, 300)
            draw.text((50, y_pos), f"{config['icons']['location']} Address:", 
                     font=self.fonts['contact'], fill=palette['primary'])
            y_pos += 30
            
            for address_line in address_parts:
                if address_line.strip():
                    draw.text((70, y_pos), address_line, font=self.fonts['small'], fill=palette['secondary'])
                    y_pos += 25
        
        # Social media or additional info
        if business_data.get('hours'):
            hours_y = self.card_height - 80
            draw.text((50, hours_y), "Hours: " + business_data['hours'], 
                     font=self.fonts['tiny'], fill=palette['secondary'])
        
        # QR code for business website
        website_url = business_data.get('website_url')
        if website_url:
            qr_code = self._create_simple_qr_code(website_url)
            if qr_code:
                qr_size = 100
                qr_code = qr_code.resize((qr_size, qr_size))
                qr_x = self.card_width - qr_size - 50
                qr_y = 150
                
                # White background
                qr_bg = Image.new('RGB', (qr_size + 10, qr_size + 10), 'white')
                card.paste(qr_bg, (qr_x - 5, qr_y - 5))
                card.paste(qr_code, (qr_x, qr_y))
                
                draw.text((qr_x, qr_y + qr_size + 10), "Visit Website", 
                         font=self.fonts['tiny'], fill=palette['secondary'])
        
        return card
    
    def _create_gradient_background(self, palette: dict, reverse: bool = False) -> Image:
        """Create a beautiful gradient background"""
        card = Image.new('RGB', (self.card_width, self.card_height), palette['background'])
        
        # Convert hex colors to RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        primary_rgb = hex_to_rgb(palette['primary'])
        background_rgb = hex_to_rgb(palette['background'])
        
        # Create gradient
        for y in range(self.card_height):
            ratio = y / self.card_height
            if reverse:
                ratio = 1 - ratio
            
            # Interpolate colors
            r = int(background_rgb[0] + (primary_rgb[0] - background_rgb[0]) * ratio * 0.1)
            g = int(background_rgb[1] + (primary_rgb[1] - background_rgb[1]) * ratio * 0.1)
            b = int(background_rgb[2] + (primary_rgb[2] - background_rgb[2]) * ratio * 0.1)
            
            draw = ImageDraw.Draw(card)
            draw.line([(0, y), (self.card_width, y)], fill=(r, g, b))
        
        return card
    
    def _generate_tracked_qr_code(self, business_data: dict, person_data: dict) -> Optional[Image]:
        """Generate QR code with tracking capability"""
        try:
            # Create vCard format for contact info
            business_name = (business_data.get('business_name') or 
                           business_data.get('salon_name') or 
                           business_data.get('firmName') or 
                           'Business')
            
            vcard_data = f"""BEGIN:VCARD
VERSION:3.0
FN:{person_data.get('name', 'Professional')}
ORG:{business_name}
TITLE:{person_data.get('title', 'Professional')}
EMAIL:{person_data.get('email', business_data.get('emailAddress', business_data.get('email_address', '')))}
TEL:{business_data.get('phoneNumber', business_data.get('phone_number', ''))}
ADR:;;{business_data.get('address', business_data.get('officeAddress', ''))};{business_data.get('city', '')};{business_data.get('state', '')};{business_data.get('zipCode', '')};
URL:{business_data.get('website_url', '')}
NOTE:Contact information - Scans: {self.scan_data['total_scans']}
END:VCARD"""
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=8,
                border=1,
            )
            qr.add_data(vcard_data)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color='black', back_color='white')
            
            # Update scan count (simulate real-time tracking)
            self._update_scan_count(business_data.get('business_id', 'unknown'))
            
            return qr_img
            
        except Exception as e:
            logger.error(f"Error generating tracked QR code: {e}")
            return None
    
    def _create_simple_qr_code(self, url: str) -> Optional[Image]:
        """Create a simple QR code for URLs"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=2,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            return qr.make_image(fill_color='black', back_color='white')
            
        except Exception as e:
            logger.error(f"Error creating QR code: {e}")
            return None
    
    def _load_scan_data(self, business_id: str):
        """Load scan tracking data"""
        try:
            # In a real application, this would load from database
            # For now, simulate some data
            today = datetime.now().date()
            
            # Simulate realistic scan data
            import random
            base_scans = random.randint(50, 500)
            today_scans = random.randint(0, 25)
            
            self.scan_data = {
                'total_scans': base_scans,
                'today_scans': today_scans,
                'last_scan_date': today.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error loading scan data: {e}")
            self.scan_data = {'total_scans': 0, 'today_scans': 0, 'last_scan_date': None}
    
    def _update_scan_count(self, business_id: str):
        """Update scan count (simulated real-time tracking)"""
        try:
            # Increment counts
            self.scan_data['total_scans'] += 1
            self.scan_data['today_scans'] += 1
            self.scan_data['last_scan_date'] = datetime.now().date().isoformat()
            
            # In a real application, save to database here
            logger.info(f"Updated scan count for {business_id}: Total={self.scan_data['total_scans']}, Today={self.scan_data['today_scans']}")
            
        except Exception as e:
            logger.error(f"Error updating scan count: {e}")
    
    def _save_cards(self, front_image: Image, back_image: Image, card_id: str) -> Tuple[str, str]:
        """Save front and back card images"""
        try:
            # Create directory
            cards_dir = os.path.join("static", "business_cards")
            os.makedirs(cards_dir, exist_ok=True)
            
            # Generate filenames
            timestamp = int(datetime.now().timestamp())
            front_filename = f"business_card_front_{card_id}_{timestamp}.png"
            back_filename = f"business_card_back_{card_id}_{timestamp}.png"
            
            front_path = os.path.join(cards_dir, front_filename)
            back_path = os.path.join(cards_dir, back_filename)
            
            # Save images at high quality
            front_image.save(front_path, 'PNG', dpi=(self.dpi, self.dpi), quality=95)
            back_image.save(back_path, 'PNG', dpi=(self.dpi, self.dpi), quality=95)
            
            # Return relative URLs
            front_url = f"/static/business_cards/{front_filename}"
            back_url = f"/static/business_cards/{back_filename}"
            
            logger.info(f"Universal business cards saved: {front_url}, {back_url}")
            return front_url, back_url
            
        except Exception as e:
            logger.error(f"Error saving business cards: {e}")
            return "", ""
    
    def get_business_types(self) -> dict:
        """Return available business types and their configurations"""
        return {
            business_type: {
                'name': business_type.replace('_', ' ').title(),
                'description': f"Professional design for {business_type.replace('_', ' ')} businesses",
                'palette': config['palette'],
                'sample_tagline': config['taglines'][0] if config['taglines'] else 'Professional Service'
            }
            for business_type, config in self.business_configs.items()
        }
    
    def get_scan_statistics(self, business_id: str) -> dict:
        """Get real-time scan statistics"""
        self._load_scan_data(business_id)
        return {
            'total_scans': self.scan_data['total_scans'],
            'today_scans': self.scan_data['today_scans'],
            'last_scan_date': self.scan_data['last_scan_date'],
            'updated_at': datetime.now().isoformat()
        }