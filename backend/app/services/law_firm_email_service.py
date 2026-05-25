"""
Email Automation Service for Law Firms - Handles automated email communications
"""

import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class LawFirmEmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = os.getenv('EMAIL_USER', 'your-email@gmail.com')
        self.email_password = os.getenv('EMAIL_PASSWORD', 'your-app-password')
        
        # Email templates
        self.templates = {
            'consultation_confirmation': self._get_consultation_confirmation_template(),
            'contact_inquiry_response': self._get_contact_inquiry_template(),
            'newsletter_welcome': self._get_newsletter_welcome_template(),
            'consultation_reminder': self._get_consultation_reminder_template(),
            'follow_up': self._get_follow_up_template(),
            'business_card_delivery': self._get_business_card_template()
        }
    
    def send_consultation_confirmation(self, firm_data: dict, consultation_data: dict) -> dict:
        """Send consultation booking confirmation email"""
        try:
            # Prepare email data
            client_email = consultation_data.get('email')
            client_name = consultation_data.get('name')
            consultation_date = consultation_data.get('date')
            consultation_time = consultation_data.get('time')
            legal_matter = consultation_data.get('legalMatter', 'Legal Consultation')
            
            # Get attorney information
            attorney_name = consultation_data.get('attorney', 'Our Legal Team')
            firm_name = firm_data.get('firmName', 'Law Firm')
            firm_phone = firm_data.get('phoneNumber', '(555) 123-4567')
            firm_address = f"{firm_data.get('officeAddress', '')}, {firm_data.get('city', '')}, {firm_data.get('state', '')}"
            
            # Generate email content
            subject = f"Consultation Confirmed - {firm_name}"
            
            template_data = {
                'client_name': client_name,
                'firm_name': firm_name,
                'attorney_name': attorney_name,
                'consultation_date': consultation_date,
                'consultation_time': consultation_time,
                'legal_matter': legal_matter,
                'firm_phone': firm_phone,
                'firm_address': firm_address,
                'confirmation_number': consultation_data.get('_id', 'N/A')
            }
            
            html_content = self.templates['consultation_confirmation'].format(**template_data)
            
            # Send email
            result = self._send_email(
                to_email=client_email,
                subject=subject,
                html_content=html_content,
                from_name=firm_name
            )
            
            if result['success']:
                logger.info(f"Consultation confirmation sent to {client_email}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending consultation confirmation: {e}")
            return {"success": False, "error": str(e)}
    
    def send_contact_inquiry_response(self, firm_data: dict, contact_data: dict) -> dict:
        """Send automated response to contact form submissions"""
        try:
            client_email = contact_data.get('email')
            client_name = contact_data.get('name')
            inquiry_subject = contact_data.get('subject', 'Legal Inquiry')
            firm_name = firm_data.get('firmName', 'Law Firm')
            
            subject = f"Thank you for contacting {firm_name}"
            
            template_data = {
                'client_name': client_name,
                'firm_name': firm_name,
                'inquiry_subject': inquiry_subject,
                'firm_phone': firm_data.get('phoneNumber', '(555) 123-4567'),
                'firm_email': firm_data.get('emailAddress', 'info@lawfirm.com'),
                'response_time': '24 hours'
            }
            
            html_content = self.templates['contact_inquiry_response'].format(**template_data)
            
            result = self._send_email(
                to_email=client_email,
                subject=subject,
                html_content=html_content,
                from_name=firm_name
            )
            
            if result['success']:
                logger.info(f"Contact inquiry response sent to {client_email}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending contact inquiry response: {e}")
            return {"success": False, "error": str(e)}
    
    def send_newsletter_welcome(self, firm_data: dict, subscriber_data: dict) -> dict:
        """Send welcome email to newsletter subscribers"""
        try:
            subscriber_email = subscriber_data.get('email')
            firm_name = firm_data.get('firmName', 'Law Firm')
            
            subject = f"Welcome to {firm_name} Legal Updates"
            
            template_data = {
                'firm_name': firm_name,
                'firm_tagline': firm_data.get('firmTagline', 'Excellence in Legal Advocacy'),
                'website_url': firm_data.get('website_url', '#'),
                'unsubscribe_url': f"{firm_data.get('website_url', '#')}/unsubscribe?email={subscriber_email}"
            }
            
            html_content = self.templates['newsletter_welcome'].format(**template_data)
            
            result = self._send_email(
                to_email=subscriber_email,
                subject=subject,
                html_content=html_content,
                from_name=firm_name
            )
            
            if result['success']:
                logger.info(f"Newsletter welcome sent to {subscriber_email}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending newsletter welcome: {e}")
            return {"success": False, "error": str(e)}
    
    def send_consultation_reminder(self, firm_data: dict, consultation_data: dict, days_before: int = 1) -> dict:
        """Send consultation reminder email"""
        try:
            client_email = consultation_data.get('email')
            client_name = consultation_data.get('name')
            consultation_date = consultation_data.get('date')
            consultation_time = consultation_data.get('time')
            firm_name = firm_data.get('firmName', 'Law Firm')
            
            subject = f"Consultation Reminder - {firm_name}"
            
            template_data = {
                'client_name': client_name,
                'firm_name': firm_name,
                'consultation_date': consultation_date,
                'consultation_time': consultation_time,
                'days_before': days_before,
                'firm_phone': firm_data.get('phoneNumber', '(555) 123-4567'),
                'firm_address': f"{firm_data.get('officeAddress', '')}, {firm_data.get('city', '')}, {firm_data.get('state', '')}"
            }
            
            html_content = self.templates['consultation_reminder'].format(**template_data)
            
            result = self._send_email(
                to_email=client_email,
                subject=subject,
                html_content=html_content,
                from_name=firm_name
            )
            
            if result['success']:
                logger.info(f"Consultation reminder sent to {client_email}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending consultation reminder: {e}")
            return {"success": False, "error": str(e)}
    
    def send_business_card_delivery(self, firm_data: dict, attorney_data: dict, card_urls: dict) -> dict:
        """Send business card delivery email to attorney"""
        try:
            attorney_email = attorney_data.get('email', firm_data.get('emailAddress'))
            attorney_name = attorney_data.get('name', 'Attorney')
            firm_name = firm_data.get('firmName', 'Law Firm')
            
            subject = f"Your Business Cards are Ready - {firm_name}"
            
            template_data = {
                'attorney_name': attorney_name,
                'firm_name': firm_name,
                'front_card_url': card_urls.get('front_image', '#'),
                'back_card_url': card_urls.get('back_image', '#'),
                'download_instructions': 'Right-click and select "Save As" to download your business cards.'
            }
            
            html_content = self.templates['business_card_delivery'].format(**template_data)
            
            result = self._send_email(
                to_email=attorney_email,
                subject=subject,
                html_content=html_content,
                from_name=firm_name
            )
            
            if result['success']:
                logger.info(f"Business card delivery sent to {attorney_email}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending business card delivery: {e}")
            return {"success": False, "error": str(e)}
    
    def _send_email(self, to_email: str, subject: str, html_content: str, from_name: str = "Law Firm") -> dict:
        """Send email using Gmail SMTP"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{from_name} <{self.email_user}>"
            message["To"] = to_email
            
            # Create HTML part
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_user, self.email_password)
                server.sendmail(self.email_user, to_email, message.as_string())
            
            return {"success": True, "message": "Email sent successfully"}
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_consultation_confirmation_template(self) -> str:
        """Get consultation confirmation email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Consultation Confirmed</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; margin-top: 20px; }}
                .header {{ background: linear-gradient(135deg, #1a365d, #2d3748); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; }}
                .appointment-details {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #d4af37; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #d4af37, #b8941a); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
                .highlight {{ color: #d4af37; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{firm_name}</h1>
                    <p>Your consultation has been confirmed</p>
                </div>
                
                <div class="content">
                    <h2>Dear {client_name},</h2>
                    
                    <p>Thank you for scheduling a consultation with <span class="highlight">{firm_name}</span>. We appreciate the opportunity to discuss your legal matter and provide you with expert guidance.</p>
                    
                    <div class="appointment-details">
                        <h3>📅 Consultation Details</h3>
                        <p><strong>Date:</strong> {consultation_date}</p>
                        <p><strong>Time:</strong> {consultation_time}</p>
                        <p><strong>Attorney:</strong> {attorney_name}</p>
                        <p><strong>Legal Matter:</strong> {legal_matter}</p>
                        <p><strong>Confirmation #:</strong> {confirmation_number}</p>
                    </div>
                    
                    <h3>📍 Location & Contact</h3>
                    <p><strong>Address:</strong> {firm_address}</p>
                    <p><strong>Phone:</strong> {firm_phone}</p>
                    
                    <h3>📋 What to Bring</h3>
                    <ul>
                        <li>Any relevant documents related to your case</li>
                        <li>List of questions you'd like to discuss</li>
                        <li>Valid photo identification</li>
                        <li>Method of payment for consultation fee (if applicable)</li>
                    </ul>
                    
                    <p><strong>Please arrive 10 minutes early</strong> to allow time for check-in and parking.</p>
                    
                    <p>If you need to reschedule or cancel, please contact us at least 24 hours in advance at <span class="highlight">{firm_phone}</span>.</p>
                </div>
                
                <div class="footer">
                    <p>We look forward to meeting with you!</p>
                    <p><strong>{firm_name}</strong><br>
                    Excellence in Legal Advocacy</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_contact_inquiry_template(self) -> str:
        """Get contact inquiry response template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Thank You for Your Inquiry</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; margin-top: 20px; }}
                .header {{ background: linear-gradient(135deg, #1a365d, #2d3748); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; }}
                .highlight {{ color: #d4af37; font-weight: bold; }}
                .contact-info {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{firm_name}</h1>
                    <p>Thank you for reaching out to us</p>
                </div>
                
                <div class="content">
                    <h2>Dear {client_name},</h2>
                    
                    <p>Thank you for contacting <span class="highlight">{firm_name}</span> regarding <strong>"{inquiry_subject}"</strong>. We have received your inquiry and appreciate the opportunity to assist you with your legal needs.</p>
                    
                    <p>Our team will review your message and respond within <span class="highlight">{response_time}</span>. We understand that legal matters can be time-sensitive, and we are committed to providing you with prompt, professional service.</p>
                    
                    <div class="contact-info">
                        <h3>📞 Need Immediate Assistance?</h3>
                        <p>If your matter is urgent, please don't hesitate to call us directly:</p>
                        <p><strong>Phone:</strong> {firm_phone}</p>
                        <p><strong>Email:</strong> {firm_email}</p>
                    </div>
                    
                    <h3>What Happens Next?</h3>
                    <ol>
                        <li>Our legal team will review your inquiry</li>
                        <li>We'll contact you to discuss your case in detail</li>
                        <li>If appropriate, we'll schedule a consultation</li>
                        <li>We'll provide you with expert legal guidance</li>
                    </ol>
                    
                    <p>At <span class="highlight">{firm_name}</span>, we are dedicated to providing exceptional legal representation and personalized service to each of our clients.</p>
                </div>
                
                <div class="footer">
                    <p>We look forward to speaking with you soon!</p>
                    <p><strong>{firm_name}</strong><br>
                    Excellence in Legal Advocacy</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_newsletter_welcome_template(self) -> str:
        """Get newsletter welcome template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Our Newsletter</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; margin-top: 20px; }}
                .header {{ background: linear-gradient(135deg, #1a365d, #2d3748); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; }}
                .highlight {{ color: #d4af37; font-weight: bold; }}
                .newsletter-benefits {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to {firm_name}</h1>
                    <p>{firm_tagline}</p>
                </div>
                
                <div class="content">
                    <h2>Thank you for subscribing!</h2>
                    
                    <p>Welcome to the <span class="highlight">{firm_name}</span> newsletter! You've taken an important step in staying informed about legal developments that could affect you.</p>
                    
                    <div class="newsletter-benefits">
                        <h3>📰 What You'll Receive:</h3>
                        <ul>
                            <li><strong>Legal Updates:</strong> Important changes in the law</li>
                            <li><strong>Expert Insights:</strong> Analysis from our experienced attorneys</li>
                            <li><strong>Practice Tips:</strong> Practical legal advice for everyday situations</li>
                            <li><strong>Firm News:</strong> Updates about our team and services</li>
                            <li><strong>Exclusive Content:</strong> Newsletter-only legal resources</li>
                        </ul>
                    </div>
                    
                    <p>Our newsletter is published monthly and contains valuable information carefully curated by our legal team to help you navigate complex legal matters.</p>
                    
                    <h3>🤝 Need Legal Assistance?</h3>
                    <p>If you have immediate legal questions or need professional representation, don't hesitate to contact us. Our experienced team is here to help.</p>
                    
                    <p style="text-align: center;">
                        <a href="{website_url}" style="display: inline-block; background: linear-gradient(135deg, #d4af37, #b8941a); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 10px 0;">Visit Our Website</a>
                    </p>
                </div>
                
                <div class="footer">
                    <p>Thank you for trusting <strong>{firm_name}</strong> with your legal information needs.</p>
                    <p><small><a href="{unsubscribe_url}">Unsubscribe</a> | This email was sent to you because you subscribed to our newsletter.</small></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_consultation_reminder_template(self) -> str:
        """Get consultation reminder template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Consultation Reminder</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; margin-top: 20px; }}
                .header {{ background: linear-gradient(135deg, #1a365d, #2d3748); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; }}
                .reminder-box {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .highlight {{ color: #d4af37; font-weight: bold; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⏰ Consultation Reminder</h1>
                    <p>{firm_name}</p>
                </div>
                
                <div class="content">
                    <h2>Dear {client_name},</h2>
                    
                    <div class="reminder-box">
                        <h3>📅 Your consultation is in {days_before} day(s)!</h3>
                        <p><strong>Date:</strong> {consultation_date}</p>
                        <p><strong>Time:</strong> {consultation_time}</p>
                        <p><strong>Location:</strong> {firm_address}</p>
                    </div>
                    
                    <p>This is a friendly reminder about your upcoming consultation with <span class="highlight">{firm_name}</span>.</p>
                    
                    <h3>📋 Preparation Checklist:</h3>
                    <ul>
                        <li>✓ Gather all relevant documents</li>
                        <li>✓ Prepare your questions</li>
                        <li>✓ Bring valid photo ID</li>
                        <li>✓ Plan to arrive 10 minutes early</li>
                    </ul>
                    
                    <p><strong>Need to reschedule?</strong> Please call us as soon as possible at <span class="highlight">{firm_phone}</span>.</p>
                    
                    <p>We look forward to meeting with you and discussing your legal matter.</p>
                </div>
                
                <div class="footer">
                    <p><strong>{firm_name}</strong><br>
                    Excellence in Legal Advocacy</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_follow_up_template(self) -> str:
        """Get follow-up email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Follow-up from {firm_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; margin-top: 20px; }}
                .header {{ background: linear-gradient(135deg, #1a365d, #2d3748); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; }}
                .highlight {{ color: #d4af37; font-weight: bold; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{firm_name}</h1>
                    <p>Following up on your legal matter</p>
                </div>
                
                <div class="content">
                    <h2>Dear {client_name},</h2>
                    
                    <p>We wanted to follow up regarding your recent consultation with <span class="highlight">{firm_name}</span>.</p>
                    
                    <p>At our firm, we believe in maintaining strong relationships with our clients and ensuring that all your legal needs are met with the highest level of professionalism and care.</p>
                    
                    <h3>🤝 How Can We Continue to Help?</h3>
                    <ul>
                        <li>Schedule a follow-up consultation</li>
                        <li>Answer any additional questions</li>
                        <li>Provide ongoing legal representation</li>
                        <li>Connect you with specialized legal resources</li>
                    </ul>
                    
                    <p>Please don't hesitate to contact us if you need any assistance or have questions about your legal matter.</p>
                </div>
                
                <div class="footer">
                    <p><strong>{firm_name}</strong><br>
                    Excellence in Legal Advocacy</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_business_card_template(self) -> str:
        """Get business card delivery template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your Business Cards are Ready</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; margin-top: 20px; }}
                .header {{ background: linear-gradient(135deg, #1a365d, #2d3748); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; }}
                .card-preview {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
                .download-btn {{ display: inline-block; background: linear-gradient(135deg, #d4af37, #b8941a); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 10px; }}
                .highlight {{ color: #d4af37; font-weight: bold; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 Your Business Cards are Ready!</h1>
                    <p>{firm_name}</p>
                </div>
                
                <div class="content">
                    <h2>Dear {attorney_name},</h2>
                    
                    <p>Great news! Your professional business cards have been generated and are ready for download.</p>
                    
                    <div class="card-preview">
                        <h3>📱 Download Your Business Cards</h3>
                        <p>Click the buttons below to download high-quality images of your business cards:</p>
                        
                        <a href="{front_card_url}" class="download-btn" target="_blank">
                            📄 Download Front
                        </a>
                        
                        <a href="{back_card_url}" class="download-btn" target="_blank">
                            📄 Download Back
                        </a>
                    </div>
                    
                    <h3>💡 Usage Tips:</h3>
                    <ul>
                        <li><strong>Print Quality:</strong> These cards are designed at 300 DPI for professional printing</li>
                        <li><strong>Paper Recommendation:</strong> Use premium cardstock (14pt or heavier) for best results</li>
                        <li><strong>Size:</strong> Standard business card size (3.5" x 2")</li>
                        <li><strong>Digital Use:</strong> Perfect for email signatures and social media</li>
                    </ul>
                    
                    <p><strong>Download Instructions:</strong> {download_instructions}</p>
                    
                    <p>If you need any modifications or have questions about your business cards, please don't hesitate to contact us.</p>
                </div>
                
                <div class="footer">
                    <p>Professional business cards for professional attorneys!</p>
                    <p><strong>{firm_name}</strong><br>
                    Excellence in Legal Advocacy</p>
                </div>
            </div>
        </body>
        </html>
        """