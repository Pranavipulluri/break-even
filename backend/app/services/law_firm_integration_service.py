"""
Law Firm Integration Service - Connects law firm systems with main business platform
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from bson import ObjectId

from app.models.law_firm_model import LawFirmDataModel
from app.services.law_firm_website_generator import LawFirmWebsiteGenerator
from app.services.law_firm_business_card_generator import LawFirmBusinessCardGenerator
from app.services.law_firm_email_service import LawFirmEmailService

logger = logging.getLogger(__name__)

class LawFirmIntegrationService:
    def __init__(self, socketio=None, mongo_client=None):
        self.socketio = socketio
        self.law_firm_model = LawFirmDataModel(mongo_client)
        self.website_generator = LawFirmWebsiteGenerator()
        self.card_generator = LawFirmBusinessCardGenerator()
        self.email_service = LawFirmEmailService()
    
    def create_complete_law_firm_setup(self, form_data: dict) -> dict:
        """Create complete law firm setup with website, cards, and integrations"""
        try:
            logger.info("Starting complete law firm setup")
            
            # Step 1: Create law firm in database
            firm_result = self.law_firm_model.create_law_firm(form_data)
            if not firm_result["success"]:
                return {"success": False, "error": "Failed to create law firm", "details": firm_result.get("error")}
            
            firm_id = firm_result["firm_id"]
            firm_data = firm_result["firm_data"]
            
            # Step 2: Generate and deploy website
            logger.info(f"Generating website for firm {firm_id}")
            website_result = self.website_generator.generate_website(firm_id, form_data)
            
            if website_result["success"]:
                # Update firm with website URL
                website_url = website_result["website_url"]
                self.law_firm_model.update_website_info(firm_id, website_url, website_result.get("qr_code_url"))
                firm_data["website_url"] = website_url
                
                # Emit real-time notification
                self._emit_notification("firm_website_created", {
                    "firm_id": firm_id,
                    "firm_name": form_data.get("firmName"),
                    "website_url": website_url
                })
            
            # Step 3: Generate business cards for all attorneys
            business_cards = []
            attorneys = form_data.get("attorneys", [])
            design_style = form_data.get("colorTheme", "classic_navy")
            
            for attorney in attorneys:
                logger.info(f"Generating business card for {attorney.get('name', 'attorney')}")
                card_result = self.card_generator.generate_business_card(firm_data, attorney, design_style)
                
                if card_result["success"]:
                    business_cards.append({
                        "attorney_name": attorney.get("name"),
                        "front_image": card_result["front_image"],
                        "back_image": card_result["back_image"],
                        "card_id": card_result["card_id"]
                    })
                    
                    # Send business card delivery email
                    self.email_service.send_business_card_delivery(firm_data, attorney, card_result)
            
            # Step 4: Set up email automation and notifications
            self._setup_firm_integrations(firm_id, firm_data)
            
            # Step 5: Create dashboard entry for tracking
            dashboard_data = self._create_dashboard_entry(firm_data, website_result, business_cards)
            
            # Emit completion notification
            self._emit_notification("firm_setup_complete", {
                "firm_id": firm_id,
                "firm_name": form_data.get("firmName"),
                "website_url": website_result.get("website_url"),
                "business_cards_count": len(business_cards),
                "dashboard_data": dashboard_data
            })
            
            logger.info(f"Complete law firm setup finished for {firm_id}")
            
            return {
                "success": True,
                "firm_id": firm_id,
                "website": website_result,
                "business_cards": business_cards,
                "dashboard_data": dashboard_data,
                "integrations_active": True
            }
            
        except Exception as e:
            logger.error(f"Error in complete law firm setup: {e}")
            return {"success": False, "error": str(e)}
    
    def handle_consultation_booking(self, firm_id: str, booking_data: dict) -> dict:
        """Handle consultation booking with full integration"""
        try:
            # Get firm data
            firm_data = self.law_firm_model.get_firm_by_id(firm_id)
            if not firm_data:
                return {"success": False, "error": "Law firm not found"}
            
            # Save consultation booking
            booking_result = self.law_firm_model.book_consultation(firm_id, booking_data)
            
            if booking_result["success"]:
                # Send confirmation email
                email_result = self.email_service.send_consultation_confirmation(firm_data, booking_data)
                
                # Sync with main dashboard
                self._sync_booking_with_dashboard(firm_id, firm_data, booking_data, booking_result["booking_id"])
                
                # Emit real-time notification
                self._emit_notification("consultation_booked", {
                    "firm_id": firm_id,
                    "firm_name": firm_data.get("firmName"),
                    "client_name": booking_data.get("name"),
                    "consultation_date": booking_data.get("date"),
                    "booking_id": booking_result["booking_id"]
                })
                
                # Connect to chat system for follow-up
                self._connect_to_chat_system(firm_id, booking_data, "consultation_booking")
                
                logger.info(f"Consultation booked and synced for firm {firm_id}")
                
                return {
                    "success": True,
                    "booking_id": booking_result["booking_id"],
                    "email_sent": email_result.get("success", False),
                    "dashboard_synced": True,
                    "chat_connected": True
                }
            
            return booking_result
            
        except Exception as e:
            logger.error(f"Error handling consultation booking: {e}")
            return {"success": False, "error": str(e)}
    
    def handle_contact_inquiry(self, firm_id: str, contact_data: dict) -> dict:
        """Handle contact form submission with chat integration"""
        try:
            # Get firm data
            firm_data = self.law_firm_model.get_firm_by_id(firm_id)
            if not firm_data:
                return {"success": False, "error": "Law firm not found"}
            
            # Save contact inquiry
            inquiry_result = self.law_firm_model.save_contact_inquiry(firm_id, contact_data)
            
            if inquiry_result["success"]:
                # Send auto-response email
                email_result = self.email_service.send_contact_inquiry_response(firm_data, contact_data)
                
                # Connect to main website chat system
                chat_result = self._connect_to_chat_system(firm_id, contact_data, "contact_inquiry")
                
                # Emit real-time notification
                self._emit_notification("contact_inquiry_received", {
                    "firm_id": firm_id,
                    "firm_name": firm_data.get("firmName"),
                    "client_name": contact_data.get("name"),
                    "subject": contact_data.get("subject"),
                    "inquiry_id": inquiry_result["inquiry_id"]
                })
                
                logger.info(f"Contact inquiry handled and connected to chat for firm {firm_id}")
                
                return {
                    "success": True,
                    "inquiry_id": inquiry_result["inquiry_id"],
                    "email_sent": email_result.get("success", False),
                    "chat_connected": chat_result.get("success", False)
                }
            
            return inquiry_result
            
        except Exception as e:
            logger.error(f"Error handling contact inquiry: {e}")
            return {"success": False, "error": str(e)}
    
    def handle_feedback_submission(self, firm_id: str, feedback_data: dict) -> dict:
        """Handle feedback submission with sentiment analysis integration"""
        try:
            # Get firm data
            firm_data = self.law_firm_model.get_firm_by_id(firm_id)
            if not firm_data:
                return {"success": False, "error": "Law firm not found"}
            
            # Save feedback
            feedback_result = self.law_firm_model.save_client_feedback(firm_id, feedback_data)
            
            if feedback_result["success"]:
                # Integrate with sentiment analysis
                sentiment_result = self._integrate_with_sentiment_analysis(firm_id, feedback_data)
                
                # Update analytics
                self._update_firm_analytics(firm_id, "feedback_received", feedback_data)
                
                # Emit real-time notification
                self._emit_notification("feedback_received", {
                    "firm_id": firm_id,
                    "firm_name": firm_data.get("firmName"),
                    "rating": feedback_data.get("rating"),
                    "sentiment": sentiment_result.get("sentiment"),
                    "feedback_id": feedback_result["feedback_id"]
                })
                
                logger.info(f"Feedback handled and analyzed for firm {firm_id}")
                
                return {
                    "success": True,
                    "feedback_id": feedback_result["feedback_id"],
                    "sentiment_analysis": sentiment_result
                }
            
            return feedback_result
            
        except Exception as e:
            logger.error(f"Error handling feedback submission: {e}")
            return {"success": False, "error": str(e)}
    
    def get_firm_dashboard_data(self, firm_id: str) -> dict:
        """Get comprehensive dashboard data for a law firm"""
        try:
            # Get firm data
            firm_data = self.law_firm_model.get_firm_by_id(firm_id)
            if not firm_data:
                return {"success": False, "error": "Law firm not found"}
            
            # Get analytics
            analytics = self.law_firm_model.get_firm_analytics(firm_id)
            
            # Get recent activity
            recent_consultations = self.law_firm_model.get_recent_consultations(firm_id, limit=10)
            recent_inquiries = self.law_firm_model.get_recent_contact_inquiries(firm_id, limit=10)
            recent_feedback = self.law_firm_model.get_recent_feedback(firm_id, limit=10)
            
            # Calculate metrics
            total_consultations = len(recent_consultations)
            total_inquiries = len(recent_inquiries)
            average_rating = self._calculate_average_rating(recent_feedback)
            
            dashboard_data = {
                "firm_info": {
                    "firm_id": firm_id,
                    "name": firm_data.get("firmName"),
                    "website_url": firm_data.get("website_url"),
                    "created_date": firm_data.get("created_date")
                },
                "metrics": {
                    "total_consultations": total_consultations,
                    "total_inquiries": total_inquiries,
                    "average_rating": average_rating,
                    "total_attorneys": len(firm_data.get("attorneys", []))
                },
                "recent_activity": {
                    "consultations": recent_consultations,
                    "inquiries": recent_inquiries,
                    "feedback": recent_feedback
                },
                "analytics": analytics
            }
            
            return {"success": True, "dashboard_data": dashboard_data}
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {"success": False, "error": str(e)}
    
    def _setup_firm_integrations(self, firm_id: str, firm_data: dict):
        """Set up integrations for the law firm"""
        try:
            # Set up email automation rules
            automation_rules = {
                "consultation_reminders": True,
                "follow_up_emails": True,
                "newsletter_automation": True,
                "birthday_greetings": False
            }
            
            # Store integration settings
            integration_settings = {
                "firm_id": firm_id,
                "dashboard_sync": True,
                "chat_integration": True,
                "sentiment_analysis": True,
                "email_automation": automation_rules,
                "created_date": datetime.utcnow().isoformat()
            }
            
            self.law_firm_model.save_integration_settings(firm_id, integration_settings)
            
        except Exception as e:
            logger.error(f"Error setting up integrations: {e}")
    
    def _sync_booking_with_dashboard(self, firm_id: str, firm_data: dict, booking_data: dict, booking_id: str):
        """Sync booking with main dashboard"""
        try:
            # Create dashboard booking entry
            dashboard_booking = {
                "booking_id": booking_id,
                "firm_id": firm_id,
                "firm_name": firm_data.get("firmName"),
                "client_name": booking_data.get("name"),
                "client_email": booking_data.get("email"),
                "client_phone": booking_data.get("phone"),
                "consultation_date": booking_data.get("date"),
                "consultation_time": booking_data.get("time"),
                "legal_matter": booking_data.get("legalMatter"),
                "status": "confirmed",
                "source": "law_firm_website",
                "created_date": datetime.utcnow().isoformat()
            }
            
            # Emit to main dashboard
            if self.socketio:
                self.socketio.emit("booking_update", dashboard_booking, room="dashboard")
            
            # Update firm analytics
            self._update_firm_analytics(firm_id, "consultation_booked", booking_data)
            
        except Exception as e:
            logger.error(f"Error syncing booking with dashboard: {e}")
    
    def _connect_to_chat_system(self, firm_id: str, contact_data: dict, interaction_type: str) -> dict:
        """Connect contact to main website chat system"""
        try:
            # Create chat session
            chat_session = {
                "firm_id": firm_id,
                "client_name": contact_data.get("name"),
                "client_email": contact_data.get("email"),
                "interaction_type": interaction_type,
                "initial_message": contact_data.get("message", ""),
                "created_date": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Emit to chat system
            if self.socketio:
                self.socketio.emit("chat_session_created", chat_session, room="chat_support")
            
            return {"success": True, "chat_session_id": str(ObjectId())}
            
        except Exception as e:
            logger.error(f"Error connecting to chat system: {e}")
            return {"success": False, "error": str(e)}
    
    def _integrate_with_sentiment_analysis(self, firm_id: str, feedback_data: dict) -> dict:
        """Integrate feedback with sentiment analysis system"""
        try:
            # Analyze sentiment of feedback
            feedback_text = feedback_data.get("feedback", "")
            rating = feedback_data.get("rating", 3)
            
            # Simple sentiment analysis based on rating and keywords
            sentiment_score = self._calculate_sentiment_score(feedback_text, rating)
            sentiment_label = self._get_sentiment_label(sentiment_score)
            
            # Create sentiment analysis entry
            sentiment_data = {
                "firm_id": firm_id,
                "feedback_text": feedback_text,
                "rating": rating,
                "sentiment_score": sentiment_score,
                "sentiment_label": sentiment_label,
                "keywords": self._extract_keywords(feedback_text),
                "created_date": datetime.utcnow().isoformat()
            }
            
            # Emit to sentiment analysis system
            if self.socketio:
                self.socketio.emit("sentiment_analysis_update", sentiment_data, room="analytics")
            
            return {
                "success": True,
                "sentiment": sentiment_label,
                "score": sentiment_score
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis integration: {e}")
            return {"success": False, "error": str(e)}
    
    def _update_firm_analytics(self, firm_id: str, event_type: str, event_data: dict):
        """Update firm analytics with new event"""
        try:
            analytics_event = {
                "firm_id": firm_id,
                "event_type": event_type,
                "event_data": event_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.law_firm_model.add_analytics_event(firm_id, analytics_event)
            
            # Emit to analytics system
            if self.socketio:
                self.socketio.emit("analytics_update", analytics_event, room="analytics")
                
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
    
    def _create_dashboard_entry(self, firm_data: dict, website_result: dict, business_cards: list) -> dict:
        """Create dashboard entry for the new firm"""
        return {
            "firm_name": firm_data.get("firmName"),
            "website_status": "active" if website_result.get("success") else "failed",
            "website_url": website_result.get("website_url"),
            "business_cards_generated": len(business_cards),
            "created_date": datetime.utcnow().isoformat(),
            "integrations": {
                "email_automation": True,
                "booking_sync": True,
                "chat_integration": True,
                "sentiment_analysis": True
            }
        }
    
    def _calculate_sentiment_score(self, text: str, rating: int) -> float:
        """Calculate sentiment score from text and rating"""
        # Base score from rating (1-5 scale to -1 to 1 scale)
        rating_score = (rating - 3) / 2  # -1 to 1 scale
        
        # Simple keyword-based sentiment analysis
        positive_keywords = ["excellent", "great", "wonderful", "amazing", "professional", "helpful", "recommend"]
        negative_keywords = ["terrible", "awful", "horrible", "poor", "unprofessional", "disappointed"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        # Text sentiment contribution
        text_score = (positive_count - negative_count) * 0.1
        
        # Combine rating and text sentiment
        final_score = (rating_score * 0.7) + (text_score * 0.3)
        
        return max(-1, min(1, final_score))  # Clamp to -1 to 1 range
    
    def _get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score >= 0.3:
            return "positive"
        elif score <= -0.3:
            return "negative"
        else:
            return "neutral"
    
    def _extract_keywords(self, text: str) -> list:
        """Extract keywords from feedback text"""
        # Simple keyword extraction
        stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "a", "an"}
        words = text.lower().split()
        keywords = [word.strip(".,!?") for word in words if word not in stop_words and len(word) > 3]
        return keywords[:10]  # Return top 10 keywords
    
    def _calculate_average_rating(self, feedback_list: list) -> float:
        """Calculate average rating from feedback list"""
        if not feedback_list:
            return 0.0
        
        total_rating = sum(feedback.get("rating", 0) for feedback in feedback_list)
        return round(total_rating / len(feedback_list), 1)
    
    def _emit_notification(self, event: str, data: dict):
        """Emit real-time notification"""
        try:
            if self.socketio:
                self.socketio.emit(event, data, room="notifications")
                logger.info(f"Notification emitted: {event}")
        except Exception as e:
            logger.error(f"Error emitting notification: {e}")