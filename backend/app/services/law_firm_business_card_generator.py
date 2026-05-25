"""
Business Card Generator for Law Firms - Creates professional business cards with QR codes
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

logger = logging.getLogger(__name__)

class LawFirmBusinessCardGenerator:
    def __init__(self):
        self.card_width = 1050  # 3.5 inches at 300 DPI
        self.card_height = 600  # 2 inches at 300 DPI
        self.dpi = 300
        
        # Color palettes for professional law firm designs
        self.color_palettes = {
            'classic_navy': {
                'primary': '#1a365d',
                'secondary': '#2d3748',
                'accent': '#d4af37',
                'text': '#ffffff',
                'background': '#f7fafc'
            },
            'professional_gray': {
                'primary': '#2d3748',
                'secondary': '#4a5568',
                'accent': '#e53e3e',
                'text': '#ffffff',
                'background': '#edf2f7'
            },
            'burgundy_gold': {
                'primary': '#7c2d12',
                'secondary': '#92400e',
                'accent': '#d4af37',
                'text': '#ffffff',
                'background': '#fef5e7'
            },
            'forest_green': {
                'primary': '#065f46',
                'secondary': '#064e3b',
                'accent': '#a3a3a3',
                'text': '#ffffff',
                'background': '#ecfdf5'
            },
            'modern_black': {
                'primary': '#0f172a',
                'secondary': '#1e293b',
                'accent': '#60a5fa',
                'text': '#ffffff',
                'background': '#f8fafc'
            }
        }
        
        # Load default fonts
        self.fonts = self._load_fonts()
    
    def _load_fonts(self):
        """Load fonts for business card text"""
        try:
            fonts = {}
            
            # Try to load system fonts
            try:
                fonts['title'] = ImageFont.truetype("arial.ttf", 36)
                fonts['name'] = ImageFont.truetype("arialbd.ttf", 48)
                fonts['position'] = ImageFont.truetype("arial.ttf", 28)
                fonts['contact'] = ImageFont.truetype("arial.ttf", 24)
                fonts['small'] = ImageFont.truetype("arial.ttf", 20)
            except:
                # Fallback to default font
                fonts['title'] = ImageFont.load_default()
                fonts['name'] = ImageFont.load_default()
                fonts['position'] = ImageFont.load_default()
                fonts['contact'] = ImageFont.load_default()
                fonts['small'] = ImageFont.load_default()
            
            return fonts
            
        except Exception as e:
            logger.error(f"Error loading fonts: {e}")
            return {
                'title': ImageFont.load_default(),
                'name': ImageFont.load_default(),
                'position': ImageFont.load_default(),
                'contact': ImageFont.load_default(),
                'small': ImageFont.load_default()
            }
    
    def generate_business_card(self, firm_data: dict, attorney_data: dict, design_style: str = 'classic_navy') -> dict:
        """Generate a professional business card for an attorney"""
        try:
            # Get color palette
            palette = self.color_palettes.get(design_style, self.color_palettes['classic_navy'])
            
            # Create front and back of card
            front_image = self._create_card_front(firm_data, attorney_data, palette, design_style)
            back_image = self._create_card_back(firm_data, attorney_data, palette, design_style)
            
            # Save cards
            card_id = f"{firm_data.get('firm_id', 'law_firm')}_{attorney_data.get('name', 'attorney').replace(' ', '_').lower()}"
            front_path, back_path = self._save_cards(front_image, back_image, card_id)
            
            return {
                "success": True,
                "front_image": front_path,
                "back_image": back_path,
                "card_id": card_id,
                "design_style": design_style
            }
            
        except Exception as e:
            logger.error(f"Error generating business card: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_card_front(self, firm_data: dict, attorney_data: dict, palette: dict, design_style: str) -> Image:
        """Create the front of the business card"""
        
        # Create base image
        card = Image.new('RGB', (self.card_width, self.card_height), color=palette['background'])
        draw = ImageDraw.Draw(card)
        
        if design_style == 'classic_navy':
            return self._create_classic_navy_front(card, draw, firm_data, attorney_data, palette)
        elif design_style == 'professional_gray':
            return self._create_professional_gray_front(card, draw, firm_data, attorney_data, palette)
        elif design_style == 'burgundy_gold':
            return self._create_burgundy_gold_front(card, draw, firm_data, attorney_data, palette)
        elif design_style == 'forest_green':
            return self._create_forest_green_front(card, draw, firm_data, attorney_data, palette)
        elif design_style == 'modern_gradient':
            return self._create_modern_gradient_front(card, draw, firm_data, attorney_data, palette)
        elif design_style == 'modern_black':
            return self._create_modern_black_front(card, draw, firm_data, attorney_data, palette)
        else:
            return self._create_classic_navy_front(card, draw, firm_data, attorney_data, palette)
    
    def _create_classic_navy_front(self, card: Image, draw: ImageDraw, firm_data: dict, attorney_data: dict, palette: dict) -> Image:
        """Create classic navy design - professional and traditional"""
        
        # Draw main background rectangle
        draw.rectangle([0, 0, self.card_width, 200], fill=palette['primary'])
        
        # Draw accent stripe
        draw.rectangle([0, 190, self.card_width, 210], fill=palette['accent'])
        
        # Add firm name
        firm_name = firm_data.get('firmName', 'Law Firm')
        draw.text((50, 40), firm_name, font=self.fonts['title'], fill=palette['text'])
        
        # Add tagline
        tagline = firm_data.get('firmTagline', 'Excellence in Legal Advocacy')
        draw.text((50, 90), tagline, font=self.fonts['small'], fill=palette['accent'])
        
        # Add attorney name (larger, prominent)
        attorney_name = attorney_data.get('name', 'Attorney Name')
        draw.text((50, 250), attorney_name, font=self.fonts['name'], fill=palette['primary'])
        
        # Add position/title
        position = attorney_data.get('title', 'Attorney at Law')
        draw.text((50, 310), position, font=self.fonts['position'], fill=palette['secondary'])
        
        # Add contact information
        y_pos = 380
        contact_info = [
            f"📧 {attorney_data.get('email', firm_data.get('emailAddress', 'info@lawfirm.com'))}",
            f"📞 {firm_data.get('phoneNumber', '(555) 123-4567')}",
            f"🏢 {firm_data.get('city', 'Your City')}, {firm_data.get('state', 'State')}"
        ]
        
        for info in contact_info:
            draw.text((50, y_pos), info, font=self.fonts['contact'], fill=palette['secondary'])
            y_pos += 35
        
        # Add professional seal/logo area (placeholder)
        draw.ellipse([800, 250, 950, 400], outline=palette['accent'], width=3)
        draw.text((835, 315), "SEAL", font=self.fonts['contact'], fill=palette['accent'])
        
        return card
    
    def _create_professional_gray_front(self, card: Image, draw: ImageDraw, firm_data: dict, attorney_data: dict, palette: dict) -> Image:
        """Create professional gray design - modern and clean"""
        
        # Create gradient background
        for i in range(self.card_height):
            alpha = i / self.card_height
            gray_value = int(240 + (15 * alpha))
            color = (gray_value, gray_value, gray_value)
            draw.line([(0, i), (self.card_width, i)], fill=color)
        
        # Draw side accent bar
        draw.rectangle([0, 0, 20, self.card_height], fill=palette['accent'])
        
        # Add firm name with shadow effect
        firm_name = firm_data.get('firmName', 'Law Firm')
        # Shadow
        draw.text((52, 42), firm_name, font=self.fonts['title'], fill='#999999')
        # Main text
        draw.text((50, 40), firm_name, font=self.fonts['title'], fill=palette['primary'])
        
        # Add attorney name
        attorney_name = attorney_data.get('name', 'Attorney Name')
        draw.text((50, 200), attorney_name, font=self.fonts['name'], fill=palette['primary'])
        
        # Add position
        position = attorney_data.get('title', 'Attorney at Law')
        draw.text((50, 260), position, font=self.fonts['position'], fill=palette['secondary'])
        
        # Contact info in organized layout
        contact_y = 350
        email = attorney_data.get('email', firm_data.get('emailAddress', 'info@lawfirm.com'))
        phone = firm_data.get('phoneNumber', '(555) 123-4567')
        
        draw.text((50, contact_y), email, font=self.fonts['contact'], fill=palette['primary'])
        draw.text((50, contact_y + 30), phone, font=self.fonts['contact'], fill=palette['primary'])
        
        # Add geometric accent
        points = [(850, 300), (950, 250), (950, 350)]
        draw.polygon(points, fill=palette['accent'])
        
        return card
    
    def _create_burgundy_gold_front(self, card: Image, draw: ImageDraw, firm_data: dict, attorney_data: dict, palette: dict) -> Image:
        """Create burgundy and gold design - luxury and prestigious"""
        
        # Create diagonal split design
        points = [(0, 0), (self.card_width, 0), (self.card_width, 250), (0, 350)]
        draw.polygon(points, fill=palette['primary'])
        
        # Add gold accent line
        draw.line([(0, 350), (self.card_width, 250)], fill=palette['accent'], width=5)
        
        # Firm name in gold
        firm_name = firm_data.get('firmName', 'Law Firm')
        draw.text((50, 50), firm_name, font=self.fonts['title'], fill=palette['accent'])
        
        # Attorney name prominently displayed
        attorney_name = attorney_data.get('name', 'Attorney Name')
        draw.text((50, 120), attorney_name, font=self.fonts['name'], fill=palette['text'])
        
        # Position/title
        position = attorney_data.get('title', 'Attorney at Law')
        draw.text((50, 180), position, font=self.fonts['position'], fill=palette['accent'])
        
        # Contact info in lower section
        contact_y = 400
        contact_info = [
            attorney_data.get('email', firm_data.get('emailAddress', 'info@lawfirm.com')),
            firm_data.get('phoneNumber', '(555) 123-4567')
        ]
        
        for info in contact_info:
            draw.text((50, contact_y), info, font=self.fonts['contact'], fill=palette['primary'])
            contact_y += 30
        
        # Add luxury border
        draw.rectangle([10, 10, self.card_width-10, self.card_height-10], 
                      outline=palette['accent'], width=2)
        
        return card
    
    def _create_forest_green_front(self, card: Image, draw: ImageDraw, firm_data: dict, attorney_data: dict, palette: dict) -> Image:
        """Create forest green design - trustworthy and stable"""
        
        # Create two-tone background
        draw.rectangle([0, 0, self.card_width, 180], fill=palette['primary'])
        draw.rectangle([0, 180, self.card_width, self.card_height], fill=palette['background'])
        
        # Add connecting elements
        draw.rectangle([0, 170, self.card_width, 190], fill=palette['secondary'])
        
        # Firm name
        firm_name = firm_data.get('firmName', 'Law Firm')
        draw.text((50, 40), firm_name, font=self.fonts['title'], fill=palette['text'])
        
        # Tagline
        tagline = firm_data.get('firmTagline', 'Excellence in Legal Advocacy')
        draw.text((50, 90), tagline, font=self.fonts['small'], fill=palette['accent'])
        
        # Attorney information
        attorney_name = attorney_data.get('name', 'Attorney Name')
        draw.text((50, 220), attorney_name, font=self.fonts['name'], fill=palette['primary'])
        
        position = attorney_data.get('title', 'Attorney at Law')
        draw.text((50, 280), position, font=self.fonts['position'], fill=palette['secondary'])
        
        # Contact details
        contact_y = 350
        contact_info = [
            f"✉ {attorney_data.get('email', firm_data.get('emailAddress', 'info@lawfirm.com'))}",
            f"☎ {firm_data.get('phoneNumber', '(555) 123-4567')}",
            f"⌂ {firm_data.get('city', 'Your City')}, {firm_data.get('state', 'State')}"
        ]
        
        for info in contact_info:
            draw.text((50, contact_y), info, font=self.fonts['contact'], fill=palette['secondary'])
            contact_y += 25
        
        # Add nature-inspired accent
        draw.ellipse([780, 200, 980, 400], outline=palette['primary'], width=3)
        
        return card
    
    def _create_modern_black_front(self, card: Image, draw: ImageDraw, firm_data: dict, attorney_data: dict, palette: dict) -> Image:
        """Create modern black design - sleek and contemporary"""
        
        # Black base with geometric accents
        card_black = Image.new('RGB', (self.card_width, self.card_height), color=palette['primary'])
        draw = ImageDraw.Draw(card_black)
        
        # Add blue accent shapes
        draw.rectangle([self.card_width-100, 0, self.card_width, 150], fill=palette['accent'])
        draw.rectangle([0, self.card_height-100, 150, self.card_height], fill=palette['accent'])
        
        # Firm name
        firm_name = firm_data.get('firmName', 'Law Firm')
        draw.text((50, 50), firm_name, font=self.fonts['title'], fill=palette['text'])
        
        # Attorney name in accent color
        attorney_name = attorney_data.get('name', 'Attorney Name')
        draw.text((50, 180), attorney_name, font=self.fonts['name'], fill=palette['accent'])
        
        # Position
        position = attorney_data.get('title', 'Attorney at Law')
        draw.text((50, 240), position, font=self.fonts['position'], fill=palette['text'])
        
        # Minimal contact info
        email = attorney_data.get('email', firm_data.get('emailAddress', 'info@lawfirm.com'))
        phone = firm_data.get('phoneNumber', '(555) 123-4567')
        
        draw.text((50, 350), email, font=self.fonts['contact'], fill=palette['text'])
        draw.text((50, 380), phone, font=self.fonts['contact'], fill=palette['text'])
        
        # Add modern line accents
        draw.line([(50, 160), (400, 160)], fill=palette['accent'], width=2)
        draw.line([(50, 320), (300, 320)], fill=palette['accent'], width=1)
        
        return card_black
    
    def _create_modern_gradient_front(self, card: Image, draw: ImageDraw, firm_data: dict, attorney_data: dict, palette: dict) -> Image:
        """Create modern gradient design - sleek and attractive with gradient effects and QR code"""
        
        # Create sophisticated gradient background
        for y in range(self.card_height):
            # Create smooth gradient from dark blue to lighter blue
            gradient_ratio = y / self.card_height
            r = int(15 + (45 * gradient_ratio))   # 15 -> 60
            g = int(30 + (70 * gradient_ratio))   # 30 -> 100  
            b = int(60 + (120 * gradient_ratio))  # 60 -> 180
            draw.line([(0, y), (self.card_width, y)], fill=(r, g, b))
        
        # Add professional geometric overlay
        overlay = Image.new('RGBA', (self.card_width, self.card_height), (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Elegant white accent for text area
        overlay_draw.rectangle([30, 30, self.card_width-200, self.card_height-30], fill=(255, 255, 255, 25))
        
        # Modern geometric shapes
        points1 = [(self.card_width-180, 0), (self.card_width, 0), (self.card_width, 120)]
        overlay_draw.polygon(points1, fill=(255, 215, 0, 70))  # Gold accent
        
        points2 = [(self.card_width-120, self.card_height-100), (self.card_width, self.card_height-200), (self.card_width, self.card_height)]
        overlay_draw.polygon(points2, fill=(255, 255, 255, 40))
        
        # Blend overlay with card
        card = Image.alpha_composite(card.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(card)
        
        # Professional typography with shadow effects
        firm_name = firm_data.get('firmName', 'Professional Law Firm')
        
        # Title with professional styling
        # Shadow for depth
        draw.text((52, 52), firm_name, font=self.fonts['title'], fill='#000000')
        # Main text in white
        draw.text((50, 50), firm_name, font=self.fonts['title'], fill='#ffffff')
        
        # Attorney name with prominence
        attorney_name = attorney_data.get('name', 'Attorney Name')
        draw.text((50, 140), attorney_name, font=self.fonts['name'], fill='#ffffff')
        
        # Professional title with gold accent
        position = attorney_data.get('title', 'Attorney at Law')
        draw.text((50, 180), position, font=self.fonts['position'], fill='#ffd700')
        
        # Practice areas if available
        practice_areas = firm_data.get('practiceAreas', [])
        if practice_areas:
            areas_text = ' • '.join(practice_areas[:3])  # Show first 3 areas
            if len(areas_text) > 40:  # Truncate if too long
                areas_text = areas_text[:37] + '...'
            draw.text((50, 210), areas_text, font=self.fonts['small'], fill='#e6e6e6')
        
        # Contact information section
        contact_y = 260
        email = attorney_data.get('email', firm_data.get('emailAddress', 'info@lawfirm.com'))
        phone = firm_data.get('phoneNumber', '(555) 123-4567')
        
        # Email with icon effect
        draw.text((50, contact_y), f"✉ {email}", font=self.fonts['contact'], fill='#ffffff')
        
        # Phone with icon effect  
        draw.text((50, contact_y + 25), f"☎ {phone}", font=self.fonts['contact'], fill='#ffffff')
        
        # Website URL if available
        website_url = firm_data.get('website_url', '')
        if website_url:
            # Clean URL for display
            display_url = website_url.replace('https://', '').replace('http://', '')
            if len(display_url) > 35:
                display_url = display_url[:32] + '...'
            draw.text((50, contact_y + 50), f"🌐 {display_url}", font=self.fonts['small'], fill='#e6e6e6')
        
        # Generate and add QR code
        qr_code = self._generate_qr_code_for_card(firm_data, attorney_data)
        if qr_code:
            # Resize QR code to fit nicely
            qr_size = 100
            qr_code = qr_code.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            
            # Position QR code in the top right
            qr_x = self.card_width - qr_size - 40
            qr_y = 40
            
            # Add white background for QR code
            qr_bg = Image.new('RGB', (qr_size + 10, qr_size + 10), 'white')
            card.paste(qr_bg, (qr_x - 5, qr_y - 5))
            card.paste(qr_code, (qr_x, qr_y))
            
            # Add QR code label
            draw = ImageDraw.Draw(card)
            draw.text((qr_x + 10, qr_y + qr_size + 10), "Scan for Contact", font=self.fonts['small'], fill='#ffffff')
        
        return card
        
    def _generate_qr_code_for_card(self, firm_data: dict, attorney_data: dict) -> Image:
        """Generate QR code containing attorney and firm contact information"""
        try:
            # Create vCard format for easy contact import
            vcard_data = f"""BEGIN:VCARD
VERSION:3.0
FN:{attorney_data.get('name', 'Attorney Name')}
ORG:{firm_data.get('firmName', 'Law Firm')}
TITLE:{attorney_data.get('title', 'Attorney at Law')}
EMAIL:{attorney_data.get('email', firm_data.get('emailAddress', ''))}
TEL:{firm_data.get('phoneNumber', '')}
ADR:;;{firm_data.get('officeAddress', '')};{firm_data.get('city', '')};{firm_data.get('state', '')};{firm_data.get('zipCode', '')};
URL:{firm_data.get('website_url', '')}
NOTE:Specializing in {', '.join(firm_data.get('practiceAreas', ['Legal Services']))}
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
            
            # Create QR code image
            qr_img = qr.make_image(fill_color='black', back_color='white')
            
            return qr_img
            
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return None

    def _create_card_back(self, firm_data: dict, attorney_data: dict, palette: dict, design_style: str) -> Image:
        """Create the back of the business card with QR code and practice areas"""
        
        # Create base image
        card = Image.new('RGB', (self.card_width, self.card_height), color=palette['background'])
        draw = ImageDraw.Draw(card)
        
        # Add header
        if design_style in ['classic_navy', 'forest_green']:
            draw.rectangle([0, 0, self.card_width, 100], fill=palette['primary'])
            draw.text((50, 30), "Practice Areas & Contact", font=self.fonts['position'], fill=palette['text'])
        else:
            draw.text((50, 30), "Practice Areas & Contact", font=self.fonts['position'], fill=palette['primary'])
            draw.line([(50, 70), (self.card_width-50, 70)], fill=palette['accent'], width=2)
        
        # Add practice areas
        practice_areas = firm_data.get('practiceAreas', [])
        area_names = {
            'criminal': 'Criminal Defense',
            'family': 'Family Law',
            'corporate': 'Corporate Law',
            'personal-injury': 'Personal Injury',
            'estate': 'Estate Planning',
            'immigration': 'Immigration Law'
        }
        
        y_pos = 120
        areas_text = "Practice Areas:"
        draw.text((50, y_pos), areas_text, font=self.fonts['contact'], fill=palette['primary'])
        y_pos += 40
        
        for area in practice_areas[:4]:  # Limit to 4 areas for space
            area_name = area_names.get(area, area.replace('-', ' ').title())
            draw.text((70, y_pos), f"• {area_name}", font=self.fonts['small'], fill=palette['secondary'])
            y_pos += 30
        
        # Add QR code
        if firm_data.get('website_url'):
            qr_code = self._create_qr_code(firm_data['website_url'])
            if qr_code:
                # Resize QR code to fit card
                qr_size = 150
                qr_code = qr_code.resize((qr_size, qr_size))
                
                # Position QR code on right side
                qr_x = self.card_width - qr_size - 50
                qr_y = 150
                card.paste(qr_code, (qr_x, qr_y))
                
                # Add QR code label
                draw.text((qr_x, qr_y + qr_size + 10), "Scan for Website", 
                         font=self.fonts['small'], fill=palette['secondary'])
        
        # Add address at bottom
        address_lines = [
            firm_data.get('officeAddress', ''),
            f"{firm_data.get('city', 'Your City')}, {firm_data.get('state', 'State')} {firm_data.get('zipCode', '')}"
        ]
        
        y_pos = self.card_height - 80
        for line in address_lines:
            if line.strip():
                draw.text((50, y_pos), line, font=self.fonts['small'], fill=palette['secondary'])
                y_pos += 25
        
        return card
    
    def _create_qr_code(self, url: str) -> Image:
        """Create QR code image for the website URL"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=2,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color='black', back_color='white')
            return qr_img
            
        except Exception as e:
            logger.error(f"Error creating QR code: {e}")
            return None
    
    def _save_cards(self, front_image: Image, back_image: Image, card_id: str) -> tuple:
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
            
            logger.info(f"Business cards saved: {front_url}, {back_url}")
            return front_url, back_url
            
        except Exception as e:
            logger.error(f"Error saving business cards: {e}")
            return "", ""
    
    def get_available_designs(self) -> dict:
        """Return available design styles and their descriptions"""
        return {
            'classic_navy': {
                'name': 'Classic Navy',
                'description': 'Traditional and professional with navy blue and gold accents',
                'preview_colors': ['#1a365d', '#d4af37', '#f7fafc']
            },
            'professional_gray': {
                'name': 'Professional Gray',
                'description': 'Modern and clean with sophisticated gray tones',
                'preview_colors': ['#2d3748', '#e53e3e', '#edf2f7']
            },
            'burgundy_gold': {
                'name': 'Burgundy Gold',
                'description': 'Luxury design with rich burgundy and gold elements',
                'preview_colors': ['#7c2d12', '#d4af37', '#fef5e7']
            },
            'forest_green': {
                'name': 'Forest Green',
                'description': 'Trustworthy and stable with natural green tones',
                'preview_colors': ['#065f46', '#a3a3a3', '#ecfdf5']
            },
            'modern_black': {
                'name': 'Modern Black',
                'description': 'Sleek and contemporary with black and blue accents',
                'preview_colors': ['#0f172a', '#60a5fa', '#f8fafc']
            }
        }
    
    def batch_generate_cards(self, firm_data: dict, design_style: str = 'classic_navy') -> dict:
        """Generate business cards for all attorneys in a firm"""
        try:
            cards = []
            attorneys = firm_data.get('attorneys', [])
            
            for attorney in attorneys:
                card_result = self.generate_business_card(firm_data, attorney, design_style)
                if card_result['success']:
                    cards.append({
                        'attorney_name': attorney.get('name', 'Attorney'),
                        'front_image': card_result['front_image'],
                        'back_image': card_result['back_image'],
                        'card_id': card_result['card_id']
                    })
            
            return {
                "success": True,
                "cards": cards,
                "design_style": design_style,
                "total_cards": len(cards)
            }
            
        except Exception as e:
            logger.error(f"Error in batch card generation: {e}")
            return {"success": False, "error": str(e)}