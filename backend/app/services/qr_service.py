import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
from flask import current_app

class QRService:
    def __init__(self):
        pass
    
    def generate_qr_code(self, url, size=256, logo_path=None):
        """Generate QR code with optional logo"""
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        
        # Add data
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Resize to requested size
        qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Add logo if provided
        if logo_path:
            try:
                logo = Image.open(logo_path)
                # Calculate logo size (should be about 1/5 of QR code size)
                logo_size = size // 5
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                
                # Calculate position to center logo
                logo_pos = ((qr_img.size[0] - logo.size[0]) // 2,
                           (qr_img.size[1] - logo.size[1]) // 2)
                
                # Paste logo onto QR code
                qr_img.paste(logo, logo_pos)
            except Exception as e:
                print(f"Error adding logo to QR code: {e}")
        
        return qr_img
    
    def generate_branded_qr_code(self, url, business_name, size=256, color='#000000'):
        """Generate QR code with business branding"""
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=4,
        )
        
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create image with custom colors
        qr_img = qr.make_image(fill_color=color, back_color="white")
        
        # Create a larger canvas for branding
        canvas_size = size + 80  # Extra space for text
        canvas = Image.new('RGB', (canvas_size, canvas_size), 'white')
        
        # Resize QR code to fit in canvas
        qr_size = size - 40
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        
        # Paste QR code onto canvas
        qr_pos = ((canvas_size - qr_size) // 2, 20)
        canvas.paste(qr_img, qr_pos)
        
        # Add business name text
        draw = ImageDraw.Draw(canvas)
        
        try:
            # Try to use a better font
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            # Fall back to default font
            font = ImageFont.load_default()
        
        # Calculate text position
        text_bbox = draw.textbbox((0, 0), business_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (canvas_size - text_width) // 2
        text_y = qr_pos[1] + qr_size + 10
        
        # Draw text
        draw.text((text_x, text_y), business_name, fill=color, font=font)
        
        # Add "Scan to visit" text
        scan_text = "Scan to visit our website"
        try:
            small_font = ImageFont.truetype("arial.ttf", 12)
        except:
            small_font = ImageFont.load_default()
        
        scan_bbox = draw.textbbox((0, 0), scan_text, font=small_font)
        scan_width = scan_bbox[2] - scan_bbox[0]
        scan_x = (canvas_size - scan_width) // 2
        scan_y = text_y + 25
        
        draw.text((scan_x, scan_y), scan_text, fill='#666666', font=small_font)
        
        return canvas
    
    def generate_qr_with_frame(self, url, business_name, frame_color='#2196F3', size=300):
        """Generate QR code with decorative frame"""
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )
        
        qr.add_data(url)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Create canvas with frame
        frame_width = 20
        canvas_size = size + (frame_width * 2)
        canvas = Image.new('RGB', (canvas_size, canvas_size), frame_color)
        
        # Create inner white area
        inner_size = size
        inner_canvas = Image.new('RGB', (inner_size, inner_size), 'white')
        
        # Resize and paste QR code
        qr_size = inner_size - 60  # Leave space for text
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        qr_pos = ((inner_size - qr_size) // 2, 20)
        inner_canvas.paste(qr_img, qr_pos)
        
        # Add text to inner canvas
        draw = ImageDraw.Draw(inner_canvas)
        
        try:
            font = ImageFont.truetype("arial.ttf", 14)
            small_font = ImageFont.truetype("arial.ttf", 10)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Business name
        text_bbox = draw.textbbox((0, 0), business_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (inner_size - text_width) // 2
        text_y = qr_pos[1] + qr_size + 10
        draw.text((text_x, text_y), business_name, fill='black', font=font)
        
        # Scan instruction
        scan_text = "Scan with your phone camera"
        scan_bbox = draw.textbbox((0, 0), scan_text, font=small_font)
        scan_width = scan_bbox[2] - scan_bbox[0]
        scan_x = (inner_size - scan_width) // 2
        scan_y = text_y + 20
        draw.text((scan_x, scan_y), scan_text, fill='#666666', font=small_font)
        
        # Paste inner canvas onto main canvas
        canvas.paste(inner_canvas, (frame_width, frame_width))
        
        return canvas
