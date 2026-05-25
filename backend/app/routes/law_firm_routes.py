"""
Law Firm website creation and management API routes
"""

from flask import Blueprint, request, jsonify, current_app, render_template_string, send_from_directory
from werkzeug.utils import secure_filename
import os
import uuid
import json
from datetime import datetime
import logging

from ..models.law_firm_model import LawFirmDataModel
from ..services.law_firm_integration_service import LawFirmIntegrationService
from ..utils.file_upload import handle_file_upload, allowed_file

logger = logging.getLogger(__name__)

law_firm_bp = Blueprint('law_firm', __name__)

# Global integration service (will be initialized with socketio in run.py)
integration_service = None

def init_law_firm_routes(socketio, mongo_client):
    """Initialize law firm routes with SocketIO and MongoDB client"""
    global integration_service
    integration_service = LawFirmIntegrationService(socketio, mongo_client)

@law_firm_bp.route('/law-firm-website-builder.html')
def serve_law_firm_builder():
    """Serve the law firm website builder form"""
    try:
        # Path to the law firm builder HTML file in templates
        template_path = os.path.join(current_app.root_path, '..', 'templates', 'law-firm-website-builder.html')
        
        with open(template_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
        
    except FileNotFoundError:
        logger.error(f"Law firm builder template not found at: {template_path}")
        return jsonify({"error": "Law firm builder form not found"}), 404
    except Exception as e:
        logger.error(f"Error serving law firm builder: {e}")
        return jsonify({"error": "Internal server error"}), 500

@law_firm_bp.route('/law-firm/create-website', methods=['POST'])
def create_law_firm_website_simple():
    """Simple law firm website creation endpoint for frontend integration"""
    try:
        if not integration_service:
            return jsonify({"success": False, "error": "Integration service not initialized"}), 500
        
        data = request.get_json()
        logger.info(f"Received law firm creation request with data: {data}")
        
        # Validate required fields
        if not data.get('website_name') or not data.get('business_email'):
            return jsonify({"success": False, "error": "Website name and business email are required"}), 400
        
        # Convert frontend data to law firm format
        years_exp = data.get('years_experience', 5)
        if isinstance(years_exp, str):
            try:
                years_exp = int(years_exp)
            except ValueError:
                years_exp = 5
        
        # Map frontend business card design to backend style
        business_card_mapping = {
            'modern': 'modern_gradient',
            'classic': 'classic_navy',
            'elegant': 'burgundy_gold',
            'corporate': 'forest_green',
            'creative': 'modern_black'
        }
        
        selected_design = data.get('business_card_design', 'modern')
        backend_design_style = business_card_mapping.get(selected_design, 'modern_gradient')
        
        # Convert frontend data to law firm format
        form_data = {
            'firmName': data.get('website_name'),
            'firmTagline': data.get('description', ''),
            'emailAddress': data.get('business_email'),
            'phoneNumber': data.get('business_phone', ''),
            'officeAddress': data.get('business_address', ''),
            'city': 'Unknown',
            'state': 'Unknown',
            'zipCode': '00000',
            'firmDescription': data.get('description', f"Professional legal services from {data.get('website_name')}"),
            'practiceAreas': data.get('practice_areas', ['General Practice', 'Civil Law', 'Business Law']),
            'attorneys': [{
                'name': data.get('attorney_name', 'Attorney Name'),
                'title': 'Attorney',
                'bio': data.get('attorney_bio', 'Experienced legal professional dedicated to serving clients with integrity and expertise.'),
                'education': 'Law Degree',
                'experience': str(years_exp),
                'email': data.get('business_email'),
                'phone': data.get('business_phone', ''),
                'photoUrl': ''
            }],
            'colorTheme': backend_design_style,  # Use mapped design style
            'heroMessage': f"Welcome to {data.get('website_name')} - Your Trusted Legal Partner",
            'enableBookingSync': True,
            'enableChatIntegration': True,
            'enableSentimentAnalysis': True,
            'generateBusinessCards': True
        }
        
        # Create complete law firm setup using integration service
        result = integration_service.create_complete_law_firm_setup(form_data)
        
        if result["success"]:
            business_cards = result.get("business_cards", [])
            website_data = result.get("website", {})
            
            # Get business card data properly
            business_card_url = None
            business_card_back_url = None
            
            if business_cards and len(business_cards) > 0:
                card = business_cards[0]
                business_card_url = card.get("front_image") or card.get("front_url")
                business_card_back_url = card.get("back_image") or card.get("back_url")
            
            return jsonify({
                "success": True,
                "message": "Professional law firm website created successfully",
                "firm_id": result["firm_id"],
                "website_url": website_data.get("website_url"),
                "netlify_url": website_data.get("website_url"),
                "business_card_url": business_card_url,
                "business_card_back_url": business_card_back_url,
                "business_card_design": selected_design,
                "business_cards": business_cards,  # Include full business card data
                "attorney_profile": website_data.get("attorney_profiles", []),
                "practice_areas": form_data['practiceAreas'],
                "qr_code_url": website_data.get("qr_code_url")
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to create law firm website")
            }), 500
            
    except Exception as e:
        logger.error(f"Error creating simple law firm website: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@law_firm_bp.route('/api/create-law-firm-website', methods=['POST'])
def create_law_firm_website():
    """Create a complete law firm website with all features using integration service"""
    try:
        if not integration_service:
            return jsonify({"success": False, "error": "Integration service not initialized"}), 500
        
        # Parse form data
        form_data = {}
        
        # Basic firm information
        form_data['firmName'] = request.form.get('firmName')
        form_data['firmTagline'] = request.form.get('firmTagline', '')
        form_data['yearsExperience'] = request.form.get('yearsExperience')
        form_data['clientsServed'] = request.form.get('clientsServed')
        form_data['firmDescription'] = request.form.get('firmDescription')
        
        # Contact information
        form_data['officeAddress'] = request.form.get('officeAddress')
        form_data['city'] = request.form.get('city')
        form_data['state'] = request.form.get('state')
        form_data['zipCode'] = request.form.get('zipCode')
        form_data['phoneNumber'] = request.form.get('phoneNumber')
        form_data['emailAddress'] = request.form.get('emailAddress')
        
        # Practice areas and services
        practice_areas = json.loads(request.form.get('practiceAreas', '[]'))
        form_data['practiceAreas'] = practice_areas
        form_data['additionalServices'] = request.form.get('additionalServices', '')
        
        # Attorney information
        attorneys = []
        attorney_count = int(request.form.get('attorneyCount', '0'))
        
        for i in range(attorney_count):
            attorney = {
                'name': request.form.get(f'attorney_{i}_name'),
                'title': request.form.get(f'attorney_{i}_title'),
                'bio': request.form.get(f'attorney_{i}_bio'),
                'education': request.form.get(f'attorney_{i}_education'),
                'experience': request.form.get(f'attorney_{i}_experience'),
                'email': request.form.get(f'attorney_{i}_email'),
                'phone': request.form.get(f'attorney_{i}_phone'),
                'photoUrl': request.form.get(f'attorney_{i}_photoUrl', '')
            }
            
            # Handle photo upload
            if f'attorney_{i}_photo' in request.files:
                photo_file = request.files[f'attorney_{i}_photo']
                if photo_file and photo_file.filename:
                    try:
                        filename = secure_filename(photo_file.filename)
                        upload_path = os.path.join('static', 'attorney_photos')
                        os.makedirs(upload_path, exist_ok=True)
                        
                        file_path = os.path.join(upload_path, f"{uuid.uuid4()}_{filename}")
                        photo_file.save(file_path)
                        attorney['photoUrl'] = f"/static/attorney_photos/{os.path.basename(file_path)}"
                    except Exception as e:
                        logger.error(f"Error uploading attorney photo: {e}")
            
            attorneys.append(attorney)
        
        form_data['attorneys'] = attorneys
        
        # Design customization
        form_data['colorTheme'] = request.form.get('colorTheme', 'blue')
        form_data['heroMessage'] = request.form.get('heroMessage', '')
        
        # Business integration settings
        form_data['enableBookingSync'] = request.form.get('enableBookingSync') == 'true'
        form_data['enableChatIntegration'] = request.form.get('enableChatIntegration') == 'true'
        form_data['enableSentimentAnalysis'] = request.form.get('enableSentimentAnalysis') == 'true'
        form_data['generateBusinessCards'] = request.form.get('generateBusinessCards') == 'true'
        
        # Validate required fields
        required_fields = ['firmName', 'city', 'state', 'phoneNumber', 'emailAddress']
        for field in required_fields:
            if not form_data.get(field):
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        # Create complete law firm setup using integration service
        result = integration_service.create_complete_law_firm_setup(form_data)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "message": "Law firm website and integrations created successfully",
                "firm_id": result["firm_id"],
                "website_url": result["website"].get("website_url"),
                "qr_code_url": result["website"].get("qr_code_url"),
                "business_cards": result["business_cards"],
                "dashboard_data": result["dashboard_data"]
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Unknown error occurred")
            }), 500
            
    except Exception as e:
        logger.error(f"Error creating law firm website: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
        form_data['additionalServices'] = request.form.get('additionalServices', '')
        
        # Attorneys
        attorneys_data = json.loads(request.form.get('attorneys', '[]'))
        
        # Handle attorney photo uploads
        for i, attorney in enumerate(attorneys_data):
            photo_key = f'attorneyPhoto_{i}'
            if photo_key in request.files:
                photo_file = request.files[photo_key]
                if photo_file and allowed_file(photo_file.filename):
                    photo_url = handle_file_upload(photo_file, 'attorney_photos')
                    attorney['photoUrl'] = photo_url
        
        form_data['attorneys'] = attorneys_data
        
        # Design and branding
        form_data['colorTheme'] = request.form.get('colorTheme', 'blue')
        form_data['heroMessage'] = request.form.get('heroMessage', '')
        
        # Handle logo upload
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and allowed_file(logo_file.filename):
                logo_url = handle_file_upload(logo_file, 'logos')
                form_data['logoUrl'] = logo_url
        
        # Business features
        form_data['enableBooking'] = request.form.get('enableBooking') == 'true'
        form_data['emailNotifications'] = request.form.get('emailNotifications') == 'true'
        form_data['weekdayHours'] = request.form.get('weekdayHours')
        form_data['weekendHours'] = request.form.get('weekendHours')
        form_data['enableNewsletter'] = request.form.get('enableNewsletter') == 'true'
        form_data['enableTestimonials'] = request.form.get('enableTestimonials') == 'true'
        form_data['enableBlog'] = request.form.get('enableBlog') == 'true'
        form_data['enableChat'] = request.form.get('enableChat') == 'true'
        
        # Create law firm in database
        create_result = law_firm_model.create_law_firm(form_data)
        if not create_result['success']:
            return jsonify({
                'success': False,
                'message': 'Failed to create law firm data'
            }), 500
        
        firm_id = create_result['firm_id']
        
        # Generate website
        website_generator = LawFirmWebsiteGenerator()
        website_result = website_generator.generate_website(firm_id, form_data)
        
        if not website_result['success']:
            return jsonify({
                'success': False,
                'message': 'Failed to generate website'
            }), 500
        
        # Update law firm with website URLs
        law_firm_model.update_website_info(
            firm_id,
            website_result['website_url'],
            website_result['qr_code_url']
        )
        
        # Generate business cards
        card_generator = BusinessCardGenerator()
        business_cards = card_generator.generate_cards(firm_id, form_data)
        
        logger.info(f"Law firm website created successfully: {firm_id}")
        
        return jsonify({
            'success': True,
            'firm_id': firm_id,
            'website_url': website_result['website_url'],
            'qr_code_url': website_result['qr_code_url'],
            'business_cards': business_cards,
            'message': 'Law firm website created successfully!'
        })
        
    except Exception as e:
        logger.error(f"Error creating law firm website: {e}")
        return jsonify({
            'success': False,
            'message': f'Error creating website: {str(e)}'
        }), 500

@law_firm_bp.route('/api/law-firm/<firm_id>/consultation/book', methods=['POST'])
def book_consultation(firm_id):
    """Book a consultation for a law firm using integration service"""
    try:
        if not integration_service:
            return jsonify({"success": False, "error": "Integration service not initialized"}), 500
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'date', 'time', 'legalMatter']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        # Process booking through integration service
        result = integration_service.handle_consultation_booking(firm_id, data)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "message": "Consultation booked successfully",
                "booking_id": result["booking_id"],
                "email_sent": result.get("email_sent", False),
                "dashboard_synced": result.get("dashboard_synced", False)
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to book consultation")
            }), 500
            
    except Exception as e:
        logger.error(f"Error booking consultation: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@law_firm_bp.route('/api/law-firm/<firm_id>/contact', methods=['POST'])
def handle_contact_form(firm_id):
    """Handle contact form submissions from law firm website using integration service"""
    try:
        if not integration_service:
            return jsonify({"success": False, "error": "Integration service not initialized"}), 500
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        # Process contact inquiry through integration service
        result = integration_service.handle_contact_inquiry(firm_id, data)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "message": "Contact form submitted successfully",
                "inquiry_id": result["inquiry_id"],
                "email_sent": result.get("email_sent", False),
                "chat_connected": result.get("chat_connected", False)
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to submit contact form")
            }), 500
            
    except Exception as e:
        logger.error(f"Error handling contact form: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
        
    except Exception as e:
        logger.error(f"Error handling contact form: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to submit contact form'
        }), 500

@law_firm_bp.route('/api/law-firm/<firm_id>/feedback', methods=['POST'])
def submit_feedback(firm_id):
    """Handle feedback submissions from law firm website using integration service"""
    try:
        if not integration_service:
            return jsonify({"success": False, "error": "Integration service not initialized"}), 500
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'rating', 'feedback']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        # Process feedback through integration service
        result = integration_service.handle_feedback_submission(firm_id, data)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "message": "Feedback submitted successfully",
                "feedback_id": result["feedback_id"],
                "sentiment_analysis": result.get("sentiment_analysis", {})
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to submit feedback")
            }), 500
            
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@law_firm_bp.route('/api/law-firm/<firm_id>/newsletter/subscribe', methods=['POST'])
def subscribe_newsletter(firm_id):
    """Handle newsletter subscription from law firm website using integration service"""
    try:
        data = request.get_json()
        
        if not integration_service:
            return jsonify({"success": False, "error": "Integration service not initialized"}), 500
        
        # Process newsletter subscription through integration service
        result = integration_service.handle_newsletter_subscription(firm_id, data)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "message": "Successfully subscribed to newsletter",
                "subscription_id": result["subscription_id"]
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to subscribe to newsletter")
            }), 500
            
    except Exception as e:
        logger.error(f"Error subscribing to newsletter: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@law_firm_bp.route('/api/law-firm/<firm_id>/dashboard', methods=['GET'])
def get_firm_dashboard(firm_id):
    """Get dashboard data for law firm using integration service"""
    try:
        if not integration_service:
            return jsonify({"success": False, "error": "Integration service not initialized"}), 500
        
        # Get comprehensive dashboard data through integration service
        result = integration_service.get_firm_dashboard_data(firm_id)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "dashboard_data": result["dashboard_data"]
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to get dashboard data")
            }), 404 if "not found" in result.get("error", "").lower() else 500
            
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@law_firm_bp.route('/api/law-firm/<firm_id>/business-cards', methods=['GET'])
def get_business_cards(firm_id):
    """Get business cards for law firm attorneys"""
    try:
        if not integration_service:
            return jsonify({"success": False, "error": "Integration service not initialized"}), 500
        
        # Get firm dashboard data which includes business card information
        result = integration_service.get_firm_dashboard_data(firm_id)
        
        if result["success"]:
            firm_data = result["dashboard_data"]["firm_info"]
            
            # Generate business cards if needed
            card_generator = integration_service.card_generator
            cards_result = card_generator.batch_generate_cards(firm_data)
            
            return jsonify({
                "success": True,
                "business_cards": cards_result.get("cards", []),
                "design_style": cards_result.get("design_style", "classic_navy")
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to get firm data")
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting business cards: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Integration helper functions for real-time notifications
def send_dashboard_notification(firm_id: str, event_type: str, data: dict):
    """Send notification to main dashboard - Legacy function, now handled by integration service"""
    logger.info(f"Legacy dashboard notification for firm {firm_id}: {event_type}")

def send_chat_message(firm_id: str, message_data: dict):
    """Send message to main website chat system"""
    try:
        from app import socketio
        
        # Emit to chat system
        socketio.emit('law_firm_chat_message', {
            'firm_id': firm_id,
            'message': message_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room='chat')
        
        logger.info(f"Chat message sent for firm {firm_id}")
        
    except Exception as e:
        logger.error(f"Error sending chat message: {e}")

def send_sentiment_analysis(firm_id: str, feedback_data: dict):
    """Send feedback for sentiment analysis"""
    try:
        from app import socketio
        
        # Emit to sentiment analysis system
        socketio.emit('law_firm_feedback', {
            'firm_id': firm_id,
            'feedback': feedback_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room='sentiment_analysis')
        
        logger.info(f"Sentiment analysis data sent for firm {firm_id}")
        
    except Exception as e:
        logger.error(f"Error sending sentiment analysis data: {e}")