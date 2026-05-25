# app/services/realtime_service.py
from flask_socketio import emit
from app import socketio
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RealtimeService:
    """
    Service for real-time synchronization between mini-websites and main dashboard
    """
    
    @staticmethod
    def emit_to_business(business_id, event_name, data):
        """
        Emit event to a specific business owner
        """
        try:
            room = str(business_id)
            logger.info(f"Emitting {event_name} to business {business_id}")
            
            # Add timestamp to data
            if isinstance(data, dict):
                data['timestamp'] = datetime.utcnow().isoformat()
            
            socketio.emit(event_name, data, room=room)
            return True
            
        except Exception as e:
            logger.error(f"Error emitting to business {business_id}: {str(e)}")
            return False
    
    @staticmethod
    def notify_new_booking(business_id, booking_type, booking_data):
        """
        Notify business owner of new booking in real-time
        """
        try:
            # Prepare notification data
            notification_data = {
                'type': 'new_booking',
                'booking_type': booking_type,
                'booking_id': str(booking_data.get('_id', '')),
                'customer_name': RealtimeService._get_customer_name(booking_data),
                'service': RealtimeService._get_service_name(booking_data),
                'source': 'mini_website',
                'priority': 'high',
                'title': f'New {booking_type.replace("_", " ").title()}',
                'message': f'New {booking_type.replace("_", " ")} from {RealtimeService._get_customer_name(booking_data)}'
            }
            
            # Emit to business owner
            RealtimeService.emit_to_business(business_id, 'new_booking', notification_data)
            
            # Also emit general notification
            RealtimeService.emit_to_business(business_id, 'notification', {
                'type': 'booking',
                'message': notification_data['message'],
                'title': notification_data['title'],
                'action_url': f'/dashboard/bookings?type={booking_type}'
            })
            
            logger.info(f"Real-time booking notification sent for {booking_type} to business {business_id}")
            
        except Exception as e:
            logger.error(f"Error sending real-time booking notification: {str(e)}")
    
    @staticmethod
    def notify_new_message(business_id, message_type, message_data):
        """
        Notify business owner of new message in real-time
        """
        try:
            # Prepare notification data
            notification_data = {
                'type': 'new_message',
                'message_type': message_type,
                'message_id': str(message_data.get('_id', '')),
                'customer_name': RealtimeService._get_message_sender(message_data),
                'subject': message_data.get('message_details', {}).get('subject', 'New Message'),
                'source': 'mini_website',
                'priority': 'medium',
                'title': f'New {message_type.replace("_", " ").title()}',
                'message': f'Message from {RealtimeService._get_message_sender(message_data)}'
            }
            
            # Emit to business owner
            RealtimeService.emit_to_business(business_id, 'new_message', notification_data)
            
            # Also emit general notification
            RealtimeService.emit_to_business(business_id, 'notification', {
                'type': 'message',
                'message': notification_data['message'],
                'title': notification_data['title'],
                'action_url': '/dashboard/messages'
            })
            
            logger.info(f"Real-time message notification sent for {message_type} to business {business_id}")
            
        except Exception as e:
            logger.error(f"Error sending real-time message notification: {str(e)}")
    
    @staticmethod
    def notify_new_customer(business_id, customer_data):
        """
        Notify business owner of new customer registration
        """
        try:
            notification_data = {
                'type': 'new_customer',
                'customer_name': customer_data.get('name', 'New Customer'),
                'customer_email': customer_data.get('email', ''),
                'source': customer_data.get('registration_source', 'mini_website'),
                'priority': 'low',
                'title': 'New Customer Registered',
                'message': f'New customer: {customer_data.get("name", "Unknown")} ({customer_data.get("email", "")})'
            }
            
            # Emit to business owner
            RealtimeService.emit_to_business(business_id, 'new_customer', notification_data)
            
            logger.info(f"Real-time customer notification sent to business {business_id}")
            
        except Exception as e:
            logger.error(f"Error sending real-time customer notification: {str(e)}")
    
    @staticmethod
    def notify_newsletter_signup(business_id, subscriber_data):
        """
        Notify business owner of new newsletter signup
        """
        try:
            notification_data = {
                'type': 'newsletter_signup',
                'subscriber_name': subscriber_data.get('name', 'New Subscriber'),
                'subscriber_email': subscriber_data.get('email', ''),
                'source': 'mini_website',
                'priority': 'low',
                'title': 'New Newsletter Subscriber',
                'message': f'New newsletter signup: {subscriber_data.get("name", subscriber_data.get("email", "Unknown"))}'
            }
            
            # Emit to business owner
            RealtimeService.emit_to_business(business_id, 'newsletter_signup', notification_data)
            
            # Also emit general notification
            RealtimeService.emit_to_business(business_id, 'notification', {
                'type': 'newsletter',
                'message': notification_data['message'],
                'title': notification_data['title'],
                'action_url': '/dashboard/customers?filter=subscribed'
            })
            
            logger.info(f"Real-time newsletter signup notification sent to business {business_id}")
            
        except Exception as e:
            logger.error(f"Error sending real-time newsletter notification: {str(e)}")
    
    @staticmethod
    def notify_new_feedback(business_id, feedback_data):
        """
        Notify business owner of new feedback with sentiment analysis
        """
        try:
            sentiment = feedback_data.get('sentiment_analysis', {}).get('sentiment', 'neutral')
            rating = feedback_data.get('rating', 0)
            
            # Choose appropriate emoji and priority based on sentiment and rating
            if sentiment == 'positive' or rating >= 4:
                emoji = "😊"
                priority = 'low'
            elif sentiment == 'negative' or rating <= 2:
                emoji = "😔"
                priority = 'high'
            else:
                emoji = "😐"
                priority = 'medium'
            
            notification_data = {
                'type': 'new_feedback',
                'customer_name': feedback_data.get('customer_name', 'Anonymous'),
                'customer_email': feedback_data.get('customer_email', ''),
                'rating': rating,
                'sentiment': sentiment,
                'feedback_text': feedback_data.get('feedback_text', ''),
                'source': 'mini_website',
                'priority': priority,
                'title': f'New Feedback {emoji}',
                'message': f'{sentiment.title()} feedback ({rating}/5 stars) from {feedback_data.get("customer_name", "Anonymous")}'
            }
            
            # Emit to business owner
            RealtimeService.emit_to_business(business_id, 'new_feedback', notification_data)
            
            # Also emit general notification
            RealtimeService.emit_to_business(business_id, 'notification', {
                'type': 'feedback',
                'message': notification_data['message'],
                'title': notification_data['title'],
                'action_url': '/dashboard/feedback',
                'priority': priority
            })
            
            logger.info(f"Real-time feedback notification sent to business {business_id} - {sentiment} sentiment")
            
        except Exception as e:
            logger.error(f"Error sending real-time feedback notification: {str(e)}")
    
    @staticmethod
    def sync_dashboard_data(business_id, data_type, data):
        """
        Sync specific data changes to dashboard in real-time
        """
        try:
            sync_data = {
                'type': 'data_sync',
                'data_type': data_type,
                'data': data,
                'action': 'update'
            }
            
            # Emit sync event
            RealtimeService.emit_to_business(business_id, 'data_sync', sync_data)
            
            logger.info(f"Data sync sent for {data_type} to business {business_id}")
            
        except Exception as e:
            logger.error(f"Error syncing data: {str(e)}")
    
    @staticmethod
    def broadcast_system_notification(message, priority='medium'):
        """
        Broadcast system-wide notification to all connected users
        """
        try:
            notification_data = {
                'type': 'system_notification',
                'message': message,
                'priority': priority,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            socketio.emit('system_notification', notification_data, broadcast=True)
            
            logger.info(f"System notification broadcasted: {message}")
            
        except Exception as e:
            logger.error(f"Error broadcasting system notification: {str(e)}")
    
    @staticmethod
    def notify_booking_status_change(business_id, booking_id, old_status, new_status, booking_type):
        """
        Notify about booking status changes
        """
        try:
            notification_data = {
                'type': 'booking_status_change',
                'booking_id': booking_id,
                'booking_type': booking_type,
                'old_status': old_status,
                'new_status': new_status,
                'title': 'Booking Status Updated',
                'message': f'Booking status changed from {old_status} to {new_status}'
            }
            
            RealtimeService.emit_to_business(business_id, 'booking_status_change', notification_data)
            
            logger.info(f"Booking status change notification sent to business {business_id}")
            
        except Exception as e:
            logger.error(f"Error sending booking status change notification: {str(e)}")
    
    @staticmethod
    def _get_customer_name(booking_data):
        """Extract customer name from booking data"""
        try:
            if 'client_info' in booking_data:
                # Law firm consultation booking
                return f"{booking_data['client_info'].get('first_name', '')} {booking_data['client_info'].get('last_name', '')}".strip()
            elif 'customer_info' in booking_data:
                # Tailor shop booking or order inquiry
                if 'first_name' in booking_data['customer_info']:
                    return f"{booking_data['customer_info'].get('first_name', '')} {booking_data['customer_info'].get('last_name', '')}".strip()
                else:
                    return booking_data['customer_info'].get('name', 'Unknown Customer')
            else:
                return 'Unknown Customer'
        except:
            return 'Unknown Customer'
    
    @staticmethod
    def _get_service_name(booking_data):
        """Extract service name from booking data"""
        try:
            if 'consultation_details' in booking_data:
                return booking_data['consultation_details'].get('practice_area', 'Legal Consultation')
            elif 'booking_details' in booking_data:
                return booking_data['booking_details'].get('service_type', 'Tailoring Service')
            elif 'order_details' in booking_data:
                return booking_data['order_details'].get('service_type', 'Custom Order')
            else:
                return 'Service'
        except:
            return 'Service'
    
    @staticmethod
    def _get_message_sender(message_data):
        """Extract sender name from message data"""
        try:
            if 'client_info' in message_data:
                return f"{message_data['client_info'].get('first_name', '')} {message_data['client_info'].get('last_name', '')}".strip()
            elif 'customer_info' in message_data:
                if 'first_name' in message_data['customer_info']:
                    return f"{message_data['customer_info'].get('first_name', '')} {message_data['customer_info'].get('last_name', '')}".strip()
                else:
                    return message_data['customer_info'].get('name', 'Unknown')
            else:
                return 'Unknown Sender'
        except:
            return 'Unknown Sender'

# Initialize global realtime service
realtime_service = RealtimeService()

def get_realtime_service():
    """Get realtime service instance"""
    return realtime_service