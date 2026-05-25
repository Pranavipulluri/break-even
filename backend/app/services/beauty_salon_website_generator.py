"""
Beauty Salon/Spa Website Generator - Creates stunning spa/salon websites with booking functionality
"""

import os
import shutil
import json
import logging
import qrcode
import zipfile
import io
import requests
from datetime import datetime
from PIL import Image
from .universal_business_card_generator import UniversalBusinessCardGenerator

logger = logging.getLogger(__name__)

class BeautySalonWebsiteGenerator:
    """Generate beautiful websites for beauty salons and spas"""
    
    def __init__(self):
        self.template_dir = "templates"
        self.static_dir = "static"
        self.netlify_token = os.environ.get('NETLIFY_API_KEY')
        self.card_generator = UniversalBusinessCardGenerator()
    
    def generate_website(self, salon_id: str, salon_data: dict) -> dict:
        """Generate website - compatibility method for integration service"""
        try:
            salon_id = salon_data.get('salon_id')
            salon_name = salon_data.get('salon_name', 'Beauty Salon')
            
            # Use the existing create_complete_spa_website method
            result = self.create_complete_spa_website(salon_data)
            
            if result.get('success'):
                # Add salon_id to salon_data for deployment
                salon_data_with_id = salon_data.copy()
                salon_data_with_id['salon_id'] = salon_id
                
                # Deploy the website
                deploy_result = self.deploy_spa_website_to_netlify(salon_data_with_id, result.get('website_files', {}))
                
                # Include business cards from the result
                business_cards = result.get('business_cards', [])
                
                return {
                    "success": True,
                    "salon_id": salon_id,
                    "website_url": deploy_result.get('website_url'),
                    "netlify_url": deploy_result.get('website_url'),  # Same as website_url for consistency
                    "qr_code_url": deploy_result.get('qr_code_url'),
                    "website_files": result.get('website_files', {}),
                    "business_cards": business_cards,
                    "deployment": deploy_result,
                    "netlify_deployed": deploy_result.get('netlify_deployed', False)
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'Failed to create spa website')
                }
                
        except Exception as e:
            logger.error(f"Error generating spa website: {e}")
            return {
                "success": False,
                "error": f"Website generation failed: {str(e)}"
            }
        
    def create_complete_spa_website(self, salon_data: dict) -> dict:
        """Create a complete spa/salon website with all functionality"""
        try:
            salon_id = salon_data.get('salon_id')
            salon_name = salon_data.get('salon_name', 'Beauty Salon')
            
            logger.info(f"Creating complete spa website for: {salon_name}")
            
            # Generate main website
            website_content = self._generate_spa_website_content(salon_data)
            
            # Create Netlify functions for spa functionality
            netlify_functions = self._create_spa_netlify_functions(salon_data)
            
            # Generate configuration
            netlify_config = self._generate_spa_netlify_config(salon_data)
            
            # Create file structure
            website_files = self._organize_spa_files(
                salon_data, website_content, netlify_functions, netlify_config
            )
            
            # Generate business cards for staff members
            business_cards = self._generate_staff_business_cards(salon_data)
            
            logger.info(f"Spa website created with {len(website_files)} files and {len(business_cards)} business cards")
            
            return {
                "success": True,
                "salon_id": salon_id,
                "salon_name": salon_name,
                "website_files": website_files,
                "business_cards": business_cards,
                "has_booking_system": True,
                "has_staff_profiles": True,
                "has_service_catalog": True,
                "has_business_cards": len(business_cards) > 0,
                "deployment_ready": True
            }
            
        except Exception as e:
            logger.error(f"Error creating spa website: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_spa_website_content(self, salon_data: dict) -> str:
        """Generate beautiful spa website HTML"""
        
        salon_name = salon_data.get('salon_name', 'Luxury Spa & Salon')
        description = salon_data.get('description', 'Experience ultimate relaxation and beauty')
        services = salon_data.get('services', [])
        staff_members = salon_data.get('staff_members', [])
        address = salon_data.get('address', '')
        phone = salon_data.get('phone_number', '')
        email = salon_data.get('email_address', '')
        
        # Generate services HTML
        services_html = ""
        service_icons = {
            'facial': 'fas fa-spa',
            'massage': 'fas fa-hands',
            'manicure': 'fas fa-hand-sparkles',
            'pedicure': 'fas fa-shoe-prints',
            'hair': 'fas fa-cut',
            'makeup': 'fas fa-palette',
            'eyebrow': 'fas fa-eye',
            'waxing': 'fas fa-feather',
            'treatment': 'fas fa-leaf',
            'therapy': 'fas fa-heart'
        }
        
        for i, service in enumerate(services):
            service_name = service.get('name', 'Service').lower()
            icon_class = 'fas fa-spa'  # default
            
            # Try to match service name with icon
            for key, icon in service_icons.items():
                if key in service_name:
                    icon_class = icon
                    break
            
            services_html += f'''
                <div class="service-card reveal">
                    <div class="service-icon">
                        <i class="{icon_class}"></i>
                    </div>
                    <h4>{service.get('name', 'Service')}</h4>
                    <p>{service.get('description', 'Professional beauty service designed to enhance your natural beauty and promote relaxation.')}</p>
                    <div class="service-price">${service.get('price', '75')}</div>
                    <div class="service-duration">{service.get('duration', '60')} minutes</div>
                </div>
            '''
        
        # Generate staff HTML
        staff_html = ""
        staff_avatars = ['👩‍💼', '👨‍💼', '👩‍⚕️', '👨‍⚕️', '👩‍🎨', '👨‍🎨']
        
        for i, staff in enumerate(staff_members):
            specializations = ', '.join(staff.get('specializations', ['Beauty Specialist']))
            avatar = staff_avatars[i % len(staff_avatars)]
            
            staff_html += f'''
                <div class="staff-card reveal">
                    <div class="staff-photo">
                        {avatar}
                    </div>
                    <h4>{staff.get('name', 'Staff Member')}</h4>
                    <p class="staff-title">{staff.get('title', 'Beauty Specialist')}</p>
                    <p class="staff-specializations">{specializations}</p>
                    <button class="book-with-staff" data-staff="{staff.get('name')}">
                        <i class="fas fa-calendar-plus"></i> Book with {staff.get('name', 'Staff').split()[0]}
                    </button>
                </div>
            '''
        
        website_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{salon_name} - Luxury Beauty & Wellness</title>
    <meta name="description" content="{description}">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@300;400;600;700&family=Lato:wght@300;400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/axios/1.3.4/axios.min.js"></script>
    <style>
        /* Language Selector */
        .language-selector {{
            position: fixed;
            top: 100px;
            left: 20px;
            z-index: 200;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1rem;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            border: 1px solid rgba(232, 180, 184, 0.3);
            transition: all 0.3s ease;
        }}
        
        .language-selector:hover {{
            transform: translateY(-2px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.2);
        }}
        
        .language-label {{
            font-size: 0.9rem;
            color: var(--charcoal);
            margin-bottom: 0.5rem;
            font-weight: 600;
            text-align: center;
        }}
        
        .language-options {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        
        .language-option {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
            border: 1px solid transparent;
        }}
        
        .language-option:hover {{
            background: linear-gradient(135deg, var(--primary-rose), var(--secondary-sage));
            color: white;
            transform: translateX(3px);
        }}
        
        .language-option.active {{
            background: linear-gradient(135deg, var(--accent-gold), var(--eucalyptus));
            color: white;
            border-color: var(--deep-sage);
        }}
        
        .flag {{
            font-size: 1.2rem;
        }}
        
        .language-name {{
            font-weight: 500;
        }}
        
        /* Loading overlay */
        .translation-loading {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(5px);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }}
        
        .loading-spinner {{
            background: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }}
        
        .spinner {{
            border: 4px solid var(--warm-cream);
            border-top: 4px solid var(--primary-rose);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
            --secondary-sage: #9CAF88;
            --accent-gold: #D4B896;
            --warm-cream: #F7F3E9;
            --soft-lavender: #E6E2F3;
            --deep-sage: #6B8E5A;
            --charcoal: #2C2C2C;
            --pearl-white: #FEFEFE;
            --sunset-peach: #F5C6A0;
            --eucalyptus: #A8C090;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Lato', sans-serif;
            line-height: 1.7;
            color: var(--charcoal);
            background: 
                radial-gradient(circle at 20% 50%, rgba(232, 180, 184, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(156, 175, 136, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 80%, rgba(212, 184, 150, 0.1) 0%, transparent 50%),
                linear-gradient(135deg, var(--warm-cream) 0%, var(--soft-lavender) 50%, var(--warm-cream) 100%);
            background-attachment: fixed;
            min-height: 100vh;
            position: relative;
        }}
        
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 60"><defs><pattern id="floral" x="0" y="0" width="30" height="30" patternUnits="userSpaceOnUse"><circle cx="15" cy="15" r="1" fill="%23E8B4B8" opacity="0.1"><animate attributeName="opacity" values="0.1;0.3;0.1" dur="8s" repeatCount="indefinite"/></circle><path d="M10,15 Q15,10 20,15 Q15,20 10,15" fill="%239CAF88" opacity="0.05"><animateTransform attributeName="transform" type="rotate" values="0 15 15;360 15 15" dur="20s" repeatCount="indefinite"/></path></pattern></defs><rect width="60" height="60" fill="url(%23floral)"/></svg>');
            pointer-events: none;
            z-index: -1;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        /* Header */
        header {{
            background: linear-gradient(135deg, var(--primary-rose) 0%, var(--secondary-sage) 50%, var(--accent-gold) 100%);
            color: white;
            padding: 1.2rem 0;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            backdrop-filter: blur(10px);
        }}
        
        nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .logo {{
            font-family: 'Playfair Display', serif;
            font-size: 2.2rem;
            font-weight: 700;
            text-decoration: none;
            color: white;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        nav ul {{
            list-style: none;
            display: flex;
            gap: 2.5rem;
            align-items: center;
        }}
        
        nav a {{
            color: white;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            position: relative;
            padding: 0.5rem 1rem;
            border-radius: 25px;
        }}
        
        nav a:hover {{
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }}
        
        /* Hero Section */
        .hero {{
            background: 
                linear-gradient(135deg, rgba(232, 180, 184, 0.8) 0%, rgba(156, 175, 136, 0.8) 50%, rgba(212, 184, 150, 0.8) 100%), 
                url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800"><defs><radialGradient id="g1" cx="0.2" cy="0.3" r="0.8"><stop offset="0%" style="stop-color:%23E8B4B8;stop-opacity:0.4"/><stop offset="100%" style="stop-color:transparent"/></radialGradient><radialGradient id="g2" cx="0.8" cy="0.7" r="0.6"><stop offset="0%" style="stop-color:%239CAF88;stop-opacity:0.3"/><stop offset="100%" style="stop-color:transparent"/></radialGradient><radialGradient id="g3" cx="0.5" cy="0.1" r="0.5"><stop offset="0%" style="stop-color:%23D4B896;stop-opacity:0.3"/><stop offset="100%" style="stop-color:transparent"/></radialGradient></defs><rect width="1200" height="800" fill="%23F7F3E9"/><circle cx="240" cy="240" r="320" fill="url(%23g1)"/><circle cx="960" cy="560" r="240" fill="url(%23g2)"/><circle cx="600" cy="80" r="200" fill="url(%23g3)"/><path d="M0,400 Q300,200 600,400 T1200,400 L1200,800 L0,800 Z" fill="%23E6E2F3" opacity="0.3"/></svg>');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: white;
            text-align: center;
            padding: 12rem 0;
            position: relative;
            overflow: hidden;
            min-height: 100vh;
            display: flex;
            align-items: center;
        }}
        
        .hero::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="10" cy="10" r="0.5" fill="white" opacity="0.6"><animate attributeName="opacity" values="0.6;0.2;0.6" dur="3s" repeatCount="indefinite"/></circle><circle cx="90" cy="30" r="0.8" fill="white" opacity="0.4"><animate attributeName="opacity" values="0.4;0.8;0.4" dur="4s" repeatCount="indefinite"/></circle><circle cx="30" cy="80" r="0.6" fill="white" opacity="0.5"><animate attributeName="opacity" values="0.5;0.1;0.5" dur="5s" repeatCount="indefinite"/></circle><circle cx="70" cy="60" r="0.4" fill="white" opacity="0.7"><animate attributeName="opacity" values="0.7;0.3;0.7" dur="2s" repeatCount="indefinite"/></circle><path d="M0,50 Q25,30 50,50 T100,50" stroke="white" stroke-width="0.2" fill="none" opacity="0.2"><animate attributeName="opacity" values="0.2;0.6;0.2" dur="6s" repeatCount="indefinite"/></path></svg>'),
                radial-gradient(circle at 20% 80%, rgba(255,255,255,0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 50%);
            animation: sparkle 15s infinite linear;
        }}
        
        .hero::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800"><defs><filter id="glow"><feGaussianBlur stdDeviation="3" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><g filter="url(%23glow)"><path d="M200,200 Q400,100 600,200 T1000,200" stroke="%23E8B4B8" stroke-width="2" fill="none" opacity="0.3"><animate attributeName="d" values="M200,200 Q400,100 600,200 T1000,200;M200,220 Q400,120 600,220 T1000,220;M200,200 Q400,100 600,200 T1000,200" dur="8s" repeatCount="indefinite"/></path><path d="M100,400 Q300,300 500,400 T900,400" stroke="%239CAF88" stroke-width="2" fill="none" opacity="0.2"><animate attributeName="d" values="M100,400 Q300,300 500,400 T900,400;M100,420 Q300,320 500,420 T900,420;M100,400 Q300,300 500,400 T900,400" dur="10s" repeatCount="indefinite"/></path><path d="M150,600 Q350,500 550,600 T950,600" stroke="%23D4B896" stroke-width="2" fill="none" opacity="0.25"><animate attributeName="d" values="M150,600 Q350,500 550,600 T950,600;M150,580 Q350,480 550,580 T950,580;M150,600 Q350,500 550,600 T950,600" dur="12s" repeatCount="indefinite"/></path></g></svg>');
            pointer-events: none;
        }}
        
        @keyframes sparkle {{
            0%, 100% {{ transform: translateY(0) rotate(0deg); opacity: 1; }}
            25% {{ transform: translateY(-5px) rotate(90deg); opacity: 0.8; }}
            50% {{ transform: translateY(-10px) rotate(180deg); opacity: 0.6; }}
            75% {{ transform: translateY(-5px) rotate(270deg); opacity: 0.8; }}
        }}
        
        .hero-content {{
            position: relative;
            z-index: 10;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .hero-image {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 600px;
            height: 600px;
            background: 
                radial-gradient(circle at center, rgba(255,255,255,0.1) 0%, transparent 70%),
                url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400"><defs><linearGradient id="petals" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:%23E8B4B8;stop-opacity:0.6"/><stop offset="50%" style="stop-color:%239CAF88;stop-opacity:0.4"/><stop offset="100%" style="stop-color:%23D4B896;stop-opacity:0.6"/></linearGradient></defs><g transform="translate(200,200)"><g id="flower"><ellipse cx="0" cy="-60" rx="25" ry="60" fill="url(%23petals)" transform="rotate(0)"/><ellipse cx="0" cy="-60" rx="25" ry="60" fill="url(%23petals)" transform="rotate(45)"/><ellipse cx="0" cy="-60" rx="25" ry="60" fill="url(%23petals)" transform="rotate(90)"/><ellipse cx="0" cy="-60" rx="25" ry="60" fill="url(%23petals)" transform="rotate(135)"/><ellipse cx="0" cy="-60" rx="25" ry="60" fill="url(%23petals)" transform="rotate(180)"/><ellipse cx="0" cy="-60" rx="25" ry="60" fill="url(%23petals)" transform="rotate(225)"/><ellipse cx="0" cy="-60" rx="25" ry="60" fill="url(%23petals)" transform="rotate(270)"/><ellipse cx="0" cy="-60" rx="25" ry="60" fill="url(%23petals)" transform="rotate(315)"/><circle cx="0" cy="0" r="20" fill="%23F7F3E9"/></g><animateTransform attributeName="transform" type="rotate" values="0 200 200;360 200 200" dur="30s" repeatCount="indefinite"/></g></svg>');
            border-radius: 50%;
            opacity: 0.3;
            z-index: 1;
            animation: float 6s ease-in-out infinite;
        }}
        
        .decorative-elements {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 2;
        }}
        
        .decorative-elements::before {{
            content: '🌸';
            position: absolute;
            top: 20%;
            left: 10%;
            font-size: 3rem;
            animation: float 4s ease-in-out infinite;
            opacity: 0.7;
        }}
        
        .decorative-elements::after {{
            content: '🌿';
            position: absolute;
            top: 70%;
            right: 15%;
            font-size: 2.5rem;
            animation: float 5s ease-in-out infinite reverse;
            opacity: 0.7;
        }}
        
        .floating-petals {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            pointer-events: none;
        }}
        
        .petal {{
            position: absolute;
            background: var(--primary-rose);
            width: 10px;
            height: 10px;
            border-radius: 50% 0 50% 0;
            opacity: 0.6;
            animation: fall linear infinite;
        }}
        
        .petal:nth-child(1) {{ left: 10%; animation-duration: 15s; animation-delay: 0s; }}
        .petal:nth-child(2) {{ left: 20%; animation-duration: 20s; animation-delay: 2s; }}
        .petal:nth-child(3) {{ left: 30%; animation-duration: 18s; animation-delay: 4s; }}
        .petal:nth-child(4) {{ left: 40%; animation-duration: 22s; animation-delay: 6s; }}
        .petal:nth-child(5) {{ left: 50%; animation-duration: 16s; animation-delay: 8s; }}
        .petal:nth-child(6) {{ left: 60%; animation-duration: 19s; animation-delay: 10s; }}
        .petal:nth-child(7) {{ left: 70%; animation-duration: 21s; animation-delay: 12s; }}
        .petal:nth-child(8) {{ left: 80%; animation-duration: 17s; animation-delay: 14s; }}
        .petal:nth-child(9) {{ left: 90%; animation-duration: 23s; animation-delay: 16s; }}
        
        @keyframes fall {{
            0% {{
                transform: translateY(-100vh) rotate(0deg);
                opacity: 0;
            }}
            10% {{
                opacity: 0.6;
            }}
            90% {{
                opacity: 0.6;
            }}
            100% {{
                transform: translateY(100vh) rotate(360deg);
                opacity: 0;
            }}
        }}
        
        .hero h1 {{
            font-family: 'Playfair Display', serif;
            font-size: 4rem;
            font-weight: 300;
            margin-bottom: 1.5rem;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
            letter-spacing: 2px;
            position: relative;
            z-index: 2;
        }}
        
        .hero p {{
            font-size: 1.4rem;
            margin-bottom: 2.5rem;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
            font-weight: 300;
            position: relative;
            z-index: 2;
        }}
        
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, var(--accent-gold), var(--deep-sage));
            color: white;
            padding: 1.2rem 3rem;
            text-decoration: none;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 500;
            transition: all 0.4s ease;
            border: none;
            cursor: pointer;
            box-shadow: 0 8px 25px rgba(212, 184, 150, 0.4);
            position: relative;
            z-index: 2;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .cta-button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(212, 184, 150, 0.6);
            background: linear-gradient(135deg, var(--deep-sage), var(--accent-gold));
        }}
        
        /* Sections */
        section {{
            padding: 5rem 0;
            position: relative;
            overflow: hidden;
        }}
        
        section:nth-child(even) {{
            background: 
                radial-gradient(circle at 70% 30%, rgba(232, 180, 184, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 30% 70%, rgba(156, 175, 136, 0.05) 0%, transparent 50%),
                var(--pearl-white);
        }}
        
        section:nth-child(odd) {{
            background: 
                radial-gradient(circle at 80% 80%, rgba(212, 184, 150, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 20% 20%, rgba(230, 226, 243, 0.3) 0%, transparent 50%),
                transparent;
        }}
        
        section::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--primary-rose), var(--secondary-sage), var(--accent-gold), transparent);
            opacity: 0.3;
        }}
        
        h2 {{
            text-align: center;
            font-family: 'Playfair Display', serif;
            font-size: 3rem;
            font-weight: 400;
            margin-bottom: 4rem;
            color: var(--charcoal);
            position: relative;
        }}
        
        h2::after {{
            content: '';
            position: absolute;
            bottom: -15px;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 3px;
            background: linear-gradient(135deg, var(--primary-rose), var(--secondary-sage));
            border-radius: 2px;
        }}
        
        /* Services */
        #services {{
            background: 
                linear-gradient(rgba(247, 243, 233, 0.95), rgba(230, 226, 243, 0.95)),
                url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><defs><radialGradient id="sg1" cx="0.3" cy="0.3" r="0.4"><stop offset="0%" style="stop-color:%23E8B4B8;stop-opacity:0.2"/><stop offset="100%" style="stop-color:transparent"/></radialGradient><radialGradient id="sg2" cx="0.7" cy="0.7" r="0.3"><stop offset="0%" style="stop-color:%239CAF88;stop-opacity:0.15"/><stop offset="100%" style="stop-color:transparent"/></radialGradient></defs><rect width="800" height="600" fill="%23F7F3E9"/><circle cx="240" cy="180" r="160" fill="url(%23sg1)"/><circle cx="560" cy="420" r="120" fill="url(%23sg2)"/><path d="M0,300 Q200,200 400,300 T800,300" stroke="%23E8B4B8" stroke-width="1" fill="none" opacity="0.1"/><path d="M0,400 Q200,350 400,400 T800,400" stroke="%239CAF88" stroke-width="1" fill="none" opacity="0.1"/></svg>');
            background-size: cover;
            background-attachment: fixed;
        }}
        
        .services-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 3rem;
            margin-top: 3rem;
        }}
        
        .service-card {{
            background: linear-gradient(135deg, rgba(254, 254, 254, 0.95) 0%, rgba(247, 243, 233, 0.95) 100%);
            padding: 2.5rem;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            transition: all 0.4s ease;
            border: 1px solid rgba(232, 180, 184, 0.2);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }}
        
        .service-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(135deg, var(--primary-rose), var(--secondary-sage));
        }}
        
        .service-card::after {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(232, 180, 184, 0.1) 0%, transparent 70%);
            transform: scale(0);
            transition: transform 0.5s ease;
        }}
        
        .service-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            background: linear-gradient(135deg, rgba(247, 243, 233, 0.95) 0%, rgba(254, 254, 254, 0.95) 100%);
        }}
        
        .service-card:hover::after {{
            transform: scale(1);
        }}
        
        .service-icon {{
            font-size: 3.5rem;
            margin-bottom: 1.5rem;
            background: linear-gradient(135deg, var(--primary-rose), var(--secondary-sage));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .service-card h4 {{
            font-family: 'Playfair Display', serif;
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: var(--charcoal);
            font-weight: 600;
        }}
        
        .service-card p {{
            color: #666;
            margin-bottom: 1.5rem;
            line-height: 1.6;
        }}
        
        .service-price {{
            font-size: 1.8rem;
            font-weight: 600;
            color: var(--deep-sage);
            margin-top: 1rem;
        }}
        
        .service-duration {{
            color: var(--secondary-sage);
            margin-top: 0.5rem;
            font-style: italic;
        }}
        
        /* Staff */
        #staff {{
            background: 
                linear-gradient(rgba(254, 254, 254, 0.95), rgba(230, 226, 243, 0.95)),
                url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><defs><pattern id="hearts" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M20,15 C20,10 15,5 10,10 C5,5 0,10 0,15 C0,25 20,35 20,35 C20,35 40,25 40,15 C40,10 35,5 30,10 C25,5 20,10 20,15 Z" fill="%23E8B4B8" opacity="0.03"><animateTransform attributeName="transform" type="scale" values="1;1.1;1" dur="6s" repeatCount="indefinite"/></path></pattern></defs><rect width="800" height="600" fill="url(%23hearts)"/></svg>');
            background-size: cover;
        }}
        
        .staff-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 3rem;
            margin-top: 3rem;
        }}
        
        .staff-card {{
            background: linear-gradient(135deg, rgba(254, 254, 254, 0.95) 0%, rgba(230, 226, 243, 0.95) 100%);
            padding: 2.5rem;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }}
        
        .staff-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(135deg, var(--accent-gold), var(--eucalyptus));
        }}
        
        .staff-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        }}
        
        .staff-photo {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary-rose), var(--secondary-sage));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            margin: 0 auto 1.5rem;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }}
        
        .staff-card h4 {{
            font-family: 'Playfair Display', serif;
            font-size: 1.4rem;
            margin-bottom: 0.5rem;
            color: var(--charcoal);
            font-weight: 600;
        }}
        
        .staff-title {{
            color: var(--accent-gold);
            font-weight: 600;
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.9rem;
        }}
        
        .staff-specializations {{
            color: #666;
            margin-bottom: 2rem;
            font-style: italic;
            line-height: 1.5;
        }}
        
        .book-with-staff {{
            background: linear-gradient(135deg, var(--deep-sage), var(--eucalyptus));
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 30px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.9rem;
        }}
        
        .book-with-staff:hover {{
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(107, 142, 90, 0.4);
        }}
        
        /* Booking Modal */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.6);
            backdrop-filter: blur(5px);
        }}
        
        .modal-content {{
            background: linear-gradient(135deg, var(--pearl-white) 0%, var(--warm-cream) 100%);
            margin: 3% auto;
            padding: 3rem;
            border-radius: 25px;
            width: 90%;
            max-width: 600px;
            position: relative;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-height: 90vh;
            overflow-y: auto;
        }}
        
        .modal-content h2 {{
            font-family: 'Playfair Display', serif;
            color: var(--charcoal);
            margin-bottom: 2rem;
            text-align: center;
            font-size: 2.2rem;
        }}
        
        .close {{
            color: var(--charcoal);
            float: right;
            font-size: 32px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            background: rgba(232, 180, 184, 0.2);
        }}
        
        .close:hover {{
            background: var(--primary-rose);
            color: white;
            transform: rotate(90deg);
        }}
        
        .form-group {{
            margin-bottom: 2rem;
        }}
        
        .form-group label {{
            display: block;
            margin-bottom: 0.8rem;
            font-weight: 600;
            color: var(--charcoal);
            font-size: 1rem;
        }}
        
        .form-group input,
        .form-group select,
        .form-group textarea {{
            width: 100%;
            padding: 1rem;
            border: 2px solid rgba(232, 180, 184, 0.3);
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: var(--pearl-white);
            font-family: 'Lato', sans-serif;
        }}
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {{
            border-color: var(--primary-rose);
            outline: none;
            box-shadow: 0 0 0 3px rgba(232, 180, 184, 0.2);
            background: white;
        }}
        
        /* Contact */
        .contact-section {{
            background: linear-gradient(135deg, var(--primary-rose) 0%, var(--secondary-sage) 100%);
            color: white;
        }}
        
        .contact-section h2 {{
            color: white;
        }}
        
        .contact-section h2::after {{
            background: linear-gradient(135deg, white, var(--accent-gold));
        }}
        
        .contact-info {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 4rem;
            border-radius: 25px;
            margin: 2rem auto;
            max-width: 900px;
            text-align: center;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        .contact-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 3rem;
            margin-top: 2rem;
        }}
        
        .contact-item {{
            padding: 2rem;
            border-radius: 15px;
            background: linear-gradient(135deg, var(--warm-cream), var(--pearl-white));
            transition: transform 0.3s ease;
            border: 1px solid rgba(232, 180, 184, 0.2);
        }}
        
        .contact-item:hover {{
            transform: translateY(-5px);
        }}
        
        .contact-item i {{
            font-size: 2.5rem;
            color: var(--primary-rose);
            margin-bottom: 1rem;
        }}
        
        .contact-item h4 {{
            color: var(--charcoal);
            margin-bottom: 1rem;
            font-family: 'Playfair Display', serif;
            font-size: 1.3rem;
        }}
        
        .contact-item p {{
            color: #666;
            font-weight: 400;
        }}
        
        /* Gallery Section */
        .gallery-section {{
            background: var(--soft-lavender);
        }}
        
        .gallery-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }}
        
        .gallery-item {{
            height: 300px;
            border-radius: 20px;
            background: linear-gradient(135deg, var(--primary-rose), var(--secondary-sage));
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 3rem;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .gallery-item::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, transparent 40%, rgba(255,255,255,0.1) 50%, transparent 60%);
            transform: translateX(-100%);
            transition: transform 0.6s ease;
        }}
        
        .gallery-item:hover {{
            transform: scale(1.05);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        }}
        
        .gallery-item:hover::before {{
            transform: translateX(100%);
        }}
        
        /* Features Section */
        .features-section {{
            background: var(--pearl-white);
        }}
        
        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2.5rem;
            margin-top: 3rem;
        }}
        
        .feature-item {{
            text-align: center;
            padding: 2rem;
        }}
        
        .feature-icon {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--accent-gold), var(--eucalyptus));
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.5rem;
            color: white;
            font-size: 2rem;
            box-shadow: 0 10px 20px rgba(212, 184, 150, 0.3);
        }}
        
        .feature-item h4 {{
            font-family: 'Playfair Display', serif;
            color: var(--charcoal);
            margin-bottom: 1rem;
            font-size: 1.3rem;
        }}
        
        .feature-item p {{
            color: #666;
            line-height: 1.6;
        }}
        
        /* Footer */
        footer {{
            background: linear-gradient(135deg, var(--charcoal) 0%, var(--deep-sage) 100%);
            color: white;
            text-align: center;
            padding: 3rem 0;
            margin-top: 0;
            position: relative;
            overflow: hidden;
        }}
        
        footer::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--primary-rose), var(--secondary-sage), var(--accent-gold), transparent);
        }}
        
        .footer-content {{
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .footer-content p {{
            font-size: 1.1rem;
            margin-bottom: 1rem;
        }}
        
        .social-links {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 2rem;
        }}
        
        .social-links a {{
            color: white;
            font-size: 1.5rem;
            transition: all 0.3s ease;
            padding: 1rem;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.1);
        }}
        
        .social-links a:hover {{
            background: var(--primary-rose);
            transform: translateY(-3px);
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .hero h1 {{
                font-size: 2.8rem;
            }}
            
            nav ul {{
                display: none;
            }}
            
            .services-grid,
            .staff-grid {{
                grid-template-columns: 1fr;
            }}
            
            .modal-content {{
                margin: 10% auto;
                padding: 2rem;
            }}
            
            .contact-info {{
                padding: 2rem;
            }}
            
            .contact-grid {{
                grid-template-columns: 1fr;
                gap: 2rem;
            }}
        }}
        
        /* Animations */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes float {{
            0%, 100% {{
                transform: translateY(0px);
            }}
            50% {{
                transform: translateY(-10px);
            }}
        }}
        
        .fade-in {{
            animation: fadeInUp 0.8s ease-out;
        }}
        
        .float-animation {{
            animation: float 3s ease-in-out infinite;
        }}
        
        /* Scroll animations */
        .reveal {{
            opacity: 0;
            transform: translateY(50px);
            transition: all 0.6s ease;
        }}
        
        .reveal.active {{
            opacity: 1;
            transform: translateY(0);
        }}
    </style>
</head>
<body>
    <!-- Language Selector -->
    <div class="language-selector" id="languageSelector">
        <div class="language-label">
            <i class="fas fa-globe"></i> Language
        </div>
        <div class="language-options">
            <div class="language-option active" data-lang="en">
                <span class="flag">🇺🇸</span>
                <span class="language-name">English</span>
            </div>
            <div class="language-option" data-lang="es">
                <span class="flag">🇪🇸</span>
                <span class="language-name">Español</span>
            </div>
            <div class="language-option" data-lang="fr">
                <span class="flag">🇫🇷</span>
                <span class="language-name">Français</span>
            </div>
            <div class="language-option" data-lang="de">
                <span class="flag">🇩🇪</span>
                <span class="language-name">Deutsch</span>
            </div>
            <div class="language-option" data-lang="it">
                <span class="flag">🇮🇹</span>
                <span class="language-name">Italiano</span>
            </div>
        </div>
    </div>

    <!-- Translation Loading Overlay -->
    <div class="translation-loading" id="translationLoading">
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>Translating content...</p>
        </div>
    </div>

    <!-- Header -->
    <header>
        <nav class="container">
            <a href="#" class="logo">{salon_name}</a>
            <ul>
                <li><a href="#services">Services</a></li>
                <li><a href="#staff">Our Team</a></li>
                <li><a href="#contact">Contact</a></li>
                <li><a href="#" onclick="openBookingModal()">Book Now</a></li>
            </ul>
        </nav>
    </header>

    <!-- Hero Section -->
    <section class="hero">
        <div class="hero-image"></div>
        <div class="decorative-elements"></div>
        <div class="floating-petals">
            <div class="petal"></div>
            <div class="petal"></div>
            <div class="petal"></div>
            <div class="petal"></div>
            <div class="petal"></div>
            <div class="petal"></div>
            <div class="petal"></div>
            <div class="petal"></div>
            <div class="petal"></div>
        </div>
        <div class="container">
            <div class="hero-content">
                <h1 class="fade-in">✨ {salon_name} ✨</h1>
                <p class="fade-in">🌸 {description} 🌸</p>
                <p class="fade-in" style="font-size: 1.1rem; margin-bottom: 3rem; opacity: 0.9;">Experience the ultimate in relaxation and beauty at our serene sanctuary</p>
                <button class="cta-button fade-in" onclick="openBookingModal()">
                    <i class="fas fa-calendar-heart"></i> Book Your Spa Experience
                </button>
            </div>
        </div>
    </section>

    <!-- Services Section -->
    <section id="services" class="reveal">
        <div class="container">
            <h2>Our Signature Services</h2>
            <div class="services-grid">
                {services_html}
            </div>
        </div>
    </section>

    <!-- Gallery Section -->
    <section class="gallery-section reveal">
        <div class="container">
            <h2>Serene Spa Environment</h2>
            <div class="gallery-grid">
                <div class="gallery-item">
                    <i class="fas fa-spa"></i>
                </div>
                <div class="gallery-item">
                    <i class="fas fa-lotus"></i>
                </div>
                <div class="gallery-item">
                    <i class="fas fa-leaf"></i>
                </div>
                <div class="gallery-item">
                    <i class="fas fa-heart"></i>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="features-section reveal">
        <div class="container">
            <h2>Why Choose Us</h2>
            <div class="features-grid">
                <div class="feature-item">
                    <div class="feature-icon">
                        <i class="fas fa-certificate"></i>
                    </div>
                    <h4>Certified Professionals</h4>
                    <p>Our team consists of licensed and certified beauty professionals with years of experience.</p>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">
                        <i class="fas fa-leaf"></i>
                    </div>
                    <h4>Organic Products</h4>
                    <p>We use only the finest organic and natural products for all our treatments.</p>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">
                        <i class="fas fa-clock"></i>
                    </div>
                    <h4>Flexible Hours</h4>
                    <p>Open 7 days a week with extended hours to accommodate your busy schedule.</p>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <h4>Safe & Clean</h4>
                    <p>We maintain the highest standards of cleanliness and safety protocols.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Staff Section -->
    <section id="staff" class="reveal">
        <div class="container">
            <h2>Meet Our Expert Team</h2>
            <div class="staff-grid">
                {staff_html}
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="contact-section reveal">
        <div class="container">
            <h2>Visit Our Sanctuary</h2>
            <div class="contact-info">
                <div class="contact-grid">
                    <div class="contact-item">
                        <i class="fas fa-map-marker-alt"></i>
                        <h4>Location</h4>
                        <p>{address}</p>
                    </div>
                    <div class="contact-item">
                        <i class="fas fa-phone"></i>
                        <h4>Call Us</h4>
                        <p>{phone}</p>
                    </div>
                    <div class="contact-item">
                        <i class="fas fa-envelope"></i>
                        <h4>Email</h4>
                        <p>{email}</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Booking Modal -->
    <div id="bookingModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeBookingModal()">&times;</span>
            <h2>Book Your Appointment</h2>
            <form id="bookingForm">
                <div class="form-group">
                    <label for="clientName">Full Name *</label>
                    <input type="text" id="clientName" name="clientName" required>
                </div>
                
                <div class="form-group">
                    <label for="clientEmail">Email *</label>
                    <input type="email" id="clientEmail" name="clientEmail" required>
                </div>
                
                <div class="form-group">
                    <label for="clientPhone">Phone *</label>
                    <input type="tel" id="clientPhone" name="clientPhone" required>
                </div>
                
                <div class="form-group">
                    <label for="preferredStaff">Preferred Staff Member</label>
                    <select id="preferredStaff" name="preferredStaff">
                        <option value="">Any Available</option>
                        {self._generate_staff_options(staff_members)}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="serviceType">Service *</label>
                    <select id="serviceType" name="serviceType" required>
                        <option value="">Select a Service</option>
                        {self._generate_service_options(services)}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="appointmentDate">Preferred Date *</label>
                    <input type="date" id="appointmentDate" name="appointmentDate" required>
                </div>
                
                <div class="form-group">
                    <label for="appointmentTime">Preferred Time *</label>
                    <select id="appointmentTime" name="appointmentTime" required>
                        <option value="">Select Time</option>
                        <option value="09:00">9:00 AM</option>
                        <option value="10:00">10:00 AM</option>
                        <option value="11:00">11:00 AM</option>
                        <option value="12:00">12:00 PM</option>
                        <option value="13:00">1:00 PM</option>
                        <option value="14:00">2:00 PM</option>
                        <option value="15:00">3:00 PM</option>
                        <option value="16:00">4:00 PM</option>
                        <option value="17:00">5:00 PM</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="specialRequests">Special Requests</label>
                    <textarea id="specialRequests" name="specialRequests" rows="3" placeholder="Any special requests or notes..."></textarea>
                </div>
                
                <button type="submit" class="cta-button">Book Appointment</button>
            </form>
        </div>
    </div>

    <!-- Footer -->
    <footer>
        <div class="container">
            <div class="footer-content">
                <p>&copy; 2024 {salon_name}. All rights reserved.</p>
                <p>✨ Relax. Rejuvenate. Repeat. ✨</p>
                <div class="social-links">
                    <a href="#" title="Facebook"><i class="fab fa-facebook-f"></i></a>
                    <a href="#" title="Instagram"><i class="fab fa-instagram"></i></a>
                    <a href="#" title="Twitter"><i class="fab fa-twitter"></i></a>
                    <a href="#" title="Pinterest"><i class="fab fa-pinterest"></i></a>
                </div>
            </div>
        </div>
    </footer>

    <script>
        // Global variables
        let currentLanguage = 'en';
        let originalContent = {{}};
        let translatedContent = {{}};
        
        // Available languages
        const languages = {{
            'en': {{ name: 'English', native: 'English', flag: '🇺🇸' }},
            'es': {{ name: 'Spanish', native: 'Español', flag: '🇪🇸' }},
            'fr': {{ name: 'French', native: 'Français', flag: '🇫🇷' }},
            'de': {{ name: 'German', native: 'Deutsch', flag: '🇩🇪' }},
            'it': {{ name: 'Italian', native: 'Italiano', flag: '🇮🇹' }},
            'pt': {{ name: 'Portuguese', native: 'Português', flag: '🇵🇹' }}
        }};
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {{
            initializeTranslation();
            setupLanguageSelector();
        }});
        
        function initializeTranslation() {{
            // Store original content
            originalContent = {{
                salon_name: '{salon_name}',
                description: '{description}',
                hero_title: document.querySelector('.hero h1')?.textContent || '{salon_name}',
                hero_subtitle: document.querySelector('.hero p')?.textContent || '{description}',
                sections: {{
                    services: 'Our Signature Services',
                    gallery: 'Serene Spa Environment',
                    features: 'Why Choose Us',
                    staff: 'Meet Our Expert Team',
                    contact: 'Visit Our Sanctuary'
                }},
                features: [
                    'Certified Professionals',
                    'Organic Products', 
                    'Flexible Hours',
                    'Safe & Clean'
                ],
                buttons: {{
                    book_appointment: 'Book Your Appointment',
                    contact_us: 'Contact Us',
                    book_now: 'Book Now'
                }},
                contact: {{
                    location: 'Location',
                    call_us: 'Call Us', 
                    email: 'Email'
                }}
            }};
        }}
        
        function setupLanguageSelector() {{
            const languageOptions = document.querySelectorAll('.language-option');
            
            languageOptions.forEach(option => {{
                option.addEventListener('click', function() {{
                    const selectedLang = this.getAttribute('data-lang');
                    
                    if (selectedLang !== currentLanguage) {{
                        // Update active state
                        languageOptions.forEach(opt => opt.classList.remove('active'));
                        this.classList.add('active');
                        
                        // Change language
                        changeLanguage(selectedLang);
                    }}
                }});
            }});
        }}
        
        async function changeLanguage(targetLang) {{
            if (targetLang === currentLanguage) return;
            
            try {{
                showLoadingOverlay();
                
                // Get translations from cache or API
                if (!translatedContent[targetLang]) {{
                    const translations = await fetchTranslations(targetLang);
                    translatedContent[targetLang] = translations;
                }}
                
                // Apply translations
                applyTranslations(targetLang);
                currentLanguage = targetLang;
                
                // Update URL parameter
                const url = new URL(window.location);
                url.searchParams.set('lang', targetLang);
                window.history.replaceState({{}}, '', url);
                
            }} catch (error) {{
                console.error('Translation error:', error);
                alert('Translation failed. Please try again.');
            }} finally {{
                hideLoadingOverlay();
            }}
        }}
        
        async function fetchTranslations(targetLang) {{
            try {{
                // Use Netlify function for translation
                const response = await fetch('/.netlify/functions/spa-translate', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        content: originalContent,
                        target_lang: targetLang,
                        source_lang: 'en'
                    }})
                }});
                
                if (response.ok) {{
                    const data = await response.json();
                    return data.translated_content || {{}};
                }} else {{
                    // Fallback to basic translations
                    return getFallbackTranslations(targetLang);
                }}
            }} catch (error) {{
                console.error('API translation failed:', error);
                return getFallbackTranslations(targetLang);
            }}
        }}
        
        function getFallbackTranslations(targetLang) {{
            const fallbacks = {{
                'es': {{
                    sections: {{
                        services: 'Nuestros Servicios Exclusivos',
                        gallery: 'Ambiente Sereno del Spa',
                        features: 'Por Qué Elegirnos',
                        staff: 'Conoce a Nuestro Equipo Experto',
                        contact: 'Visita Nuestro Santuario'
                    }},
                    features: [
                        'Profesionales Certificados',
                        'Productos Orgánicos',
                        'Horarios Flexibles',
                        'Seguro y Limpio'
                    ],
                    buttons: {{
                        book_appointment: 'Reserve Su Cita',
                        contact_us: 'Contáctanos',
                        book_now: 'Reservar Ahora'
                    }},
                    contact: {{
                        location: 'Ubicación',
                        call_us: 'Llámanos',
                        email: 'Correo Electrónico'
                    }}
                }},
                'fr': {{
                    sections: {{
                        services: 'Nos Services Signature',
                        gallery: 'Environnement Spa Serein',
                        features: 'Pourquoi Nous Choisir',
                        staff: 'Rencontrez Notre Équipe Experte',
                        contact: 'Visitez Notre Sanctuaire'
                    }},
                    features: [
                        'Professionnels Certifiés',
                        'Produits Biologiques',
                        'Horaires Flexibles',
                        'Sûr et Propre'
                    ],
                    buttons: {{
                        book_appointment: 'Réservez Votre Rendez-vous',
                        contact_us: 'Contactez-nous',
                        book_now: 'Réserver Maintenant'
                    }},
                    contact: {{
                        location: 'Emplacement',
                        call_us: 'Appelez-nous',
                        email: 'E-mail'
                    }}
                }},
                'de': {{
                    sections: {{
                        services: 'Unsere Signature-Services',
                        gallery: 'Ruhige Spa-Umgebung',
                        features: 'Warum Uns Wählen',
                        staff: 'Lernen Sie Unser Expertenteam Kennen',
                        contact: 'Besuchen Sie Unser Heiligtum'
                    }},
                    features: [
                        'Zertifizierte Fachkräfte',
                        'Bio-Produkte',
                        'Flexible Zeiten',
                        'Sicher und Sauber'
                    ],
                    buttons: {{
                        book_appointment: 'Ihren Termin Buchen',
                        contact_us: 'Kontaktiere Uns',
                        book_now: 'Jetzt Buchen'
                    }},
                    contact: {{
                        location: 'Standort',
                        call_us: 'Rufen Sie Uns An',
                        email: 'E-Mail'
                    }}
                }},
                'it': {{
                    sections: {{
                        services: 'I Nostri Servizi Signature',
                        gallery: 'Ambiente Spa Sereno',
                        features: 'Perché Sceglierci',
                        staff: 'Incontra Il Nostro Team Esperto',
                        contact: 'Visita Il Nostro Santuario'
                    }},
                    features: [
                        'Professionisti Certificati',
                        'Prodotti Biologici',
                        'Orari Flessibili',
                        'Sicuro e Pulito'
                    ],
                    buttons: {{
                        book_appointment: 'Prenota Il Tuo Appuntamento',
                        contact_us: 'Contattaci',
                        book_now: 'Prenota Ora'
                    }},
                    contact: {{
                        location: 'Posizione',
                        call_us: 'Chiamaci',
                        email: 'Email'
                    }}
                }}
            }};
            
            return fallbacks[targetLang] || {{}};
        }}
        
        function applyTranslations(targetLang) {{
            const translations = translatedContent[targetLang];
            if (!translations) return;
            
            // Update section headings
            if (translations.sections) {{
                const serviceHeading = document.querySelector('#services h2');
                if (serviceHeading && translations.sections.services) {{
                    serviceHeading.textContent = translations.sections.services;
                }}
                
                const galleryHeading = document.querySelector('.gallery-section h2');
                if (galleryHeading && translations.sections.gallery) {{
                    galleryHeading.textContent = translations.sections.gallery;
                }}
                
                const featuresHeading = document.querySelector('.features-section h2');
                if (featuresHeading && translations.sections.features) {{
                    featuresHeading.textContent = translations.sections.features;
                }}
                
                const staffHeading = document.querySelector('#staff h2');
                if (staffHeading && translations.sections.staff) {{
                    staffHeading.textContent = translations.sections.staff;
                }}
                
                const contactHeading = document.querySelector('#contact h2');
                if (contactHeading && translations.sections.contact) {{
                    contactHeading.textContent = translations.sections.contact;
                }}
            }}
            
            // Update features
            if (translations.features) {{
                const featureItems = document.querySelectorAll('.feature-item h4');
                featureItems.forEach((item, index) => {{
                    if (translations.features[index]) {{
                        item.textContent = translations.features[index];
                    }}
                }});
            }}
            
            // Update buttons
            if (translations.buttons) {{
                const bookButtons = document.querySelectorAll('.cta-button');
                bookButtons.forEach(button => {{
                    if (button.textContent.includes('Book') || button.textContent.includes('Reserve')) {{
                        button.textContent = translations.buttons.book_appointment || translations.buttons.book_now;
                    }}
                }});
            }}
            
            // Update contact labels
            if (translations.contact) {{
                const contactItems = document.querySelectorAll('.contact-item h4');
                const contactLabels = ['location', 'call_us', 'email'];
                
                contactItems.forEach((item, index) => {{
                    if (translations.contact[contactLabels[index]]) {{
                        item.textContent = translations.contact[contactLabels[index]];
                    }}
                }});
            }}
        }}
        
        function showLoadingOverlay() {{
            document.getElementById('translationLoading').style.display = 'flex';
        }}
        
        function hideLoadingOverlay() {{
            document.getElementById('translationLoading').style.display = 'none';
        }}
        
        // Check URL for language parameter
        window.addEventListener('load', function() {{
            const urlParams = new URLSearchParams(window.location.search);
            const langParam = urlParams.get('lang');
            
            if (langParam && langParam !== 'en' && languages[langParam]) {{
                // Find and click the appropriate language option
                const langOption = document.querySelector(`[data-lang="${{langParam}}"]`);
                if (langOption) {{
                    langOption.click();
                }}
            }}
        }});
        // Booking Modal Functions
        function openBookingModal() {{
            document.getElementById('bookingModal').style.display = 'block';
            document.body.style.overflow = 'hidden';
        }}
        
        function closeBookingModal() {{
            document.getElementById('bookingModal').style.display = 'none';
            document.body.style.overflow = 'auto';
        }}
        
        // Close modal when clicking outside
        window.onclick = function(event) {{
            const modal = document.getElementById('bookingModal');
            if (event.target == modal) {{
                modal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }}
        }}
        
        // Book with specific staff
        document.querySelectorAll('.book-with-staff').forEach(button => {{
            button.addEventListener('click', function() {{
                const staffName = this.getAttribute('data-staff');
                openBookingModal();
                document.getElementById('preferredStaff').value = staffName;
            }});
        }});
        
        // Form submission with enhanced feedback
        document.getElementById('bookingForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            
            // Show loading state
            const submitButton = this.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Booking...';
            submitButton.disabled = true;
            
            const formData = new FormData(this);
            const appointmentData = Object.fromEntries(formData.entries());
            
            // Add salon info
            appointmentData.salon_id = '{salon_data.get('salon_id', '')}';
            appointmentData.salon_name = '{salon_name}';
            
            // Submit to Netlify function
            fetch('/.netlify/functions/spa-appointment-booking', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify(appointmentData)
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    // Success animation
                    submitButton.textContent = '✓ Booked!';
                    submitButton.style.background = 'linear-gradient(135deg, #4CAF50, #45a049)';
                    
                    setTimeout(() => {{
                        alert('🌸 Appointment request submitted successfully! We will contact you within 24 hours to confirm your booking. Thank you for choosing {salon_name}! 🌸');
                        closeBookingModal();
                        this.reset();
                        
                        // Reset button
                        submitButton.textContent = originalText;
                        submitButton.disabled = false;
                        submitButton.style.background = '';
                    }}, 1500);
                }} else {{
                    throw new Error('Booking failed');
                }}
            }})
            .catch(error => {{
                console.error('Error:', error);
                submitButton.textContent = 'Try Again';
                submitButton.disabled = false;
                alert('We apologize, but there was an issue with your booking request. Please try again or call us directly at {salon_data.get('phone_number', '')}.');
            }});
        }});
        
        // Set minimum date to today and maximum to 3 months ahead
        const today = new Date();
        const maxDate = new Date();
        maxDate.setMonth(maxDate.getMonth() + 3);
        
        document.getElementById('appointmentDate').min = today.toISOString().split('T')[0];
        document.getElementById('appointmentDate').max = maxDate.toISOString().split('T')[0];
        
        // Smooth scrolling for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}
            }});
        }});
        
        // Enhanced scroll reveal animations
        const revealElements = document.querySelectorAll('.reveal');
        
        const revealObserver = new IntersectionObserver(function(entries) {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.classList.add('active');
                    
                    // Add staggered animation for child elements
                    const children = entry.target.querySelectorAll('.service-card, .staff-card, .feature-item, .gallery-item');
                    children.forEach((child, index) => {{
                        setTimeout(() => {{
                            child.style.animation = `fadeInUp 0.6s ease-out ${{index * 0.1}}s both`;
                        }}, 100);
                    }});
                }}
            }});
        }}, {{
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        }});
        
        revealElements.forEach(element => {{
            revealObserver.observe(element);
        }});
        
        // Floating animation for service icons
        document.querySelectorAll('.service-icon').forEach(icon => {{
            icon.classList.add('float-animation');
        }});
        
        // Parallax effect for hero section
        window.addEventListener('scroll', function() {{
            const scrolled = window.pageYOffset;
            const hero = document.querySelector('.hero');
            if (hero) {{
                hero.style.transform = `translateY(${{scrolled * 0.5}}px)`;
            }}
        }});
        
        // Add loading animation to page
        window.addEventListener('load', function() {{
            document.body.style.opacity = '0';
            document.body.style.transition = 'opacity 0.5s ease';
            
            setTimeout(() => {{
                document.body.style.opacity = '1';
            }}, 100);
        }});
        
        // Service card hover effects
        document.querySelectorAll('.service-card').forEach(card => {{
            card.addEventListener('mouseenter', function() {{
                this.style.transform = 'translateY(-10px) scale(1.02)';
            }});
            
            card.addEventListener('mouseleave', function() {{
                this.style.transform = 'translateY(0) scale(1)';
            }});
        }});
        
        // Gallery item rotation effect
        document.querySelectorAll('.gallery-item').forEach(item => {{
            item.addEventListener('mouseenter', function() {{
                this.style.transform = 'scale(1.05) rotate(2deg)';
            }});
            
            item.addEventListener('mouseleave', function() {{
                this.style.transform = 'scale(1) rotate(0deg)';
            }});
        }});
        
        // Form validation enhancements
        const form = document.getElementById('bookingForm');
        const inputs = form.querySelectorAll('input[required], select[required]');
        
        inputs.forEach(input => {{
            input.addEventListener('blur', function() {{
                if (this.value.trim() === '') {{
                    this.style.borderColor = 'var(--primary-rose)';
                    this.style.boxShadow = '0 0 0 3px rgba(232, 180, 184, 0.3)';
                }} else {{
                    this.style.borderColor = 'var(--secondary-sage)';
                    this.style.boxShadow = '0 0 0 3px rgba(156, 175, 136, 0.3)';
                }}
            }});
        }});
        
        // Add sparkle effect to CTA button
        document.querySelectorAll('.cta-button').forEach(button => {{
            button.addEventListener('click', function(e) {{
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                ripple.style.position = 'absolute';
                ripple.style.borderRadius = '50%';
                ripple.style.background = 'rgba(255, 255, 255, 0.6)';
                ripple.style.transform = 'scale(0)';
                ripple.style.animation = 'ripple 0.6s linear';
                ripple.style.pointerEvents = 'none';
                
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(ripple);
                
                setTimeout(() => {{
                    ripple.remove();
                }}, 600);
            }});
        }});
        
        // Add ripple animation styles
        const style = document.createElement('style');
        style.textContent = `
            @keyframes ripple {{
                to {{
                    transform: scale(4);
                    opacity: 0;
                }}
            }}
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>'''
        
        return website_html
    
    def _generate_staff_options(self, staff_members: list) -> str:
        """Generate HTML options for staff selection"""
        options = ""
        for staff in staff_members:
            name = staff.get('name', 'Staff Member')
            options += f'<option value="{name}">{name}</option>'
        return options
    
    def _generate_service_options(self, services: list) -> str:
        """Generate HTML options for service selection"""
        options = ""
        for service in services:
            if isinstance(service, dict):
                name = service.get('name', 'Service')
                price = service.get('price', '50')
                duration = service.get('duration', '60')
                options += f'<option value="{name}">{name} - ${price} ({duration} min)</option>'
            else:
                options += f'<option value="{service}">{service}</option>'
        return options
    
    def _create_spa_netlify_functions(self, salon_data: dict) -> dict:
        """Create Netlify functions for spa functionality"""
        
        # Spa appointment booking function
        appointment_function = f'''exports.handler = async (event, context) => {{
    console.log('Spa appointment booking request received');
    
    if (event.httpMethod !== 'POST') {{
        return {{
            statusCode: 405,
            headers: {{
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            }},
            body: JSON.stringify({{ message: 'Method not allowed' }})
        }};
    }}
    
    try {{
        const appointmentData = JSON.parse(event.body);
        
        console.log('Appointment data:', appointmentData);
        
        // In a real implementation, save to database
        const appointmentDetails = {{
            salon_id: appointmentData.salon_id || '{salon_data.get('salon_id', '')}',
            salon_name: appointmentData.salon_name || '{salon_data.get('salon_name', 'Beauty Salon')}',
            client_name: appointmentData.clientName,
            client_email: appointmentData.clientEmail,
            client_phone: appointmentData.clientPhone,
            preferred_staff: appointmentData.preferredStaff,
            service_type: appointmentData.serviceType,
            appointment_date: appointmentData.appointmentDate,
            appointment_time: appointmentData.appointmentTime,
            special_requests: appointmentData.specialRequests,
            status: 'pending_confirmation',
            created_at: new Date().toISOString()
        }};
        
        // Here you would typically save to your database
        // and send confirmation emails
        
        return {{
            statusCode: 200,
            headers: {{
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            }},
            body: JSON.stringify({{
                success: true,
                message: 'Appointment request received successfully',
                appointment_id: `SPA_${{Date.now()}}`,
                appointment_details: appointmentDetails
            }})
        }};
        
    }} catch (error) {{
        console.error('Error processing appointment:', error);
        
        return {{
            statusCode: 200,
            headers: {{
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type'
            }},
            body: JSON.stringify({{
                success: true,
                message: 'Thank you for your appointment request. We will contact you within 24 hours to confirm your booking.',
                fallback: true
            }})
        }};
    }}
}};'''
        
        # Spa contact function
        contact_function = f'''exports.handler = async (event, context) => {{
    console.log('Spa contact form request received');
    
    if (event.httpMethod !== 'POST') {{
        return {{
            statusCode: 405,
            headers: {{
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            }},
            body: JSON.stringify({{ message: 'Method not allowed' }})
        }};
    }}
    
    try {{
        const contactData = JSON.parse(event.body);
        
        console.log('Contact form data:', contactData);
        
        return {{
            statusCode: 200,
            headers: {{
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type'
            }},
            body: JSON.stringify({{
                success: true,
                message: 'Thank you for contacting {salon_data.get('salon_name', 'our spa')}. We will respond within 24 hours.',
                spa_info: {{
                    salon_name: '{salon_data.get('salon_name', 'Beauty Salon')}',
                    phone: '{salon_data.get('phone_number', '')}',
                    email: '{salon_data.get('email_address', '')}',
                    address: '{salon_data.get('address', '')}'
                }}
            }})
        }};
        
    }} catch (error) {{
        console.error('Error processing contact form:', error);
        
        return {{
            statusCode: 200,
            headers: {{
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type'
            }},
            body: JSON.stringify({{
                success: true,
                message: 'Thank you for your interest in {salon_data.get('salon_name', 'our spa')}. Please call us at {salon_data.get('phone_number', '')} for immediate assistance.'
            }})
        }};
    }}
}};'''
        
        # Spa translation function
        spa_translate_function = f'''exports.handler = async (event, context) => {{
    console.log('Spa translation request received');
    
    if (event.httpMethod !== 'POST') {{
        return {{
            statusCode: 405,
            headers: {{
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            }},
            body: JSON.stringify({{ message: 'Method not allowed' }})
        }};
    }}
    
    try {{
        const {{ content, target_lang, source_lang }} = JSON.parse(event.body);
        
        console.log('Translation request:', {{ target_lang, source_lang }});
        
        // Fallback translations for spa content
        const translations = {{
            'es': {{
                sections: {{
                    services: 'Nuestros Servicios Exclusivos',
                    gallery: 'Ambiente Sereno del Spa',
                    features: 'Por Qué Elegirnos',
                    staff: 'Conoce a Nuestro Equipo Experto',
                    contact: 'Visita Nuestro Santuario'
                }},
                features: [
                    'Profesionales Certificados',
                    'Productos Orgánicos',
                    'Horarios Flexibles',
                    'Seguro y Limpio'
                ],
                buttons: {{
                    book_appointment: 'Reserve Su Cita',
                    contact_us: 'Contáctanos',
                    book_now: 'Reservar Ahora'
                }},
                contact: {{
                    location: 'Ubicación',
                    call_us: 'Llámanos',
                    email: 'Correo Electrónico'
                }}
            }},
            'fr': {{
                sections: {{
                    services: 'Nos Services Signature',
                    gallery: 'Environnement Spa Serein',
                    features: 'Pourquoi Nous Choisir',
                    staff: 'Rencontrez Notre Équipe Experte',
                    contact: 'Visitez Notre Sanctuaire'
                }},
                features: [
                    'Professionnels Certifiés',
                    'Produits Biologiques',
                    'Horaires Flexibles',
                    'Sûr et Propre'
                ],
                buttons: {{
                    book_appointment: 'Réservez Votre Rendez-vous',
                    contact_us: 'Contactez-nous',
                    book_now: 'Réserver Maintenant'
                }},
                contact: {{
                    location: 'Emplacement',
                    call_us: 'Appelez-nous',
                    email: 'E-mail'
                }}
            }},
            'de': {{
                sections: {{
                    services: 'Unsere Signature-Services',
                    gallery: 'Ruhige Spa-Umgebung',
                    features: 'Warum Uns Wählen',
                    staff: 'Lernen Sie Unser Expertenteam Kennen',
                    contact: 'Besuchen Sie Unser Heiligtum'
                }},
                features: [
                    'Zertifizierte Fachkräfte',
                    'Bio-Produkte',
                    'Flexible Zeiten',
                    'Sicher und Sauber'
                ],
                buttons: {{
                    book_appointment: 'Ihren Termin Buchen',
                    contact_us: 'Kontaktiere Uns',
                    book_now: 'Jetzt Buchen'
                }},
                contact: {{
                    location: 'Standort',
                    call_us: 'Rufen Sie Uns An',
                    email: 'E-Mail'
                }}
            }},
            'it': {{
                sections: {{
                    services: 'I Nostri Servizi Signature',
                    gallery: 'Ambiente Spa Sereno',
                    features: 'Perché Sceglierci',
                    staff: 'Incontra Il Nostro Team Esperto',
                    contact: 'Visita Il Nostro Santuario'
                }},
                features: [
                    'Professionisti Certificati',
                    'Prodotti Biologici',
                    'Orari Flessibili',
                    'Sicuro e Pulito'
                ],
                buttons: {{
                    book_appointment: 'Prenota Il Tuo Appuntamento',
                    contact_us: 'Contattaci',
                    book_now: 'Prenota Ora'
                }},
                contact: {{
                    location: 'Posizione',
                    call_us: 'Chiamaci',
                    email: 'Email'
                }}
            }},
            'pt': {{
                sections: {{
                    services: 'Nossos Serviços Exclusivos',
                    gallery: 'Ambiente Spa Sereno',
                    features: 'Por Que Nos Escolher',
                    staff: 'Conheça Nossa Equipe Especializada',
                    contact: 'Visite Nosso Santuário'
                }},
                features: [
                    'Profissionais Certificados',
                    'Produtos Orgânicos',
                    'Horários Flexíveis',
                    'Seguro e Limpo'
                ],
                buttons: {{
                    book_appointment: 'Reserve Seu Horário',
                    contact_us: 'Entre em Contato',
                    book_now: 'Reservar Agora'
                }},
                contact: {{
                    location: 'Localização',
                    call_us: 'Nos Ligue',
                    email: 'E-mail'
                }}
            }}
        }};
        
        const translated_content = translations[target_lang] || {{}};
        
        return {{
            statusCode: 200,
            headers: {{
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type'
            }},
            body: JSON.stringify({{
                success: true,
                translated_content,
                target_language: target_lang,
                message: 'Content translated successfully'
            }})
        }};
        
    }} catch (error) {{
        console.error('Translation error:', error);
        
        return {{
            statusCode: 200,
            headers: {{
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type'
            }},
            body: JSON.stringify({{
                success: false,
                message: 'Translation service temporarily unavailable',
                translated_content: {{}}
            }})
        }};
    }}
}};'''
        
        return {{
            'spa-appointment-booking.js': appointment_function,
            'spa-contact.js': contact_function,
            'spa-translate.js': spa_translate_function
        }}
    
    def _generate_spa_netlify_config(self, salon_data: dict) -> str:
        """Generate netlify.toml configuration for spa"""
        return f'''[build]
  functions = "netlify-functions"
  publish = "."

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[functions]
  directory = "netlify-functions"

# Spa-specific headers
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Content-Security-Policy = "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: https:; img-src 'self' data: https:; font-src 'self' data: https:"

# Spa appointment booking
[[headers]]
  for = "/.netlify/functions/spa-appointment-booking"
  [headers.values]
    Access-Control-Allow-Origin = "*"
    Access-Control-Allow-Headers = "Content-Type"
    Access-Control-Allow-Methods = "POST, OPTIONS"

# Spa contact
[[headers]]
  for = "/.netlify/functions/spa-contact"
  [headers.values]
    Access-Control-Allow-Origin = "*"
    Access-Control-Allow-Headers = "Content-Type"
    Access-Control-Allow-Methods = "POST, OPTIONS"

# Spa translation
[[headers]]
  for = "/.netlify/functions/spa-translate"
  [headers.values]
    Access-Control-Allow-Origin = "*"
    Access-Control-Allow-Headers = "Content-Type"
    Access-Control-Allow-Methods = "POST, OPTIONS"
'''
    
    def _organize_spa_files(self, salon_data: dict, website_content: str, netlify_functions: dict, netlify_config: str) -> dict:
        """Organize all spa website files"""
        
        files = {}
        
        # Main website file
        files['index.html'] = {
            'content': website_content,
            'type': 'html'
        }
        
        # Netlify configuration
        files['netlify.toml'] = {
            'content': netlify_config,
            'type': 'config'
        }
        
        # Netlify functions
        for func_name, func_content in netlify_functions.items():
            files[f'netlify-functions/{func_name}'] = {
                'content': func_content,
                'type': 'function'
            }
        
        # Package.json for functions
        package_json = {
            "name": f"{salon_data.get('salon_name', 'spa').lower().replace(' ', '-')}-functions",
            "version": "1.0.0",
            "description": "Netlify Functions for Spa Website",
            "main": "index.js",
            "scripts": {
                "test": "echo \"Error: no test specified\" && exit 1"
            },
            "dependencies": {},
            "author": "",
            "license": "ISC"
        }
        
        files['netlify-functions/package.json'] = {
            'content': json.dumps(package_json, indent=2),
            'type': 'config'
        }
        
        return files
    
    def _generate_staff_business_cards(self, salon_data: dict) -> list:
        """Generate business cards for all staff members"""
        try:
            business_cards = []
            staff_members = salon_data.get('staff_members', [])
            
            # Prepare business data for card generation
            business_data = {
                'business_id': salon_data.get('salon_id'),
                'business_name': salon_data.get('salon_name'),
                'salon_name': salon_data.get('salon_name'),
                'emailAddress': salon_data.get('email_address'),
                'email_address': salon_data.get('email_address'),
                'phoneNumber': salon_data.get('phone_number'),
                'phone_number': salon_data.get('phone_number'),
                'address': salon_data.get('address'),
                'city': salon_data.get('city'),
                'state': salon_data.get('state'),
                'zipCode': salon_data.get('zip_code'),
                'website_url': salon_data.get('website_url'),
                'description': salon_data.get('description', 'Professional Spa & Beauty Services'),
                'services': salon_data.get('services', [])
            }
            
            for staff in staff_members:
                try:
                    # Prepare person data
                    person_data = {
                        'name': staff.get('name', 'Staff Member'),
                        'title': staff.get('title', 'Beauty Specialist'),
                        'position': staff.get('title', 'Beauty Specialist'),
                        'email': staff.get('email', business_data.get('emailAddress')),
                        'specializations': staff.get('specializations', [])
                    }
                    
                    # Generate business card
                    card_result = self.card_generator.generate_business_card(
                        business_data, 
                        person_data, 
                        business_type='spa',
                        design_style='modern'
                    )
                    
                    if card_result.get('success'):
                        business_cards.append({
                            'staff_name': person_data['name'],
                            'staff_title': person_data['title'],
                            'front_image': card_result['front_image'],
                            'back_image': card_result['back_image'],
                            'card_id': card_result['card_id'],
                            'scan_stats': card_result.get('scan_stats', {}),
                            'qr_code_info': {
                                'total_scans': card_result.get('scan_stats', {}).get('total_scans', 0),
                                'today_scans': card_result.get('scan_stats', {}).get('today_scans', 0),
                                'last_scan': card_result.get('scan_stats', {}).get('last_scan_date')
                            }
                        })
                        
                        logger.info(f"Generated business card for {person_data['name']}")
                    
                except Exception as e:
                    logger.error(f"Error generating business card for {staff.get('name', 'staff')}: {e}")
                    continue
            
            logger.info(f"Generated {len(business_cards)} business cards for spa staff")
            return business_cards
            
        except Exception as e:
            logger.error(f"Error generating staff business cards: {e}")
            return []
    
    def deploy_spa_website_to_netlify(self, salon_data: dict, website_files: dict) -> dict:
        """Deploy spa website to Netlify"""
        try:
            salon_id = salon_data.get('salon_id')
            salon_name = salon_data.get('salon_name', 'Beauty Salon')
            
            # Create deployment directory
            deploy_dir = f"deploy_spa_{salon_id}_{int(datetime.now().timestamp())}"
            os.makedirs(deploy_dir, exist_ok=True)
            
            # Write all files
            for file_path, file_data in website_files.items():
                full_path = os.path.join(deploy_dir, file_path)
                
                # Create directory if needed
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Write file content
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(file_data['content'])
            
            logger.info(f"Spa website files created in: {deploy_dir}")
            
            # Deploy to Netlify
            try:
                website_url = self._deploy_spa_to_netlify(website_files, salon_id)
                
                # Generate QR code for the website
                qr_code_url = None
                if website_url:
                    qr_code_url = self._generate_qr_code(website_url, salon_id)
                
                # Get business cards from the spa creation result
                business_cards = []
                
                return {
                    "success": True,
                    "deployment_directory": deploy_dir,
                    "salon_name": salon_name,
                    "files_created": len(website_files),
                    "ready_for_netlify": True,
                    "website_url": website_url,
                    "qr_code_url": qr_code_url,
                    "netlify_deployed": website_url is not None,
                    "business_cards": business_cards,
                    "features": [
                        "Appointment Booking System",
                        "Staff Profiles with Business Cards",
                        "Service Catalog",
                        "Contact Forms",
                        "Responsive Design",
                        "Professional Spa Theme",
                        "Real-time QR Code Tracking"
                    ]
                }
                
            except Exception as deploy_error:
                logger.warning(f"Netlify deployment failed, but files created locally: {deploy_error}")
                business_cards = []
                
                return {
                    "success": True,
                    "deployment_directory": deploy_dir,
                    "salon_name": salon_name,
                    "files_created": len(website_files),
                    "ready_for_netlify": True,
                    "website_url": None,
                    "qr_code_url": None,
                    "netlify_deployed": False,
                    "business_cards": business_cards,
                    "features": [
                        "Appointment Booking System",
                        "Staff Profiles with Business Cards",
                        "Service Catalog",
                        "Contact Forms",
                        "Responsive Design",
                        "Professional Spa Theme",
                        "Real-time QR Code Tracking"
                    ]
                }
            
        except Exception as e:
            logger.error(f"Error deploying spa website: {e}")
            return {"success": False, "error": str(e)}

    def _deploy_spa_to_netlify(self, website_files: dict, salon_id: str) -> str:
        """Deploy spa website to Netlify with local fallback"""
        try:
            headers = {
                'Authorization': f'Bearer {self.netlify_token}',
                'Content-Type': 'application/json'
            }
            
            # Create a zip file with all website files
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add all website files
                for file_path, file_data in website_files.items():
                    zip_info = zipfile.ZipInfo(file_path)
                    zip_info.external_attr = 0o644 << 16
                    zip_file.writestr(zip_info, file_data['content'])
                
                # Add _headers file for proper content type
                headers_content = """/index.html
  Content-Type: text/html; charset=UTF-8

/*.js
  Content-Type: application/javascript; charset=UTF-8

/*.css
  Content-Type: text/css; charset=UTF-8

/.netlify/functions/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Headers: Content-Type
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
"""
                zip_file.writestr('_headers', headers_content)
            
            zip_buffer.seek(0)
            
            # Create site
            site_data = {
                'name': f'spa-{salon_id}-{int(datetime.now().timestamp())}',
                'custom_domain': None
            }
            
            response = requests.post(
                'https://api.netlify.com/api/v1/sites',
                headers=headers,
                json=site_data
            )
            
            if response.status_code == 422:
                # Usage limit exceeded, use local fallback
                logger.warning("Netlify usage limit exceeded, falling back to local deployment")
                return self._create_local_spa_website(website_files, salon_id)
            
            if response.status_code == 201:
                site_info = response.json()
                site_id = site_info['id']
                
                # Deploy files
                deploy_headers = {
                    'Authorization': f'Bearer {self.netlify_token}',
                    'Content-Type': 'application/zip'
                }
                
                deploy_response = requests.post(
                    f'https://api.netlify.com/api/v1/sites/{site_id}/deploys',
                    headers=deploy_headers,
                    data=zip_buffer.getvalue()
                )
                
                if deploy_response.status_code in [200, 201]:
                    deploy_info = deploy_response.json()
                    website_url = deploy_info.get('ssl_url') or deploy_info.get('url')
                    
                    logger.info(f"Spa website deployed successfully: {website_url}")
                    return website_url
                else:
                    logger.error(f"Deploy failed: {deploy_response.status_code} - {deploy_response.text}")
                    # Fallback to local deployment
                    return self._create_local_spa_website(website_files, salon_id)
            else:
                logger.error(f"Site creation failed: {response.status_code} - {response.text}")
                # Fallback to local deployment
                return self._create_local_spa_website(website_files, salon_id)
                
        except Exception as e:
            logger.error(f"Error deploying to Netlify: {e}")
            # Fallback to local deployment when Netlify fails
            return self._create_local_spa_website(website_files, salon_id)
    
    def _create_local_spa_website(self, website_files: dict, salon_id: str) -> str:
        """Create a local spa website when Netlify deployment fails"""
        try:
            import uuid
            
            # Generate a unique ID for the mock website
            site_id = str(uuid.uuid4())[:8]
            mock_domain = f"local-spa-{salon_id}-{site_id}"
            local_url = f"http://localhost:5000/static/websites/{mock_domain}/index.html"
            
            # Create the website directory structure
            website_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'websites', mock_domain)
            os.makedirs(website_dir, exist_ok=True)
            
            # Write all website files
            for file_path, file_data in website_files.items():
                full_path = os.path.join(website_dir, file_path)
                
                # Create directory if needed
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Write file content
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(file_data['content'])
            
            logger.info(f"✅ Created local spa website: {local_url}")
            return local_url
            
        except Exception as e:
            logger.error(f"Failed to create local spa website: {e}")
            return f"http://localhost:5000/static/spa-fallback.html"

    def _generate_qr_code(self, website_url: str, salon_id: str) -> str:
        """Generate QR code for the spa website"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(website_url)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color='black', back_color='white')
            
            # Save QR code
            qr_filename = f"spa_qr_{salon_id}.png"
            qr_path = os.path.join("static", "qr_codes", qr_filename)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(qr_path), exist_ok=True)
            
            qr_img.save(qr_path)
            
            # Return relative URL
            qr_url = f"/static/qr_codes/{qr_filename}"
            
            logger.info(f"Spa QR code generated: {qr_url}")
            return qr_url
            
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return None