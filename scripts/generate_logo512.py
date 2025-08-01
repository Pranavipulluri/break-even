#!/usr/bin/env python3
"""
Generate a 512x512 logo for the Break-even app
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_logo512():
    """Create a 512x512 logo for the app"""
    
    # Create a new image with white background
    size = 512
    image = Image.new('RGBA', (size, size), (59, 130, 246, 255))  # Blue background
    draw = ImageDraw.Draw(image)
    
    # Draw a circle background
    circle_margin = 50
    circle_bbox = [circle_margin, circle_margin, size - circle_margin, size - circle_margin]
    draw.ellipse(circle_bbox, fill=(255, 255, 255, 255))
    
    # Try to load a font, fallback to default if not found
    try:
        font_size = 120
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)  # macOS
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)  # Linux
            except:
                font = ImageFont.load_default()
    
    # Draw "BE" text (Break-Even)
    text = "BE"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - 20
    
    draw.text((text_x, text_y), text, fill=(59, 130, 246, 255), font=font)
    
    # Add smaller subtitle
    try:
        subtitle_font = ImageFont.truetype("arial.ttf", 40)
    except:
        subtitle_font = font
    
    subtitle = "Business"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    
    subtitle_x = (size - subtitle_width) // 2
    subtitle_y = text_y + text_height + 10
    
    draw.text((subtitle_x, subtitle_y), subtitle, fill=(107, 114, 128, 255), font=subtitle_font)
    
    return image

def main():
    """Generate and save the logo"""
    try:
        # Get the frontend public directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        public_dir = os.path.join(os.path.dirname(script_dir), 'frontend', 'public')
        
        # Create the logo
        logo = create_logo512()
        
        # Save as PNG
        logo_path = os.path.join(public_dir, 'logo512.png')
        logo.save(logo_path, 'PNG', optimize=True)
        print(f"✅ Generated logo512.png: {logo_path}")
        
        # Also create a smaller version - force regeneration of logo192.png
        logo192_path = os.path.join(public_dir, 'logo192.png')
        logo192 = logo.resize((192, 192), Image.Resampling.LANCZOS)
        logo192.save(logo192_path, 'PNG', optimize=True)
        print(f"✅ Generated logo192.png: {logo192_path}")
        
        # Create favicon.ico - always regenerate to ensure it's valid
        favicon_path = os.path.join(public_dir, 'favicon.ico')
        favicon_sizes = [(16, 16), (32, 32), (48, 48)]
        favicon_images = []
        for size in favicon_sizes:
            favicon_img = logo.resize(size, Image.Resampling.LANCZOS)
            favicon_images.append(favicon_img)
            
        favicon_images[0].save(
            favicon_path,
            format='ICO',
            sizes=[(16, 16), (32, 32), (48, 48)],
            append_images=favicon_images[1:]
        )
        print(f"✅ Generated favicon.ico: {favicon_path}")
            
    except ImportError:
        print("❌ PIL (Pillow) not installed. Install it with: pip install Pillow")
    except Exception as e:
        print(f"❌ Error generating logo: {e}")

if __name__ == "__main__":
    main()
