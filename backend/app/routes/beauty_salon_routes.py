"""
Beauty Salon/Spa API Routes - Complete backend integration for spa functionality
"""

from flask import Blueprint, request, jsonify, current_app
import logging
from datetime import datetime
import traceback

# Import beauty salon services
from app.services.beauty_salon_integration_service import BeautySalonIntegrationService
from app.services.beauty_salon_business_card_generator import BeautySalonBusinessCardGenerator
from app.services.beauty_salon_website_generator import BeautySalonWebsiteGenerator
from app.models.beauty_salon_model import BeautySalonDataModel

logger = logging.getLogger(__name__)

# Create Blueprint
beauty_salon_bp = Blueprint('beauty_salon', __name__, url_prefix='/api/beauty-salon')

# Initialize services (will be set up in init function)
integration_service = None
card_generator = BeautySalonBusinessCardGenerator()
website_generator = BeautySalonWebsiteGenerator()
data_model = None

def init_beauty_salon_routes(socketio, mongo_client):
    """Initialize beauty salon routes with required dependencies"""
    global integration_service, data_model
    integration_service = BeautySalonIntegrationService(socketio, mongo_client)
    data_model = BeautySalonDataModel(mongo_client)

@beauty_salon_bp.route('/create-complete-salon', methods=['POST'])
def create_complete_salon():
    """Create a complete beauty salon with all features"""
    try:
        logger.info("Creating complete beauty salon...")
        
        if integration_service is None:
            return jsonify({
                "success": False,
                "error": "Beauty salon service not initialized"
            }), 500
        
        salon_data = request.get_json()
        
        if not salon_data:
            return jsonify({
                "success": False,
                "error": "No salon data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['salon_name', 'owner_name', 'email_address']
        missing_fields = [field for field in required_fields if not salon_data.get(field)]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Create complete salon setup
        result = integration_service.create_complete_salon_setup(salon_data)
        
        if result.get('success'):
            logger.info(f"Complete salon created successfully: {result.get('salon_id')}")
            return jsonify(result), 200
        else:
            logger.error(f"Failed to create salon: {result.get('error')}")
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error in create_complete_salon: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": "Internal server error creating salon"
        }), 500

@beauty_salon_bp.route('/generate-spa-website', methods=['POST'])
def generate_spa_website():
    """Generate a beautiful spa website"""
    try:
        logger.info("Generating spa website...")
        
        salon_data = request.get_json()
        
        if not salon_data:
            return jsonify({
                "success": False,
                "error": "No salon data provided"
            }), 400
        
        # Generate website
        result = website_generator.create_complete_spa_website(salon_data)
        
        if result.get('success'):
            # Deploy to Netlify
            deploy_result = website_generator.deploy_spa_website_to_netlify(
                salon_data, result.get('website_files', {})
            )
            
            # Combine results
            combined_result = {
                **result,
                "deployment": deploy_result
            }
            
            logger.info(f"Spa website generated and deployed: {salon_data.get('salon_name')}")
            return jsonify(combined_result), 200
        else:
            logger.error(f"Failed to generate spa website: {result.get('error')}")
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error in generate_spa_website: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": "Internal server error generating website"
        }), 500

@beauty_salon_bp.route('/generate-spa-business-cards', methods=['POST'])
def generate_spa_business_cards():
    """Generate beautiful spa business cards for all staff"""
    try:
        logger.info("Generating spa business cards...")
        
        salon_data = request.get_json()
        
        if not salon_data:
            return jsonify({
                "success": False,
                "error": "No salon data provided"
            }), 400
        
        # Generate business cards
        result = card_generator.batch_generate_cards(salon_data)
        
        if result.get('success'):
            logger.info(f"Spa business cards generated: {result.get('total_cards')} cards")
            return jsonify(result), 200
        else:
            logger.error(f"Failed to generate spa business cards: {result.get('error')}")
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error in generate_spa_business_cards: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": "Internal server error generating business cards"
        }), 500

@beauty_salon_bp.route('/book-appointment', methods=['POST'])
def book_appointment():
    """Book an appointment at the spa"""
    try:
        logger.info("Processing spa appointment booking...")
        
        if integration_service is None:
            return jsonify({
                "success": False,
                "error": "Beauty salon service not initialized"
            }), 500
        
        appointment_data = request.get_json()
        
        if not appointment_data:
            return jsonify({
                "success": False,
                "error": "No appointment data provided"
            }), 400
        
        # Process appointment booking
        result = integration_service.process_appointment_booking(appointment_data)
        
        if result.get('success'):
            logger.info(f"Appointment booked successfully: {result.get('appointment_id')}")
            return jsonify(result), 200
        else:
            logger.error(f"Failed to book appointment: {result.get('error')}")
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error in book_appointment: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": "Internal server error booking appointment"
        }), 500

@beauty_salon_bp.route('/get-salon-info/<salon_id>', methods=['GET'])
def get_salon_info(salon_id):
    """Get complete salon information"""
    try:
        logger.info(f"Getting salon info for: {salon_id}")
        
        if data_model is None:
            return jsonify({
                "success": False,
                "error": "Beauty salon data service not initialized"
            }), 500
        
        # Get salon data
        salon_data = data_model.get_beauty_salon(salon_id)
        
        if salon_data:
            logger.info(f"Salon info retrieved: {salon_data.get('salon_name')}")
            return jsonify({
                "success": True,
                "salon_data": salon_data
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Salon not found"
            }), 404
            
    except Exception as e:
        logger.error(f"Error in get_salon_info: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": "Internal server error getting salon info"
        }), 500

@beauty_salon_bp.route('/get-staff-availability', methods=['POST'])
def get_staff_availability():
    """Get staff availability for appointment booking"""
    try:
        logger.info("Getting staff availability...")
        
        if data_model is None:
            return jsonify({
                "success": False,
                "error": "Beauty salon data service not initialized"
            }), 500
        
        request_data = request.get_json()
        salon_id = request_data.get('salon_id')
        date = request_data.get('date')
        
        if not salon_id or not date:
            return jsonify({
                "success": False,
                "error": "salon_id and date are required"
            }), 400
        
        # Get availability
        availability = data_model.get_staff_availability(salon_id, date)
        
        logger.info(f"Staff availability retrieved for {salon_id} on {date}")
        return jsonify({
            "success": True,
            "availability": availability,
            "date": date
        }), 200
            
    except Exception as e:
        logger.error(f"Error in get_staff_availability: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": "Internal server error getting availability"
        }), 500

@beauty_salon_bp.route('/get-services/<salon_id>', methods=['GET'])
def get_services(salon_id):
    """Get all services offered by the salon"""
    try:
        logger.info(f"Getting services for salon: {salon_id}")
        
        # Get services
        services = data_model.get_salon_services(salon_id)
        
        if services is not None:
            logger.info(f"Services retrieved: {len(services)} services")
            return jsonify({
                "success": True,
                "services": services,
                "salon_id": salon_id
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Salon not found or no services available"
            }), 404
            
    except Exception as e:
        logger.error(f"Error in get_services: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": "Internal server error getting services"
        }), 500

@beauty_salon_bp.route('/get-staff/<salon_id>', methods=['GET'])
def get_staff(salon_id):
    """Get all staff members for the salon"""
    try:
        logger.info(f"Getting staff for salon: {salon_id}")
        
        # Get staff
        staff = data_model.get_salon_staff(salon_id)
        
        if staff is not None:
            logger.info(f"Staff retrieved: {len(staff)} staff members")
            return jsonify({
                "success": True,
                "staff": staff,
                "salon_id": salon_id
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Salon not found or no staff available"
            }), 404
            
    except Exception as e:
        logger.error(f"Error in get_staff: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": "Internal server error getting staff"
        }), 500

@beauty_salon_bp.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    """Submit client feedback/review"""
    try:
        logger.info("Processing client feedback...")
        
        if integration_service is None:
            return jsonify({
                "success": False,
                "error": "Beauty salon service not initialized"
            }), 500
        
        feedback_data = request.get_json()
        
        if not feedback_data:
            return jsonify({
                "success": False,
                "error": "No feedback data provided"
            }), 400
        
        # Process feedback
        result = integration_service.process_client_feedback(feedback_data)
        
        if result.get('success'):
            logger.info(f"Feedback submitted successfully: {result.get('feedback_id')}")
            return jsonify(result), 200
        else:
            logger.error(f"Failed to submit feedback: {result.get('error')}")
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error in submit_feedback: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": "Internal server error submitting feedback"
        }), 500

@beauty_salon_bp.route('/get-appointments/<salon_id>', methods=['GET'])
def get_appointments(salon_id):
    """Get all appointments for salon (admin view)"""
    try:
        logger.info(f"Getting appointments for salon: {salon_id}")
        
        # Get optional date filter
        date_filter = request.args.get('date')
        
        # Get appointments
        appointments = data_model.get_salon_appointments(salon_id, date_filter)
        
        if appointments is not None:
            logger.info(f"Appointments retrieved: {len(appointments)} appointments")
            return jsonify({
                "success": True,
                "appointments": appointments,
                "salon_id": salon_id,
                "date_filter": date_filter
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Salon not found"
            }), 404
            
    except Exception as e:
        logger.error(f"Error in get_appointments: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": "Internal server error getting appointments"
        }), 500

@beauty_salon_bp.route('/update-appointment-status', methods=['PUT'])
def update_appointment_status():
    """Update appointment status (confirm, cancel, etc.)"""
    try:
        logger.info("Updating appointment status...")
        
        update_data = request.get_json()
        
        if not update_data:
            return jsonify({
                "success": False,
                "error": "No update data provided"
            }), 400
        
        appointment_id = update_data.get('appointment_id')
        new_status = update_data.get('status')
        
        if not appointment_id or not new_status:
            return jsonify({
                "success": False,
                "error": "appointment_id and status are required"
            }), 400
        
        # Update appointment
        result = data_model.update_appointment_status(appointment_id, new_status)
        
        if result:
            logger.info(f"Appointment status updated: {appointment_id} -> {new_status}")
            return jsonify({
                "success": True,
                "appointment_id": appointment_id,
                "new_status": new_status
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Appointment not found or update failed"
            }), 404
            
    except Exception as e:
        logger.error(f"Error in update_appointment_status: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": "Internal server error updating appointment"
        }), 500

@beauty_salon_bp.route('/get-salon-analytics/<salon_id>', methods=['GET'])
def get_salon_analytics(salon_id):
    """Get salon analytics and performance metrics"""
    try:
        logger.info(f"Getting analytics for salon: {salon_id}")
        
        if integration_service is None:
            return jsonify({
                "success": False,
                "error": "Beauty salon service not initialized"
            }), 500
        
        # Get analytics
        analytics = integration_service.get_salon_analytics(salon_id)
        
        if analytics.get('success'):
            logger.info(f"Analytics retrieved for salon: {salon_id}")
            return jsonify(analytics), 200
        else:
            logger.error(f"Failed to get analytics: {analytics.get('error')}")
            return jsonify(analytics), 500
            
    except Exception as e:
        logger.error(f"Error in get_salon_analytics: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": "Internal server error getting analytics"
        }), 500

# Error handlers
@beauty_salon_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@beauty_salon_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "Method not allowed"
    }), 405

@beauty_salon_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

# Health check
@beauty_salon_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "success": True,
        "message": "Beauty Salon API is healthy",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/create-complete-salon",
            "/generate-spa-website", 
            "/generate-spa-business-cards",
            "/book-appointment",
            "/get-salon-info/<salon_id>",
            "/get-staff-availability",
            "/get-services/<salon_id>",
            "/get-staff/<salon_id>",
            "/submit-feedback",
            "/get-appointments/<salon_id>",
            "/update-appointment-status",
            "/get-salon-analytics/<salon_id>"
        ]
    }), 200