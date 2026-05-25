"""
Beauty Salon Email Service - Handles email communications for spa/salon
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class BeautySalonEmailService:
    """Service for managing spa/salon email communications"""
    
    def __init__(self):
        # Email configuration (in real implementation, use environment variables)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = "your-spa-email@gmail.com"  # Configure with real email
        self.email_password = "your-app-password"      # Configure with real password
    
    def setup_automation(self, salon_data: dict) -> dict:
        """Setup email automation for the salon"""
        try:
            salon_id = salon_data.get('salon_id')
            salon_name = salon_data.get('salon_name', 'Beauty Salon')
            email_address = salon_data.get('email_address')
            
            logger.info(f"Setting up email automation for: {salon_name}")
            
            # Configure email automation
            automation_config = {
                'salon_id': salon_id,
                'salon_name': salon_name,
                'sender_email': email_address,
                'templates': {
                    'appointment_confirmation': True,
                    'appointment_reminder': True,
                    'welcome_email': True,
                    'promotional_emails': True
                },
                'automation_enabled': True
            }
            
            return {
                'success': True,
                'automation_config': automation_config,
                'message': 'Email automation setup completed'
            }
            
        except Exception as e:
            logger.error(f"Error setting up email automation: {e}")
            return {
                'success': False,
                'error': f'Email automation setup failed: {str(e)}'
            }
        
    def send_appointment_confirmation(self, appointment_data: Dict) -> Dict:
        """Send appointment confirmation email"""
        try:
            subject = f"Appointment Confirmation - {appointment_data.get('salon_name', 'Luxury Spa')}"
            
            # Create email content
            html_content = self._create_appointment_confirmation_html(appointment_data)
            text_content = self._create_appointment_confirmation_text(appointment_data)
            
            # Send email
            result = self._send_email(
                to_email=appointment_data.get('client_email'),
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if result.get('success'):
                logger.info(f"Appointment confirmation sent to {appointment_data.get('client_email')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending appointment confirmation: {e}")
            return {
                "success": False,
                "error": "Failed to send confirmation email"
            }
    
    def send_appointment_reminder(self, appointment_data: Dict) -> Dict:
        """Send appointment reminder email"""
        try:
            subject = f"Appointment Reminder - Tomorrow at {appointment_data.get('appointment_time')}"
            
            # Create email content
            html_content = self._create_appointment_reminder_html(appointment_data)
            text_content = self._create_appointment_reminder_text(appointment_data)
            
            # Send email
            result = self._send_email(
                to_email=appointment_data.get('client_email'),
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if result.get('success'):
                logger.info(f"Appointment reminder sent to {appointment_data.get('client_email')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending appointment reminder: {e}")
            return {
                "success": False,
                "error": "Failed to send reminder email"
            }
    
    def send_follow_up_email(self, appointment_data: Dict) -> Dict:
        """Send follow-up email after appointment"""
        try:
            subject = f"Thank you for visiting {appointment_data.get('salon_name', 'our spa')}!"
            
            # Create email content
            html_content = self._create_follow_up_html(appointment_data)
            text_content = self._create_follow_up_text(appointment_data)
            
            # Send email
            result = self._send_email(
                to_email=appointment_data.get('client_email'),
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if result.get('success'):
                logger.info(f"Follow-up email sent to {appointment_data.get('client_email')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending follow-up email: {e}")
            return {
                "success": False,
                "error": "Failed to send follow-up email"
            }
    
    def send_promotional_email(self, client_data: Dict, promotion_data: Dict) -> Dict:
        """Send promotional email to client"""
        try:
            subject = promotion_data.get('subject', 'Special Offer Just for You!')
            
            # Create email content
            html_content = self._create_promotional_html(client_data, promotion_data)
            text_content = self._create_promotional_text(client_data, promotion_data)
            
            # Send email
            result = self._send_email(
                to_email=client_data.get('email'),
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if result.get('success'):
                logger.info(f"Promotional email sent to {client_data.get('email')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending promotional email: {e}")
            return {
                "success": False,
                "error": "Failed to send promotional email"
            }
    
    def _send_email(self, to_email: str, subject: str, html_content: str, text_content: str) -> Dict:
        """Send email using SMTP (simulated for now)"""
        try:
            # In a real implementation, configure SMTP properly
            # For now, we'll simulate email sending
            
            logger.info(f"Simulating email send to: {to_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Content length: {len(html_content)} characters")
            
            # Simulate successful email send
            return {
                "success": True,
                "message": "Email sent successfully",
                "recipient": to_email,
                "subject": subject,
                "sent_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in email sending: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_appointment_confirmation_html(self, appointment_data: Dict) -> str:
        """Create HTML content for appointment confirmation"""
        salon_name = appointment_data.get('salon_name', 'Luxury Spa')
        client_name = appointment_data.get('client_name', 'Valued Client')
        service_type = appointment_data.get('service_type', 'Spa Service')
        appointment_date = appointment_data.get('appointment_date', '')
        appointment_time = appointment_data.get('appointment_time', '')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .header {{ background: linear-gradient(135deg, #8b9b9b, #d4af37); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .appointment-details {{ background: #f5f9f9; padding: 15px; margin: 20px 0; border-radius: 8px; }}
                .footer {{ background: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{salon_name}</h1>
                <p>Your Appointment is Confirmed!</p>
            </div>
            
            <div class="content">
                <h2>Dear {client_name},</h2>
                
                <p>Thank you for choosing {salon_name}! We're excited to pamper you with our professional services.</p>
                
                <div class="appointment-details">
                    <h3>Appointment Details:</h3>
                    <p><strong>Service:</strong> {service_type}</p>
                    <p><strong>Date:</strong> {appointment_date}</p>
                    <p><strong>Time:</strong> {appointment_time}</p>
                    <p><strong>Status:</strong> Confirmed</p>
                </div>
                
                <h3>What to Expect:</h3>
                <ul>
                    <li>Please arrive 15 minutes early for check-in</li>
                    <li>Bring a valid ID for verification</li>
                    <li>Let us know if you have any allergies or special requirements</li>
                    <li>Feel free to ask our staff any questions</li>
                </ul>
                
                <p>We look forward to providing you with a relaxing and rejuvenating experience!</p>
                
                <p>Need to reschedule or have questions? Contact us anytime.</p>
            </div>
            
            <div class="footer">
                <p>This is an automated message from {salon_name}</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_appointment_confirmation_text(self, appointment_data: Dict) -> str:
        """Create text content for appointment confirmation"""
        salon_name = appointment_data.get('salon_name', 'Luxury Spa')
        client_name = appointment_data.get('client_name', 'Valued Client')
        service_type = appointment_data.get('service_type', 'Spa Service')
        appointment_date = appointment_data.get('appointment_date', '')
        appointment_time = appointment_data.get('appointment_time', '')
        
        text = f"""
        {salon_name} - Appointment Confirmation
        
        Dear {client_name},
        
        Thank you for choosing {salon_name}! Your appointment is confirmed.
        
        Appointment Details:
        - Service: {service_type}
        - Date: {appointment_date}
        - Time: {appointment_time}
        - Status: Confirmed
        
        Please arrive 15 minutes early for check-in. We look forward to seeing you!
        
        Best regards,
        {salon_name} Team
        """
        
        return text
    
    def _create_appointment_reminder_html(self, appointment_data: Dict) -> str:
        """Create HTML content for appointment reminder"""
        salon_name = appointment_data.get('salon_name', 'Luxury Spa')
        client_name = appointment_data.get('client_name', 'Valued Client')
        service_type = appointment_data.get('service_type', 'Spa Service')
        appointment_time = appointment_data.get('appointment_time', '')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .header {{ background: linear-gradient(135deg, #8b9b9b, #d4af37); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .reminder-box {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 20px 0; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{salon_name}</h1>
                <p>Appointment Reminder</p>
            </div>
            
            <div class="content">
                <h2>Hello {client_name}!</h2>
                
                <div class="reminder-box">
                    <h3>⏰ Reminder: Your appointment is tomorrow!</h3>
                    <p><strong>Service:</strong> {service_type}</p>
                    <p><strong>Time:</strong> {appointment_time}</p>
                </div>
                
                <p>We're looking forward to seeing you tomorrow for your {service_type} appointment!</p>
                
                <p>Remember to arrive 15 minutes early. If you need to reschedule, please let us know as soon as possible.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_appointment_reminder_text(self, appointment_data: Dict) -> str:
        """Create text content for appointment reminder"""
        salon_name = appointment_data.get('salon_name', 'Luxury Spa')
        client_name = appointment_data.get('client_name', 'Valued Client')
        service_type = appointment_data.get('service_type', 'Spa Service')
        appointment_time = appointment_data.get('appointment_time', '')
        
        text = f"""
        {salon_name} - Appointment Reminder
        
        Hello {client_name}!
        
        This is a reminder that you have an appointment tomorrow:
        - Service: {service_type}
        - Time: {appointment_time}
        
        Please arrive 15 minutes early. We're looking forward to seeing you!
        
        {salon_name} Team
        """
        
        return text
    
    def _create_follow_up_html(self, appointment_data: Dict) -> str:
        """Create HTML content for follow-up email"""
        salon_name = appointment_data.get('salon_name', 'Luxury Spa')
        client_name = appointment_data.get('client_name', 'Valued Client')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .header {{ background: linear-gradient(135deg, #8b9b9b, #d4af37); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .feedback-box {{ background: #e8f4f8; padding: 15px; margin: 20px 0; border-radius: 8px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{salon_name}</h1>
                <p>Thank You for Visiting!</p>
            </div>
            
            <div class="content">
                <h2>Dear {client_name},</h2>
                
                <p>Thank you for choosing {salon_name} for your beauty and wellness needs. We hope you had a wonderful and relaxing experience with us!</p>
                
                <div class="feedback-box">
                    <h3>How was your experience?</h3>
                    <p>We'd love to hear your feedback! Your input helps us continue providing exceptional service.</p>
                </div>
                
                <h3>Special Offers for You:</h3>
                <ul>
                    <li>Book your next appointment within 30 days and receive 10% off</li>
                    <li>Refer a friend and both receive 15% off your next service</li>
                    <li>Follow us on social media for exclusive offers</li>
                </ul>
                
                <p>We look forward to seeing you again soon!</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_follow_up_text(self, appointment_data: Dict) -> str:
        """Create text content for follow-up email"""
        salon_name = appointment_data.get('salon_name', 'Luxury Spa')
        client_name = appointment_data.get('client_name', 'Valued Client')
        
        text = f"""
        {salon_name} - Thank You!
        
        Dear {client_name},
        
        Thank you for visiting {salon_name}! We hope you had a wonderful experience.
        
        Special offers for you:
        - 10% off your next appointment if booked within 30 days
        - 15% off when you refer a friend
        
        We'd love your feedback and look forward to seeing you again!
        
        Best regards,
        {salon_name} Team
        """
        
        return text
    
    def _create_promotional_html(self, client_data: Dict, promotion_data: Dict) -> str:
        """Create HTML content for promotional email"""
        client_name = client_data.get('name', 'Valued Client')
        promotion_title = promotion_data.get('title', 'Special Offer')
        promotion_description = promotion_data.get('description', 'Limited time offer on our spa services')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .header {{ background: linear-gradient(135deg, #ff69b4, #d4af37); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .offer-box {{ background: #ffe4e1; border: 2px solid #ff69b4; padding: 20px; margin: 20px 0; border-radius: 8px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{promotion_title}</h1>
                <p>Exclusive Offer Just for You!</p>
            </div>
            
            <div class="content">
                <h2>Dear {client_name},</h2>
                
                <div class="offer-box">
                    <h3>🌸 {promotion_title} 🌸</h3>
                    <p>{promotion_description}</p>
                </div>
                
                <p>Don't miss out on this amazing opportunity to treat yourself to our luxury spa services!</p>
                
                <p>Book now to secure your spot and enjoy this exclusive offer.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_promotional_text(self, client_data: Dict, promotion_data: Dict) -> str:
        """Create text content for promotional email"""
        client_name = client_data.get('name', 'Valued Client')
        promotion_title = promotion_data.get('title', 'Special Offer')
        promotion_description = promotion_data.get('description', 'Limited time offer on our spa services')
        
        text = f"""
        {promotion_title}
        
        Dear {client_name},
        
        {promotion_description}
        
        Book now to secure your spot and enjoy this exclusive offer!
        
        Limited time only.
        """
        
        return text