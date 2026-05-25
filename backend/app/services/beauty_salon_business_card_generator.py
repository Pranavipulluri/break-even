"""
Beauty Salon/Spa Business Card Generator - Creates beautiful spa-themed business cards
"""

import os
import qrcode
import logging
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import io
import base64

logger = logging.getLogger(__name__)

class BeautySalonBusinessCardGenerator:
    """Generate beautiful business cards for beauty salon staff"""
    
    def __init__(self):
        self.card_width = 1050  # 3.5 inches at 300 DPI
        self.card_height = 600  # 2 inches at 300 DPI
        self.margin = 50
        
        # Load fonts with fallbacks
        self.fonts = self._load_fonts()
        
        # Spa color palettes
        self.color_themes = {
            'spa_serenity': {
                'primary': '#8B9B9B',      # Soft sage
                'secondary': '#E8F4F8',    # Light spa blue
                'accent': '#D4AF37',       # Soft gold
                'text': '#2C3E3E',         # Deep teal
                'background': '#F5F9F9'    # Very light mint
            },
            'rose_gold_elegance': {
                'primary': '#E8B4B8',      # Rose gold
                'secondary': '#F4E6E7',    # Soft rose
                'accent': '#B8860B',       # Dark gold
                'text': '#4A2C2A',         # Deep brown
                'background': '#FDF8F9'    # Off white pink
            },
            'lavender_luxury': {
                'primary': '#C8A2C8',      # Soft lavender
                'secondary': '#F0E6F7',    # Light lavender
                'accent': '#8A2BE2',       # Deep purple
                'text': '#2E2E2E',         # Charcoal
                'background': '#F9F6FF'    # Very light purple
            },
            'mint_fresh': {
                'primary': '#98D8C8',      # Mint green
                'secondary': '#E8F7F4',    # Light mint
                'accent': '#FF69B4',       # Hot pink accent
                'text': '#2C5F54',         # Deep green
                'background': '#F7FDFC'    # Mint white
            },
            'coral_sunset': {
                'primary': '#FF7F7F',      # Coral
                'secondary': '#FFE4E1',    # Misty rose
                'accent': '#FFD700',       # Gold
                'text': '#8B4513',         # Saddle brown
                'background': '#FFF8F5'    # Seashell
            }
        }
    
    def _load_fonts(self):
        """Load fonts with fallbacks"""
        fonts = {}
        
        try:
            # Try to load professional fonts
            fonts['title'] = ImageFont.truetype("arial.ttf", 24)
            fonts['name'] = ImageFont.truetype("arial.ttf", 20)
            fonts['contact'] = ImageFont.truetype("arial.ttf", 14)
            fonts['small'] = ImageFont.truetype("arial.ttf", 12)
            fonts['services'] = ImageFont.truetype("arial.ttf", 13)
        except:
            # Fallback to default font
            try:
                fonts['title'] = ImageFont.load_default()
                fonts['name'] = ImageFont.load_default()
                fonts['contact'] = ImageFont.load_default()
                fonts['small'] = ImageFont.load_default()
                fonts['services'] = ImageFont.load_default()
            except:
                logger.warning("Could not load fonts, using minimal fallback")
                fonts = {key: None for key in ['title', 'name', 'contact', 'small', 'services']}
        
        return fonts
    
    def batch_generate_cards(self, salon_data: dict) -> dict:
        """Generate business cards for all staff members"""
        try:
            staff_members = salon_data.get('staff_members', [])
            design_style = salon_data.get('business_card_design', 'spa_serenity')
            
            generated_cards = []
            
            for staff in staff_members:
                card_result = self.generate_business_card(
                    salon_data=salon_data,
                    staff_data=staff,
                    design_style=design_style
                )
                
                if card_result.get('success'):
                    generated_cards.append(card_result)
                else:
                    logger.error(f"Failed to generate card for {staff.get('name', 'Unknown')}")
            
            return {
                "success": True,
                "cards": generated_cards,
                "design_style": design_style,
                "total_cards": len(generated_cards)
            }
            
        except Exception as e:
            logger.error(f"Error in batch card generation: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_business_card(self, salon_data: dict, staff_data: dict, design_style: str = 'spa_serenity') -> dict:
        """Generate a single business card"""
        try:
            # Create front and back cards
            front_card = self._create_spa_front_card(salon_data, staff_data, design_style)
            back_card = self._create_spa_back_card(salon_data, staff_data, design_style)
            
            # Generate QR code
            qr_code = self._generate_qr_code_for_spa(salon_data, staff_data)
            
            # Save cards
            salon_id = salon_data.get('salon_id', 'unknown')
            staff_name = staff_data.get('name', 'staff').lower().replace(' ', '_')
            timestamp = int(datetime.now().timestamp())
            
            front_filename = f"spa_card_front_{salon_id}_{staff_name}_{timestamp}.png"
            back_filename = f"spa_card_back_{salon_id}_{staff_name}_{timestamp}.png"
            
            os.makedirs("static/business_cards", exist_ok=True)
            
            front_path = os.path.join("static", "business_cards", front_filename)
            back_path = os.path.join("static", "business_cards", back_filename)
            
            front_card.save(front_path, "PNG", quality=95, optimize=True)
            back_card.save(back_path, "PNG", quality=95, optimize=True)
            
            logger.info(f"Spa business cards saved: {front_path}, {back_path}")
            
            return {
                "success": True,
                "front_image": f"/static/business_cards/{front_filename}",
                "back_image": f"/static/business_cards/{back_filename}",
                "front_image_path": front_path,
                "back_image_path": back_path,
                "qr_code_included": True,
                "design_style": design_style,
                "staff_name": staff_data.get('name'),
                "card_theme": design_style
            }
            
        except Exception as e:
            logger.error(f"Error generating spa business card: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_spa_front_card(self, salon_data: dict, staff_data: dict, design_style: str) -> Image:
        """Create beautiful spa-themed front card"""
        
        # Create card with spa background
        card = Image.new('RGB', (self.card_width, self.card_height), '#FFFFFF')
        draw = ImageDraw.Draw(card)
        
        colors = self.color_themes.get(design_style, self.color_themes['spa_serenity'])
        
        # Beautiful gradient background
        self._draw_spa_gradient(draw, colors)
        
        # Elegant border design
        self._draw_spa_border(draw, colors)
        
        # Salon name (elegant header)
        salon_name = salon_data.get('salon_name', 'Beauty Salon')
        draw.text((self.card_width//2, 80), salon_name, 
                 font=self.fonts['title'], fill=colors['text'], anchor='mm')
        
        # Elegant separator line
        line_y = 120
        draw.line([(150, line_y), (self.card_width-150, line_y)], 
                 fill=colors['accent'], width=2)
        
        # Staff name (prominent)
        staff_name = staff_data.get('name', 'Staff Member')
        draw.text((self.card_width//2, 180), staff_name, 
                 font=self.fonts['name'], fill=colors['primary'], anchor='mm')
        
        # Title/specialization
        title = staff_data.get('title', 'Beauty Specialist')
        draw.text((self.card_width//2, 210), title, 
                 font=self.fonts['contact'], fill=colors['text'], anchor='mm')
        
        # Specializations (in elegant format)
        specializations = staff_data.get('specializations', [])
        if specializations:
            spec_text = ' • '.join(specializations[:3])  # Max 3 specializations
            draw.text((self.card_width//2, 240), spec_text, 
                     font=self.fonts['small'], fill=colors['primary'], anchor='mm')
        
        # Contact information (elegant layout)
        contact_y = 300
        phone = salon_data.get('phone_number', '')
        email = salon_data.get('email_address', '')
        
        if phone:
            draw.text((self.card_width//2, contact_y), f"📞 {phone}", 
                     font=self.fonts['contact'], fill=colors['text'], anchor='mm')
            contact_y += 25
        
        if email:
            draw.text((self.card_width//2, contact_y), f"✉ {email}", 
                     font=self.fonts['contact'], fill=colors['text'], anchor='mm')
        
        # Spa decorative elements
        self._add_spa_decorations(draw, colors)
        
        return card
    
    def _create_spa_back_card(self, salon_data: dict, staff_data: dict, design_style: str) -> Image:
        """Create beautiful spa-themed back card with services and QR code"""
        
        card = Image.new('RGB', (self.card_width, self.card_height), '#FFFFFF')
        draw = ImageDraw.Draw(card)
        
        colors = self.color_themes.get(design_style, self.color_themes['spa_serenity'])
        
        # Background
        self._draw_spa_gradient(draw, colors, reverse=True)
        self._draw_spa_border(draw, colors)
        
        # Services header
        draw.text((self.card_width//2, 80), "Our Services", 
                 font=self.fonts['title'], fill=colors['text'], anchor='mm')
        
        # Services list (beautiful formatting)
        services = salon_data.get('services', [
            'Hair Styling', 'Facial Treatments', 'Massage Therapy', 
            'Nail Care', 'Spa Packages', 'Skincare'
        ])
        
        services_y = 140
        max_services = 8  # Limit to fit nicely
        
        for i, service in enumerate(services[:max_services]):
            if i < 4:
                # Left column
                x_pos = self.card_width//4
                y_pos = services_y + (i * 25)
            else:
                # Right column
                x_pos = (self.card_width//4) * 3
                y_pos = services_y + ((i-4) * 25)
            
            draw.text((x_pos, y_pos), f"• {service}", 
                     font=self.fonts['services'], fill=colors['text'], anchor='mm')
        
        # QR Code
        qr_image = self._generate_qr_code_for_spa(salon_data, staff_data)
        if qr_image:
            qr_size = 120
            qr_x = self.card_width - qr_size - 50
            qr_y = self.card_height - qr_size - 50
            
            qr_resized = qr_image.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            card.paste(qr_resized, (qr_x, qr_y))
            
            # QR code label
            draw.text((qr_x + qr_size//2, qr_y + qr_size + 15), "Book Online", 
                     font=self.fonts['small'], fill=colors['text'], anchor='mm')
        
        # Address
        address = salon_data.get('address', '')
        if address:
            draw.text((80, self.card_height - 80), f"📍 {address}", 
                     font=self.fonts['small'], fill=colors['text'])
        
        # Hours or additional info
        draw.text((80, self.card_height - 55), "Visit us for a relaxing experience", 
                 font=self.fonts['small'], fill=colors['primary'])
        
        return card
    
    def _draw_spa_gradient(self, draw: ImageDraw, colors: dict, reverse: bool = False):
        """Draw beautiful spa gradient background"""
        primary = colors['primary'] if not reverse else colors['secondary']
        secondary = colors['secondary'] if not reverse else colors['primary']
        
        # Create subtle gradient effect
        for i in range(self.card_height):
            ratio = i / self.card_height
            # Simple gradient approximation
            if i < self.card_height // 3:
                color = primary
            elif i > (self.card_height * 2) // 3:
                color = secondary
            else:
                color = colors['background']
            
            if i % 10 == 0:  # Draw every 10th line for performance
                draw.line([(0, i), (self.card_width, i)], fill=color, width=10)
    
    def _draw_spa_border(self, draw: ImageDraw, colors: dict):
        """Draw elegant spa border"""
        border_width = 3
        accent_color = colors['accent']
        
        # Main border
        draw.rectangle([0, 0, self.card_width-1, self.card_height-1], 
                      outline=accent_color, width=border_width)
        
        # Inner decorative border
        inner_margin = 15
        draw.rectangle([inner_margin, inner_margin, 
                       self.card_width-inner_margin-1, self.card_height-inner_margin-1], 
                      outline=colors['primary'], width=1)
    
    def _add_spa_decorations(self, draw: ImageDraw, colors: dict):
        """Add decorative spa elements"""
        # Corner decorations (simple geometric patterns)
        accent = colors['accent']
        
        # Top corners
        for x in range(20, 60, 10):
            draw.ellipse([x, 20, x+5, 25], fill=accent)
            draw.ellipse([self.card_width-x-5, 20, self.card_width-x, 25], fill=accent)
        
        # Bottom corners
        for x in range(20, 60, 10):
            draw.ellipse([x, self.card_height-25, x+5, self.card_height-20], fill=accent)
            draw.ellipse([self.card_width-x-5, self.card_height-25, self.card_width-x, self.card_height-20], fill=accent)
    
    def _generate_qr_code_for_spa(self, salon_data: dict, staff_data: dict) -> Image:
        """Generate QR code for spa booking"""
        try:
            # Create spa booking vCard format
            salon_name = salon_data.get('salon_name', 'Beauty Salon')
            staff_name = staff_data.get('name', 'Staff Member')
            phone = salon_data.get('phone_number', '')
            email = salon_data.get('email_address', '')
            address = salon_data.get('address', '')
            
            # Extract service names from service dictionaries
            services_list = salon_data.get('services', [])
            service_names = []
            for service in services_list[:3]:  # Take first 3 services
                if isinstance(service, dict):
                    service_names.append(service.get('name', 'Service'))
                else:
                    service_names.append(str(service))
            services = ', '.join(service_names)
            
            # Create vCard content for spa
            vcard_content = f"""BEGIN:VCARD
VERSION:3.0
FN:{staff_name}
ORG:{salon_name}
TITLE:Beauty Specialist
EMAIL:{email}
TEL:{phone}
ADR:;;{address};;;
URL:
NOTE:Services: {services}
END:VCARD"""
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(vcard_content)
            qr.make(fit=True)
            
            qr_image = qr.make_image(fill_color='black', back_color='white')
            
            return qr_image
            
        except Exception as e:
            logger.error(f"Error generating QR code for spa: {e}")
            return None