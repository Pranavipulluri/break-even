"""
Law Firm specific data models and database operations
"""

from pymongo import MongoClient
from datetime import datetime
import uuid
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class LawFirmDataModel:
    def __init__(self, mongo_client):
        self.db = mongo_client.break_even
        self.law_firms = self.db.law_firms
        self.attorneys = self.db.attorneys
        self.practice_areas = self.db.practice_areas
        self.consultations = self.db.consultations
        self.law_firm_analytics = self.db.law_firm_analytics
        
        # Create indexes for better performance
        self.create_indexes()
    
    def create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Law firms indexes
            self.law_firms.create_index("firm_id", unique=True)
            self.law_firms.create_index("email_address")
            self.law_firms.create_index("phone_number")
            
            # Attorneys indexes
            self.attorneys.create_index("firm_id")
            self.attorneys.create_index("attorney_id", unique=True)
            
            # Consultations indexes
            self.consultations.create_index("firm_id")
            self.consultations.create_index("consultation_date")
            self.consultations.create_index("status")
            
            logger.info("Law firm database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def create_law_firm(self, firm_data: Dict) -> Dict:
        """Create a new law firm with all associated data"""
        try:
            firm_id = str(uuid.uuid4())
            
            # Prepare law firm document
            law_firm_doc = {
                "firm_id": firm_id,
                "firm_name": firm_data.get("firmName"),
                "firm_tagline": firm_data.get("firmTagline", ""),
                "years_experience": int(firm_data.get("yearsExperience", 0)),
                "clients_served": int(firm_data.get("clientsServed", 0)),
                "firm_description": firm_data.get("firmDescription", ""),
                
                # Contact information
                "contact": {
                    "office_address": firm_data.get("officeAddress"),
                    "city": firm_data.get("city"),
                    "state": firm_data.get("state"),
                    "zip_code": firm_data.get("zipCode"),
                    "phone_number": firm_data.get("phoneNumber"),
                    "email_address": firm_data.get("emailAddress"),
                    "weekday_hours": firm_data.get("weekdayHours", "Monday - Friday: 9:00 AM - 6:00 PM"),
                    "weekend_hours": firm_data.get("weekendHours", "Saturday: 10:00 AM - 4:00 PM")
                },
                
                # Practice areas
                "practice_areas": firm_data.get("practiceAreas", []),
                "additional_services": firm_data.get("additionalServices", ""),
                
                # Design and branding
                "branding": {
                    "color_theme": firm_data.get("colorTheme", "blue"),
                    "hero_message": firm_data.get("heroMessage", ""),
                    "logo_url": firm_data.get("logoUrl", "")
                },
                
                # Business features
                "features": {
                    "enable_booking": firm_data.get("enableBooking", True),
                    "email_notifications": firm_data.get("emailNotifications", True),
                    "enable_newsletter": firm_data.get("enableNewsletter", True),
                    "enable_testimonials": firm_data.get("enableTestimonials", True),
                    "enable_blog": firm_data.get("enableBlog", False),
                    "enable_chat": firm_data.get("enableChat", True)
                },
                
                # Website and business info
                "website_url": "",
                "qr_code_url": "",
                "business_card_designs": [],
                
                # Metadata
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "active"
            }
            
            # Insert law firm
            result = self.law_firms.insert_one(law_firm_doc)
            
            # Create attorneys
            attorneys = firm_data.get("attorneys", [])
            attorney_ids = []
            for i, attorney_data in enumerate(attorneys):
                attorney_id = self.create_attorney(firm_id, attorney_data, i)
                attorney_ids.append(attorney_id)
            
            # Update law firm with attorney IDs
            self.law_firms.update_one(
                {"firm_id": firm_id},
                {"$set": {"attorney_ids": attorney_ids}}
            )
            
            logger.info(f"Law firm created successfully: {firm_id}")
            return {
                "success": True,
                "firm_id": firm_id,
                "attorney_ids": attorney_ids,
                "firm_data": law_firm_doc
            }
            
        except Exception as e:
            logger.error(f"Error creating law firm: {e}")
            return {"success": False, "error": str(e)}
    
    def create_attorney(self, firm_id: str, attorney_data: Dict, index: int = 0) -> str:
        """Create an attorney profile"""
        try:
            attorney_id = str(uuid.uuid4())
            
            attorney_doc = {
                "attorney_id": attorney_id,
                "firm_id": firm_id,
                "name": attorney_data.get("name", ""),
                "title": attorney_data.get("title", ""),
                "experience_years": int(attorney_data.get("experience", 0)) if attorney_data.get("experience") else None,
                "education": attorney_data.get("education", ""),
                "specializations": attorney_data.get("specializations", ""),
                "bio": attorney_data.get("bio", ""),
                "photo_url": attorney_data.get("photoUrl", ""),
                "order_index": index,
                "created_at": datetime.utcnow(),
                "status": "active"
            }
            
            self.attorneys.insert_one(attorney_doc)
            logger.info(f"Attorney created: {attorney_id}")
            return attorney_id
            
        except Exception as e:
            logger.error(f"Error creating attorney: {e}")
            raise e
    
    def get_law_firm(self, firm_id: str) -> Optional[Dict]:
        """Get law firm data with attorneys"""
        try:
            firm = self.law_firms.find_one({"firm_id": firm_id})
            if not firm:
                return None
            
            # Get attorneys
            attorneys = list(self.attorneys.find(
                {"firm_id": firm_id}, 
                {"_id": 0}
            ).sort("order_index", 1))
            
            firm["attorneys"] = attorneys
            firm.pop("_id", None)
            return firm
            
        except Exception as e:
            logger.error(f"Error getting law firm: {e}")
            return None
    
    def update_website_info(self, firm_id: str, website_url: str, qr_code_url: str) -> bool:
        """Update law firm with website and QR code URLs"""
        try:
            result = self.law_firms.update_one(
                {"firm_id": firm_id},
                {
                    "$set": {
                        "website_url": website_url,
                        "qr_code_url": qr_code_url,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating website info: {e}")
            return False
    
    def create_consultation(self, consultation_data: Dict) -> Dict:
        """Create a consultation booking"""
        try:
            consultation_id = str(uuid.uuid4())
            
            consultation_doc = {
                "consultation_id": consultation_id,
                "firm_id": consultation_data.get("firm_id"),
                "client_info": {
                    "first_name": consultation_data.get("firstName"),
                    "last_name": consultation_data.get("lastName"),
                    "email": consultation_data.get("email"),
                    "phone": consultation_data.get("phone")
                },
                "consultation_details": {
                    "practice_area": consultation_data.get("practiceArea"),
                    "preferred_date": consultation_data.get("date"),
                    "preferred_time": consultation_data.get("time"),
                    "description": consultation_data.get("description", "")
                },
                "status": "pending",
                "created_at": datetime.utcnow(),
                "source": "law_firm_website"
            }
            
            result = self.consultations.insert_one(consultation_doc)
            
            # Update analytics
            self.update_analytics(consultation_data.get("firm_id"), "consultation_booked")
            
            logger.info(f"Consultation created: {consultation_id}")
            return {
                "success": True,
                "consultation_id": consultation_id
            }
            
        except Exception as e:
            logger.error(f"Error creating consultation: {e}")
            return {"success": False, "error": str(e)}
    
    def get_firm_consultations(self, firm_id: str, limit: int = 50) -> List[Dict]:
        """Get consultations for a law firm"""
        try:
            consultations = list(self.consultations.find(
                {"firm_id": firm_id},
                {"_id": 0}
            ).sort("created_at", -1).limit(limit))
            
            return consultations
        except Exception as e:
            logger.error(f"Error getting consultations: {e}")
            return []
    
    def update_consultation_status(self, consultation_id: str, status: str, notes: str = "") -> bool:
        """Update consultation status"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if notes:
                update_data["admin_notes"] = notes
            
            result = self.consultations.update_one(
                {"consultation_id": consultation_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating consultation status: {e}")
            return False
    
    def update_analytics(self, firm_id: str, event_type: str, data: Dict = None):
        """Update analytics for law firm"""
        try:
            today = datetime.utcnow().date()
            
            # Update or create daily analytics
            self.law_firm_analytics.update_one(
                {"firm_id": firm_id, "date": today},
                {
                    "$inc": {f"events.{event_type}": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                },
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
    
    def get_firm_analytics(self, firm_id: str, days: int = 30) -> Dict:
        """Get analytics for law firm"""
        try:
            from datetime import timedelta
            
            start_date = datetime.utcnow().date() - timedelta(days=days)
            
            analytics = list(self.law_firm_analytics.find(
                {
                    "firm_id": firm_id,
                    "date": {"$gte": start_date}
                },
                {"_id": 0}
            ).sort("date", 1))
            
            # Calculate totals
            totals = {}
            for day_data in analytics:
                events = day_data.get("events", {})
                for event_type, count in events.items():
                    totals[event_type] = totals.get(event_type, 0) + count
            
            return {
                "daily_analytics": analytics,
                "totals": totals,
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"daily_analytics": [], "totals": {}, "period_days": days}
    
    def search_law_firms(self, query: str, limit: int = 10) -> List[Dict]:
        """Search law firms by name, location, or practice area"""
        try:
            search_filter = {
                "$or": [
                    {"firm_name": {"$regex": query, "$options": "i"}},
                    {"contact.city": {"$regex": query, "$options": "i"}},
                    {"contact.state": {"$regex": query, "$options": "i"}},
                    {"practice_areas": {"$regex": query, "$options": "i"}}
                ]
            }
            
            firms = list(self.law_firms.find(
                search_filter,
                {
                    "_id": 0,
                    "firm_id": 1,
                    "firm_name": 1,
                    "contact.city": 1,
                    "contact.state": 1,
                    "practice_areas": 1,
                    "years_experience": 1,
                    "website_url": 1
                }
            ).limit(limit))
            
            return firms
        except Exception as e:
            logger.error(f"Error searching law firms: {e}")
            return []