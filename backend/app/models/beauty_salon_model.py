"""
Beauty Salon/Spa Data Model - Database operations for beauty salon management
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid
from pymongo import MongoClient
from bson import ObjectId

logger = logging.getLogger(__name__)

class BeautySalonDataModel:
    """Data model for beauty salon/spa operations"""
    
    def __init__(self, mongo_client: MongoClient):
        self.client = mongo_client
        self.db = mongo_client.break_even
        
        # Collections
        self.salons = self.db.beauty_salons
        self.staff = self.db.salon_staff
        self.appointments = self.db.salon_appointments
        self.services = self.db.salon_services
        self.clients = self.db.salon_clients
        self.reviews = self.db.salon_reviews
        self.analytics = self.db.salon_analytics
        
        self._create_indexes()
        
    def _create_indexes(self):
        """Create database indexes for performance"""
        try:
            # Beauty salons indexes
            self.salons.create_index("salon_id", unique=True)
            self.salons.create_index("salon_name")
            self.salons.create_index("contact.email_address")
            self.salons.create_index("created_at")
            
            # Staff indexes
            self.staff.create_index("staff_id", unique=True)
            self.staff.create_index("salon_id")
            self.staff.create_index("name")
            self.staff.create_index("specializations")
            
            # Appointments indexes
            self.appointments.create_index("appointment_id", unique=True)
            self.appointments.create_index("salon_id")
            self.appointments.create_index("staff_id")
            self.appointments.create_index("appointment_date")
            self.appointments.create_index("status")
            
            # Services indexes
            self.services.create_index("service_id", unique=True)
            self.services.create_index("salon_id")
            self.services.create_index("category")
            self.services.create_index("name")
            
            # Clients indexes
            self.clients.create_index("client_id", unique=True)
            self.clients.create_index("email")
            self.clients.create_index("phone")
            
            # Reviews indexes
            self.reviews.create_index("review_id", unique=True)
            self.reviews.create_index("salon_id")
            self.reviews.create_index("rating")
            self.reviews.create_index("created_at")
            
            logger.info("Beauty salon database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating database indexes: {e}")
    
    def create_beauty_salon(self, salon_data: dict) -> dict:
        """Create a new beauty salon"""
        try:
            salon_data['created_at'] = datetime.utcnow()
            salon_data['updated_at'] = datetime.utcnow()
            
            result = self.salons.insert_one(salon_data)
            
            if result.inserted_id:
                logger.info(f"Beauty salon created successfully: {salon_data['salon_id']}")
                return {
                    "success": True,
                    "salon_id": salon_data['salon_id'],
                    "message": "Beauty salon created successfully"
                }
            else:
                return {"success": False, "error": "Failed to create beauty salon"}
                
        except Exception as e:
            logger.error(f"Error creating beauty salon: {e}")
            return {"success": False, "error": str(e)}
    
    def create_staff_member(self, staff_data: dict) -> dict:
        """Create a new staff member"""
        try:
            if not staff_data.get('staff_id'):
                staff_data['staff_id'] = str(uuid.uuid4())
            
            staff_data['created_at'] = datetime.utcnow()
            staff_data['updated_at'] = datetime.utcnow()
            
            result = self.staff.insert_one(staff_data)
            
            if result.inserted_id:
                logger.info(f"Staff member created: {staff_data['staff_id']}")
                return {
                    "success": True,
                    "staff_id": staff_data['staff_id'],
                    "message": "Staff member created successfully"
                }
            else:
                return {"success": False, "error": "Failed to create staff member"}
                
        except Exception as e:
            logger.error(f"Error creating staff member: {e}")
            return {"success": False, "error": str(e)}
    
    def get_salon_by_id(self, salon_id: str) -> Optional[dict]:
        """Get salon by ID"""
        try:
            salon = self.salons.find_one({"salon_id": salon_id})
            if salon:
                salon['_id'] = str(salon['_id'])
            return salon
        except Exception as e:
            logger.error(f"Error getting salon by ID: {e}")
            return None
    
    def get_staff_by_salon(self, salon_id: str) -> List[dict]:
        """Get all staff members for a salon"""
        try:
            staff_members = list(self.staff.find({"salon_id": salon_id}))
            for staff in staff_members:
                staff['_id'] = str(staff['_id'])
            return staff_members
        except Exception as e:
            logger.error(f"Error getting staff by salon: {e}")
            return []
    
    def create_service(self, service_data: dict) -> dict:
        """Create a new service"""
        try:
            if not service_data.get('service_id'):
                service_data['service_id'] = str(uuid.uuid4())
            
            service_data['created_at'] = datetime.utcnow()
            service_data['updated_at'] = datetime.utcnow()
            
            result = self.services.insert_one(service_data)
            
            if result.inserted_id:
                logger.info(f"Service created: {service_data['service_id']}")
                return {
                    "success": True,
                    "service_id": service_data['service_id'],
                    "message": "Service created successfully"
                }
            else:
                return {"success": False, "error": "Failed to create service"}
                
        except Exception as e:
            logger.error(f"Error creating service: {e}")
            return {"success": False, "error": str(e)}
    
    def get_services_by_salon(self, salon_id: str) -> List[dict]:
        """Get all services for a salon"""
        try:
            services = list(self.services.find({"salon_id": salon_id}))
            for service in services:
                service['_id'] = str(service['_id'])
            return services
        except Exception as e:
            logger.error(f"Error getting services by salon: {e}")
            return []
    
    def create_appointment(self, appointment_data: dict) -> dict:
        """Create a new appointment"""
        try:
            if not appointment_data.get('appointment_id'):
                appointment_data['appointment_id'] = str(uuid.uuid4())
            
            appointment_data['created_at'] = datetime.utcnow()
            appointment_data['updated_at'] = datetime.utcnow()
            appointment_data['status'] = appointment_data.get('status', 'scheduled')
            
            result = self.appointments.insert_one(appointment_data)
            
            if result.inserted_id:
                logger.info(f"Appointment created: {appointment_data['appointment_id']}")
                return {
                    "success": True,
                    "appointment_id": appointment_data['appointment_id'],
                    "message": "Appointment created successfully"
                }
            else:
                return {"success": False, "error": "Failed to create appointment"}
                
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            return {"success": False, "error": str(e)}
    
    def get_appointments_by_salon(self, salon_id: str, date_from: datetime = None, date_to: datetime = None) -> List[dict]:
        """Get appointments for a salon within date range"""
        try:
            query = {"salon_id": salon_id}
            
            if date_from or date_to:
                query["appointment_date"] = {}
                if date_from:
                    query["appointment_date"]["$gte"] = date_from
                if date_to:
                    query["appointment_date"]["$lte"] = date_to
            
            appointments = list(self.appointments.find(query).sort("appointment_date", 1))
            for appointment in appointments:
                appointment['_id'] = str(appointment['_id'])
            return appointments
        except Exception as e:
            logger.error(f"Error getting appointments by salon: {e}")
            return []
    
    def create_client(self, client_data: dict) -> dict:
        """Create a new client"""
        try:
            if not client_data.get('client_id'):
                client_data['client_id'] = str(uuid.uuid4())
            
            client_data['created_at'] = datetime.utcnow()
            client_data['updated_at'] = datetime.utcnow()
            
            result = self.clients.insert_one(client_data)
            
            if result.inserted_id:
                logger.info(f"Client created: {client_data['client_id']}")
                return {
                    "success": True,
                    "client_id": client_data['client_id'],
                    "message": "Client created successfully"
                }
            else:
                return {"success": False, "error": "Failed to create client"}
                
        except Exception as e:
            logger.error(f"Error creating client: {e}")
            return {"success": False, "error": str(e)}
    
    def get_client_by_email(self, email: str) -> Optional[dict]:
        """Get client by email"""
        try:
            client = self.clients.find_one({"email": email})
            if client:
                client['_id'] = str(client['_id'])
            return client
        except Exception as e:
            logger.error(f"Error getting client by email: {e}")
            return None
    
    def add_client_feedback(self, salon_id: str, feedback_data: dict) -> dict:
        """Add client feedback and review"""
        try:
            if not feedback_data.get('review_id'):
                feedback_data['review_id'] = str(uuid.uuid4())
            
            feedback_data['salon_id'] = salon_id
            feedback_data['created_at'] = datetime.utcnow()
            feedback_data['updated_at'] = datetime.utcnow()
            
            result = self.reviews.insert_one(feedback_data)
            
            if result.inserted_id:
                # Update salon analytics
                self._update_salon_analytics(salon_id, {
                    'reviews_count': 1,
                    'total_rating': feedback_data.get('rating', 0)
                })
                
                logger.info(f"Client feedback added: {feedback_data['review_id']}")
                return {
                    "success": True,
                    "review_id": feedback_data['review_id'],
                    "message": "Feedback added successfully"
                }
            else:
                return {"success": False, "error": "Failed to add feedback"}
                
        except Exception as e:
            logger.error(f"Error adding client feedback: {e}")
            return {"success": False, "error": str(e)}
    
    def get_salon_reviews(self, salon_id: str, limit: int = 50) -> List[dict]:
        """Get reviews for a salon"""
        try:
            reviews = list(self.reviews.find({"salon_id": salon_id}).sort("created_at", -1).limit(limit))
            for review in reviews:
                review['_id'] = str(review['_id'])
            return reviews
        except Exception as e:
            logger.error(f"Error getting salon reviews: {e}")
            return []
    
    def update_website_info(self, salon_id: str, website_url: str, qr_code_url: str):
        """Update salon website information"""
        try:
            result = self.salons.update_one(
                {"salon_id": salon_id},
                {
                    "$set": {
                        "website_url": website_url,
                        "qr_code_url": qr_code_url,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Website info updated for salon: {salon_id}")
                return True
            else:
                logger.warning(f"No salon found to update website info: {salon_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating website info: {e}")
            return False
    
    def _update_salon_analytics(self, salon_id: str, metrics: dict):
        """Update salon analytics"""
        try:
            self.analytics.update_one(
                {"salon_id": salon_id},
                {
                    "$inc": metrics,
                    "$set": {"updated_at": datetime.utcnow()}
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error updating salon analytics: {e}")
    
    def get_salon_analytics(self, salon_id: str) -> dict:
        """Get salon analytics"""
        try:
            analytics = self.analytics.find_one({"salon_id": salon_id})
            if analytics:
                analytics['_id'] = str(analytics['_id'])
                return analytics
            else:
                return {
                    "salon_id": salon_id,
                    "appointments_count": 0,
                    "reviews_count": 0,
                    "total_rating": 0,
                    "average_rating": 0,
                    "revenue": 0
                }
        except Exception as e:
            logger.error(f"Error getting salon analytics: {e}")
            return {}
    
    def get_staff_availability(self, staff_id: str, date: datetime) -> dict:
        """Get staff availability for a specific date"""
        try:
            # Get staff working hours
            staff = self.staff.find_one({"staff_id": staff_id})
            if not staff:
                return {"available": False, "error": "Staff member not found"}
            
            working_hours = staff.get('working_hours', {})
            day_of_week = date.strftime('%A').lower()
            
            if day_of_week not in working_hours:
                return {"available": False, "reason": "Not working on this day"}
            
            # Get existing appointments for the day
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            appointments = list(self.appointments.find({
                "staff_id": staff_id,
                "appointment_date": {"$gte": start_of_day, "$lt": end_of_day},
                "status": {"$in": ["scheduled", "confirmed"]}
            }))
            
            # Calculate available time slots
            work_start = working_hours[day_of_week].get('start', '09:00')
            work_end = working_hours[day_of_week].get('end', '17:00')
            
            available_slots = self._calculate_available_slots(
                work_start, work_end, appointments
            )
            
            return {
                "available": len(available_slots) > 0,
                "available_slots": available_slots,
                "booked_slots": [apt['appointment_time'] for apt in appointments]
            }
            
        except Exception as e:
            logger.error(f"Error getting staff availability: {e}")
            return {"available": False, "error": str(e)}
    
    def _calculate_available_slots(self, work_start: str, work_end: str, appointments: List[dict]) -> List[str]:
        """Calculate available time slots"""
        # Implementation for calculating available time slots
        # This would involve parsing work hours and excluding booked appointments
        available_slots = []
        
        # Simple implementation - would need more sophisticated logic for real use
        work_hours = ['09:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00']
        booked_times = [apt.get('appointment_time', '') for apt in appointments]
        
        for time_slot in work_hours:
            if time_slot not in booked_times:
                available_slots.append(time_slot)
        
        return available_slots