"""
Mock Image Generator Service for Break-even App
Returns predefined images based on specific prompts
"""

import base64
import io
from PIL import Image
from flask import current_app
import os
from datetime import datetime

class MockImageService:
    
    def __init__(self):
        self.mock_images = {}
        self._load_mock_images()
    
    def _load_mock_images(self):
        """Load predefined mock images"""
        # These are base64 encoded versions of the images you provided
        # For now, I'll create placeholder images, but you can replace with actual base64 data
        
        # Samosa business poster image (placeholder - replace with actual base64)
        self.mock_images['samosa'] = self._create_samosa_mockup()
        
        # Clothes store business poster (placeholder - replace with actual base64)  
        self.mock_images['clothes'] = self._create_clothes_mockup()
        
        # Default business image
        self.mock_images['default'] = self._create_default_mockup()
    
    def generate_image(self, prompt, image_type='poster', style='professional'):
        """Generate mock image based on prompt"""
        try:
            prompt_lower = prompt.lower()
            
            # Determine which mock image to return based on prompt
            if 'samosa' in prompt_lower or 'indian food' in prompt_lower or 'street food' in prompt_lower:
                image_data = self.mock_images['samosa']
                concept = "Professional samosa business poster featuring golden triangular samosas arranged on a traditional plate with Indian spices and chutneys. Dark background with elegant typography showcasing 'SAMOSA BUSINESS' branding."
            elif 'clothes' in prompt_lower or 'clothing' in prompt_lower or 'fashion' in prompt_lower or 'apparel' in prompt_lower:
                image_data = self.mock_images['clothes']
                concept = "Modern clothing business poster with neatly folded colorful garments arranged in a circle. Features elegant typography with 'MY CLOTHS BUSINESS' branding on a warm brown background."
            else:
                image_data = self.mock_images['default']
                concept = f"Professional {image_type} design for {prompt} with {style} styling."
            
            return {
                'success': True,
                'image_data': image_data,
                'concept': concept,
                'prompt': prompt,
                'image_type': image_type,
                'style': style,
                'dimensions': '800x600'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Mock image generation failed: {str(e)}'
            }
    
    def _create_samosa_mockup(self):
        """Create samosa business poster mockup"""
        try:
            # Create a realistic samosa poster
            width, height = 800, 800
            image = Image.new('RGB', (width, height), color='#2c1810')  # Dark brown background
            
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(image)
            
            # Try to load fonts
            try:
                title_font = ImageFont.truetype("arial.ttf", 60)
                subtitle_font = ImageFont.truetype("arial.ttf", 40)
                text_font = ImageFont.truetype("arial.ttf", 24)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
            
            # Add decorative border
            draw.rectangle([20, 20, width-20, height-20], outline='#d4af37', width=4)
            
            # Add title "SAMOSA BUSINESS"
            title_y = 80
            draw.text((width//2, title_y), "SAMOSA", fill='#ffffff', font=title_font, anchor="mm")
            draw.text((width//2, title_y + 70), "BUSINESS", fill='#ffd700', font=subtitle_font, anchor="mm")
            
            # Add decorative lines
            draw.line([(100, 180), (700, 180)], fill='#d4af37', width=2)
            draw.line([(100, 600), (700, 600)], fill='#d4af37', width=2)
            
            # Create samosa shapes (triangular)
            samosa_positions = [
                (200, 300), (400, 280), (600, 320),
                (150, 400), (350, 420), (550, 380), (650, 450)
            ]
            
            for x, y in samosa_positions:
                # Draw triangular samosa shape
                points = [(x, y), (x+60, y+20), (x+30, y+80)]
                draw.polygon(points, fill='#daa520', outline='#b8860b', width=2)
                
                # Add texture lines
                draw.line([(x+10, y+20), (x+50, y+30)], fill='#b8860b', width=1)
                draw.line([(x+15, y+40), (x+45, y+50)], fill='#b8860b', width=1)
            
            # Add circular plate outline
            draw.ellipse([120, 250, 680, 500], outline='#8b4513', width=3, fill=None)
            
            # Add promotional text
            draw.text((width//2, 650), "Authentic • Fresh • Delicious", fill='#ffd700', font=text_font, anchor="mm")
            draw.text((width//2, 680), "₹20 per piece", fill='#ffffff', font=text_font, anchor="mm")
            
            # Add small decorative elements
            for i in range(8):
                angle = i * 45
                x = width//2 + 250 * (0.7 if i % 2 else 0.8) * (1 if i < 4 else -1) * (1 if i % 4 < 2 else -1)
                y = height//2 + 200 * (0.7 if i % 2 else 0.8) * (1 if i < 4 else -1) * (1 if (i+1) % 4 < 2 else -1)
                if 50 < x < width-50 and 50 < y < height-50:
                    draw.ellipse([x-3, y-3, x+3, y+3], fill='#d4af37')
            
            # Convert to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"Error creating samosa mockup: {e}")
            return self._create_default_mockup()
    
    def _create_clothes_mockup(self):
        """Create clothes store business poster mockup"""
        try:
            width, height = 800, 800
            image = Image.new('RGB', (width, height), color='#8b4513')  # Brown background
            
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(image)
            
            try:
                title_font = ImageFont.truetype("arial.ttf", 50)
                subtitle_font = ImageFont.truetype("arial.ttf", 35)
                text_font = ImageFont.truetype("arial.ttf", 20)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
            
            # Add title
            draw.text((width//2, 100), "MY CLOTHS", fill='#ffffff', font=title_font, anchor="mm")
            draw.text((width//2, 160), "BUSINESS", fill='#ffffff', font=subtitle_font, anchor="mm")
            
            # Add decorative elements
            draw.line([(150, 200), (650, 200)], fill='#ffffff', width=2)
            
            # Create clothing items arranged in circle
            clothing_colors = [
                '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', 
                '#feca57', '#ff9ff3', '#54a0ff', '#5f27cd'
            ]
            
            import math
            center_x, center_y = width//2, height//2 + 50
            radius = 200
            
            for i in range(8):
                angle = i * (2 * math.pi / 8)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                
                color = clothing_colors[i % len(clothing_colors)]
                
                # Draw folded clothing item (rectangle with fold lines)
                item_width, item_height = 80, 60
                draw.rectangle([x-item_width//2, y-item_height//2, 
                              x+item_width//2, y+item_height//2], 
                             fill=color, outline='#654321', width=2)
                
                # Add fold lines
                draw.line([(x-item_width//4, y-item_height//2), 
                          (x-item_width//4, y+item_height//2)], 
                         fill='#ffffff', width=1)
                draw.line([(x+item_width//4, y-item_height//2), 
                          (x+item_width//4, y+item_height//2)], 
                         fill='#ffffff', width=1)
            
            # Add center circle
            draw.ellipse([center_x-60, center_y-60, center_x+60, center_y+60], 
                        fill='#654321', outline='#ffffff', width=3)
            draw.text((center_x, center_y), "FASHION", fill='#ffffff', font=text_font, anchor="mm")
            
            # Add bottom text
            draw.text((width//2, height-100), "GREAT BUSINESS", fill='#ffffff', font=text_font, anchor="mm")
            draw.text((width//2, height-70), "WHAT FORTH WITH", fill='#ffffff', font=text_font, anchor="mm")
            
            # Convert to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"Error creating clothes mockup: {e}")
            return self._create_default_mockup()
    
    def _create_default_mockup(self):
        """Create default business poster mockup"""
        try:
            width, height = 800, 600
            image = Image.new('RGB', (width, height), color='#4a90e2')
            
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(image)
            
            try:
                font = ImageFont.truetype("arial.ttf", 36)
            except:
                font = ImageFont.load_default()
            
            draw.text((width//2, height//2), "BUSINESS POSTER", 
                     fill='white', font=font, anchor="mm")
            
            # Convert to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"Error creating default mockup: {e}")
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    def test_connection(self):
        """Test mock service (always returns success)"""
        return {
            'success': True,
            'message': 'Mock Image Service ready'
        }
