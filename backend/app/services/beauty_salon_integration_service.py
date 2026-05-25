"""
Beauty Salon/Spa Integration Service - Complete spa website creation with booking
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
import asyncio

from ..models.beauty_salon_model import BeautySalonDataModel
from ..services.beauty_salon_website_generator import BeautySalonWebsiteGenerator
from ..services.beauty_salon_business_card_generator import BeautySalonBusinessCardGenerator
from ..services.beauty_salon_booking_service import BeautySalonBookingService
from ..services.beauty_salon_email_service import BeautySalonEmailService

logger = logging.getLogger(__name__)

class BeautySalonIntegrationService:
    """Complete beauty salon/spa integration service"""
    
    def __init__(self, socketio, mongo_client):
        self.socketio = socketio
        self.mongo_client = mongo_client
        # Initialize services
        self.data_model = BeautySalonDataModel(mongo_client)
        self.salon_model = self.data_model  # Alias for backward compatibility
        self.website_generator = BeautySalonWebsiteGenerator()
        self.business_card_generator = BeautySalonBusinessCardGenerator()
        self.booking_service = BeautySalonBookingService()
        self.email_service = BeautySalonEmailService()
        
    def create_complete_salon_setup(self, salon_data: dict) -> dict:
        """Create complete beauty salon setup with website, booking, and business cards"""
        try:
            logger.info("Starting complete beauty salon setup")
            
            # Generate unique salon ID
            salon_id = str(uuid.uuid4())
            
            # 1. Create salon in database
            salon_creation_result = self._create_salon_database_entry(salon_id, salon_data)
            if not salon_creation_result["success"]:
                return salon_creation_result
            
            # 2. Generate website
            website_result = self._generate_salon_website(salon_id, salon_data)
            
            # 3. Generate business cards for staff
            business_cards_result = self._generate_business_cards(salon_id, salon_data)
            
            # 4. Set up booking integration
            booking_setup_result = self._setup_booking_integration(salon_id, salon_data)
            
            # 5. Set up email automation
            email_setup_result = self._setup_email_automation(salon_id, salon_data)
            
            # 6. Emit real-time notifications
            self._emit_setup_notifications(salon_id, {
                "website": website_result,
                "booking": booking_setup_result,
                "business_cards": business_cards_result
            })
            
            logger.info(f"Complete beauty salon setup finished for {salon_id}")
            
            return {
                "success": True,
                "salon_id": salon_id,
                "website": website_result,
                "business_cards": business_cards_result.get("cards", []),
                "booking_system": booking_setup_result,
                "email_automation": email_setup_result,
                "dashboard_data": self._get_salon_dashboard_data(salon_id)
            }
            
        except Exception as e:
            logger.error(f"Error in complete salon setup: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_salon_database_entry(self, salon_id: str, salon_data: dict) -> dict:
        """Create salon entry in database"""
        try:
            # Process staff data
            staff_members = []
            for staff in salon_data.get('staff_members', []):
                staff_id = str(uuid.uuid4())
                
                staff_entry = {
                    "staff_id": staff_id,
                    "name": staff.get('name'),
                    "title": staff.get('title'),
                    "specializations": staff.get('specializations', []),
                    "experience": staff.get('experience'),
                    "bio": staff.get('bio'),
                    "photo_url": staff.get('photo_url', ''),
                    "certifications": staff.get('certifications', []),
                    "available_services": staff.get('available_services', []),
                    "working_hours": staff.get('working_hours', {}),
                    "created_at": datetime.utcnow()
                }
                
                # Create staff member in database
                staff_creation = self.salon_model.create_staff_member(staff_entry)
                if staff_creation['success']:
                    staff_members.append({**staff_entry, "staff_id": staff_creation['staff_id']})
                    logger.info(f"Staff member created: {staff_creation['staff_id']}")
                else:
                    logger.error(f"Failed to create staff member: {staff.get('name')}")
            
            # Create main salon data
            salon_info = {
                "salon_id": salon_id,
                "salon_name": salon_data.get('salon_name'),
                "salon_tagline": salon_data.get('salon_tagline', ''),
                "description": salon_data.get('description'),
                "services": salon_data.get('services', []),
                "contact": {
                    "phone_number": salon_data.get('phone_number'),
                    "email_address": salon_data.get('email_address'),
                    "address": salon_data.get('address'),
                    "city": salon_data.get('city'),
                    "state": salon_data.get('state'),
                    "zip_code": salon_data.get('zip_code')
                },
                "business_hours": salon_data.get('business_hours', {}),
                "staff_members": staff_members,
                "pricing": salon_data.get('pricing', {}),
                "packages": salon_data.get('packages', []),
                "social_media": salon_data.get('social_media', {}),
                "specialties": salon_data.get('specialties', []),
                "years_in_business": salon_data.get('years_in_business', 1),
                "client_capacity": salon_data.get('client_capacity', 50),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create salon in database
            creation_result = self.salon_model.create_beauty_salon(salon_info)
            
            return creation_result
            
        except Exception as e:
            logger.error(f"Error creating salon database entry: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_salon_website(self, salon_id: str, salon_data: dict) -> dict:
        """Generate beauty salon website"""
        try:
            logger.info(f"Generating website for salon {salon_id}")
            
            # Generate website using salon website generator
            website_result = self.website_generator.generate_website(salon_id, salon_data)
            
            if website_result.get("success"):
                # Update salon with website info
                self.salon_model.update_website_info(
                    salon_id, 
                    website_result.get("website_url"),
                    website_result.get("qr_code_url")
                )
                
                logger.info(f"Website generated successfully for salon {salon_id}")
                
            return website_result
            
        except Exception as e:
            logger.error(f"Error generating salon website: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_business_cards(self, salon_id: str, salon_data: dict) -> dict:
        """Generate business cards for salon staff"""
        try:
            logger.info(f"Generating business cards for salon {salon_id}")
            
            cards_result = self.business_card_generator.batch_generate_cards(salon_data)
            
            return cards_result
            
        except Exception as e:
            logger.error(f"Error generating business cards: {e}")
            return {"success": False, "error": str(e)}
    
    def _setup_booking_integration(self, salon_id: str, salon_data: dict) -> dict:
        """Set up booking system integration"""
        try:
            logger.info(f"Setting up booking integration for salon {salon_id}")
            
            booking_config = {
                "salon_id": salon_id,
                "services": salon_data.get('services', []),
                "staff_availability": salon_data.get('staff_availability', {}),
                "booking_rules": {
                    "advance_booking_days": 30,
                    "cancellation_hours": 24,
                    "buffer_time_minutes": 15
                },
                "payment_integration": salon_data.get('payment_integration', False),
                "reminder_settings": {
                    "email_reminder_hours": [24, 2],
                    "sms_reminder_hours": [24]
                }
            }
            
            result = self.booking_service.setup_booking_system(booking_config)
            
            return result
            
        except Exception as e:
            logger.error(f"Error setting up booking integration: {e}")
            return {"success": False, "error": str(e)}
    
    def _setup_email_automation(self, salon_id: str, salon_data: dict) -> dict:
        """Set up email automation for salon"""
        try:
            logger.info(f"Setting up email automation for salon {salon_id}")
            
            email_config = {
                "salon_id": salon_id,
                "salon_name": salon_data.get('salon_name'),
                "email_templates": {
                    "booking_confirmation": True,
                    "appointment_reminder": True,
                    "follow_up_care": True,
                    "promotional_offers": salon_data.get('enable_marketing', True)
                },
                "automated_sequences": {
                    "new_client_welcome": True,
                    "birthday_special": True,
                    "loyalty_rewards": True
                }
            }
            
            result = self.email_service.setup_automation(email_config)
            
            return result
            
        except Exception as e:
            logger.error(f"Error setting up email automation: {e}")
            return {"success": False, "error": str(e)}
    
    def _emit_setup_notifications(self, salon_id: str, setup_data: dict):
        """Emit real-time notifications for salon setup"""
        try:
            # Emit to main dashboard
            self.socketio.emit('salon_setup_progress', {
                'salon_id': salon_id,
                'progress': setup_data,
                'timestamp': datetime.utcnow().isoformat()
            }, room='dashboard')
            
            # Emit website creation notification
            if setup_data.get("website", {}).get("success"):
                self.socketio.emit('salon_website_created', {
                    'salon_id': salon_id,
                    'website_url': setup_data["website"].get("website_url"),
                    'timestamp': datetime.utcnow().isoformat()
                }, room='dashboard')
            
            # Emit booking system notification
            if setup_data.get("booking", {}).get("success"):
                self.socketio.emit('salon_booking_ready', {
                    'salon_id': salon_id,
                    'booking_system': setup_data["booking"],
                    'timestamp': datetime.utcnow().isoformat()
                }, room='booking')
            
            logger.info(f"Setup notifications emitted for salon {salon_id}")
            
        except Exception as e:
            logger.error(f"Error emitting setup notifications: {e}")
    
    def _get_salon_dashboard_data(self, salon_id: str) -> dict:
        """Get dashboard data for salon"""
        try:
            salon_data = self.salon_model.get_salon_by_id(salon_id)
            
            if not salon_data:
                return {"error": "Salon not found"}
            
            # Get booking statistics
            booking_stats = self.booking_service.get_salon_statistics(salon_id)
            
            dashboard_data = {
                "salon_info": salon_data,
                "booking_statistics": booking_stats,
                "recent_appointments": self.booking_service.get_recent_appointments(salon_id, limit=10),
                "staff_performance": self._get_staff_performance(salon_id),
                "revenue_summary": self._get_revenue_summary(salon_id),
                "client_satisfaction": self._get_client_satisfaction(salon_id)
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting salon dashboard data: {e}")
            return {"error": str(e)}
    
    def _get_staff_performance(self, salon_id: str) -> dict:
        """Get staff performance metrics"""
        # Implementation for staff performance analytics
        return {
            "top_performers": [],
            "booking_counts": {},
            "client_ratings": {}
        }
    
    def _get_revenue_summary(self, salon_id: str) -> dict:
        """Get revenue summary"""
        # Implementation for revenue analytics
        return {
            "daily_revenue": 0,
            "monthly_revenue": 0,
            "top_services": []
        }
    
    def _get_client_satisfaction(self, salon_id: str) -> dict:
        """Get client satisfaction metrics"""
        # Implementation for client satisfaction analytics
        return {
            "average_rating": 4.5,
            "total_reviews": 0,
            "satisfaction_trend": []
        }
    
    # Additional service methods for booking management
    
    def handle_appointment_booking(self, salon_id: str, booking_data: dict) -> dict:
        """Handle appointment booking requests"""
        try:
            return self.booking_service.create_appointment(salon_id, booking_data)
        except Exception as e:
            logger.error(f"Error handling appointment booking: {e}")
            return {"success": False, "error": str(e)}
    
    def handle_appointment_modification(self, salon_id: str, appointment_id: str, changes: dict) -> dict:
        """Handle appointment modifications"""
        try:
            return self.booking_service.modify_appointment(appointment_id, changes)
        except Exception as e:
            logger.error(f"Error modifying appointment: {e}")
            return {"success": False, "error": str(e)}
    
    def handle_client_feedback(self, salon_id: str, feedback_data: dict) -> dict:
        """Handle client feedback and reviews"""
        try:
            # Process feedback through salon model
            result = self.salon_model.add_client_feedback(salon_id, feedback_data)
            
            # Send feedback to email service for follow-up
            if result.get("success"):
                self.email_service.send_feedback_thank_you(feedback_data)
            
            return result
        except Exception as e:
            logger.error(f"Error handling client feedback: {e}")
            return {"success": False, "error": str(e)}
    
    def get_salon_dashboard_data(self, salon_id: str) -> dict:
        """Get comprehensive dashboard data for salon"""
        return self._get_salon_dashboard_data(salon_id)