# app/services/email_service.py - FIXED VERSION
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import logging
import html

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Gmail SMTP configuration
        self.smtp_server = "smtp.gmail.com"
        self.port = 587  # For starttls
        
        # Email credentials from environment variables
        self.sender_email = os.environ.get('GMAIL_EMAIL', 'pulluripranavi@gmail.com')
        self.sender_password = os.environ.get('GMAIL_APP_PASSWORD', 'lxwr gdrb pgvz raoh')
        
        # Fallback credentials for testing (replace with your actual credentials)
        if self.sender_email == 'your-email@gmail.com':
            # You can set these for testing - REPLACE WITH YOUR ACTUAL CREDENTIALS
            self.sender_email = "pulluripranavi@gmail.com"  # Replace with your Gmail
            self.sender_password = "lxwr gdrb pgvz raoh"  # Replace with your App Password
    
    def test_connection(self):
        """Test SMTP connection without sending an email"""
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
            return {
                'success': True,
                'message': 'SMTP connection and authentication successful',
                'sender_email': self.sender_email
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'help': 'Make sure you are using a Gmail App Password (not your regular password). Generate one at https://myaccount.google.com/apppasswords'
            }
    
    def clean_content(self, content):
        """Clean content to handle encoding issues"""
        try:
            # Remove or replace problematic characters
            if isinstance(content, str):
                # Replace common emoji and special characters
                replacements = {
                    '🚀': 'ROCKET',
                    '✅': 'CHECK',
                    '❌': 'X',
                    '📧': 'EMAIL',
                    '🎉': 'PARTY',
                    '⚠️': 'WARNING',
                    '📱': 'PHONE',
                    '💰': 'MONEY',
                    '🔥': 'FIRE',
                    '⭐': 'STAR',
                    '💡': 'BULB',
                    '🎯': 'TARGET',
                    '📈': 'CHART',
                    '🌟': 'STAR',
                    # Add more emoji replacements as needed
                }
                
                cleaned_content = content
                for emoji, replacement in replacements.items():
                    cleaned_content = cleaned_content.replace(emoji, replacement)
                
                # Ensure content is properly encoded
                return cleaned_content.encode('ascii', 'ignore').decode('ascii')
            
            return str(content)
        except Exception as e:
            logger.warning(f"Content cleaning error: {e}")
            # Return a safe fallback
            return str(content).encode('ascii', 'ignore').decode('ascii')
    
    def send_email(self, to_email, subject, content, content_type='html'):
        """Send a single email"""
        try:
            # Get current datetime for this function scope
            current_time = datetime.now()
            
            # Clean content to prevent encoding issues
            clean_subject = self.clean_content(subject)
            clean_content = self.clean_content(content)
            
            # Create message container with UTF-8 encoding
            message = MIMEMultipart("alternative")
            message["Subject"] = clean_subject
            message["From"] = self.sender_email
            message["To"] = to_email
            
            # Set charset to UTF-8
            message.set_charset('utf-8')
            
            # Convert content to HTML if it's plain text
            if content_type == 'html':
                html_content = clean_content
            else:
                # Convert plain text to HTML with Break-even branding
                # Escape HTML entities and handle line breaks
                escaped_content = html.escape(clean_content).replace('\n', '<br>')
                
                html_content = f"""
                <html>
                  <head>
                    <meta charset="UTF-8">
                  </head>
                  <body>
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                            <h2>ROCKET Break-Even Platform</h2>
                            <p>AI-Generated Email Campaign</p>
                        </div>
                        <div style="padding: 20px; background: #f9f9f9; border-radius: 0 0 10px 10px;">
                            <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                                {escaped_content}
                            </div>
                            <div style="text-align: center; color: #666; font-size: 12px;">
                                <p>This email was generated and sent via Break-Even AI Tools</p>
                                <p>Generated on: {current_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                            </div>
                        </div>
                    </div>
                  </body>
                </html>
                """
            
            # Create HTML part with UTF-8 encoding
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                
                text = message.as_string()
                server.sendmail(self.sender_email, to_email, text)
                
                logger.info(f"✅ Email sent successfully to {to_email}")
                return {
                    'success': True,
                    'message': f'Email sent to {to_email}',
                    'sent_at': current_time.isoformat(),
                    'message_id': f'break-even-{int(current_time.timestamp())}'
                }
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Failed to send email to {to_email}: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'failed_at': datetime.now().isoformat()
            }
    
    def send_bulk_emails(self, recipients, subject, content, content_type='html'):
        """Send emails to multiple recipients"""
        results = {
            'total_recipients': len(recipients),
            'successful_sends': [],
            'failed_sends': [],
            'summary': {}
        }
        
        logger.info(f"📧 Starting bulk email send to {len(recipients)} recipients")
        
        for i, recipient in enumerate(recipients):
            logger.info(f"📧 Sending email {i+1}/{len(recipients)} to {recipient}")
            result = self.send_email(recipient, subject, content, content_type)
            
            if result['success']:
                results['successful_sends'].append({
                    'email': recipient,
                    'status': 'sent',
                    'sent_at': result['sent_at'],
                    'message_id': result['message_id']
                })
                logger.info(f"✅ Email {i+1} sent successfully to {recipient}")
            else:
                results['failed_sends'].append({
                    'email': recipient,
                    'error': result['error'],
                    'failed_at': result['failed_at']
                })
                logger.error(f"❌ Email {i+1} failed to {recipient}: {result['error']}")
        
        # Calculate summary
        success_count = len(results['successful_sends'])
        fail_count = len(results['failed_sends'])
        
        results['summary'] = {
            'successful_sends': success_count,
            'failed_sends': fail_count,
            'success_rate': f"{(success_count / len(recipients)) * 100:.1f}%" if recipients else "0%"
        }
        
        logger.info(f"📊 Bulk email complete: {success_count}/{len(recipients)} successful ({results['summary']['success_rate']})")
        
        return results
    
    def send_test_email(self, recipient_email):
        """Send a test email to verify functionality"""
        current_time = datetime.now()
        
        test_content = f"""
        Hello from Break-Even AI Tools! ROCKET
        
        This is a test email to verify that our email service is working correctly.
        
        Recipient: {recipient_email}
        Timestamp: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
        
        If you received this email, it means our AI-generated email system is functioning properly!
        
        Features working:
        CHECK AI Content Generation
        CHECK Real Email Delivery
        CHECK SMTP Integration
        CHECK Database Logging
        
        Thank you for testing the Break-Even platform!
        
        Best regards,
        The Break-Even Team
        """
        
        return self.send_email(
            to_email=recipient_email,
            subject='ROCKET Break-Even AI Tools - Test Email',
            content=test_content,
            content_type='text'
        )
    
    def test_connection(self):
        """Test SMTP connection"""
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                logger.info(f"✅ Email service connection successful for {self.sender_email}")
                return {
                    'success': True,
                    'message': 'SMTP connection successful',
                    'sender_email': self.sender_email,
                    'smtp_server': self.smtp_server
                }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Email service connection failed: {error_msg}")
            
            # Provide helpful error messages
            help_msg = ""
            if "authentication failed" in error_msg.lower():
                help_msg = "Check your Gmail email and app password. Make sure 2FA is enabled and you're using an App Password."
            elif "connection" in error_msg.lower():
                help_msg = "Check your internet connection and firewall settings."
            
            return {
                'success': False,
                'error': error_msg,
                'help': help_msg,
                'sender_email': self.sender_email,
                'smtp_server': self.smtp_server
            }

    def send_consultation_confirmation(self, booking_data, business_info):
        """Send consultation booking confirmation email to client"""
        client_email = booking_data['client_info']['email']
        client_name = f"{booking_data['client_info']['first_name']} {booking_data['client_info']['last_name']}"
        
        subject = f"Consultation Confirmed - {business_info.get('name', 'Law Office')}"
        
        html_content = f"""
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1>Consultation Confirmed</h1>
                <p>{business_info.get('name', 'Law Office')}</p>
            </div>
            
            <div style="padding: 20px; background: #f8fafc;">
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2>Dear {client_name},</h2>
                    <p>Thank you for scheduling a consultation with our legal team. We have received your request and will contact you within 24 hours to confirm your appointment.</p>
                    
                    <h3>Consultation Details:</h3>
                    <ul>
                        <li><strong>Practice Area:</strong> {booking_data['consultation_details']['practice_area']}</li>
                        <li><strong>Preferred Date:</strong> {booking_data['consultation_details'].get('preferred_date', 'To be confirmed')}</li>
                        <li><strong>Preferred Time:</strong> {booking_data['consultation_details'].get('preferred_time', 'To be confirmed')}</li>
                        <li><strong>Case Type:</strong> {booking_data['consultation_details'].get('urgency_level', 'Standard')}</li>
                    </ul>
                    
                    <h3>What to Prepare:</h3>
                    <ul>
                        <li>Any relevant documents related to your case</li>
                        <li>List of questions you'd like to discuss</li>
                        <li>Timeline of events (if applicable)</li>
                        <li>Any previous legal correspondence</li>
                    </ul>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>Contact Information:</h3>
                    <p><strong>Phone:</strong> {business_info.get('phone', 'Contact via email')}</p>
                    <p><strong>Email:</strong> {business_info.get('email', 'N/A')}</p>
                    <p><strong>Address:</strong> {business_info.get('address', 'N/A')}</p>
                </div>
            </div>
            
            <div style="background: #374151; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px;">
                <p>This is an automated message from {business_info.get('name', 'Law Office')}.</p>
                <p>If you need to reschedule or have questions, please contact us directly.</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(client_email, subject, html_content, 'html')

    def send_measurement_confirmation(self, booking_data, business_info):
        """Send measurement appointment confirmation email to customer"""
        customer_email = booking_data['customer_info']['email']
        customer_name = f"{booking_data['customer_info']['first_name']} {booking_data['customer_info']['last_name']}"
        
        subject = f"Measurement Appointment Confirmed - {business_info.get('name', 'Tailor Shop')}"
        
        html_content = f"""
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background: linear-gradient(135deg, #8b4513 0%, #d2691e 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1>Measurement Appointment Confirmed</h1>
                <p>{business_info.get('name', 'Tailor Shop')}</p>
            </div>
            
            <div style="padding: 20px; background: #f8fafc;">
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2>Dear {customer_name},</h2>
                    <p>Thank you for booking a measurement session with our expert tailors. We will contact you within 24 hours to confirm your appointment time.</p>
                    
                    <h3>Appointment Details:</h3>
                    <ul>
                        <li><strong>Service:</strong> {booking_data['booking_details']['service_type']}</li>
                        <li><strong>Preferred Date:</strong> {booking_data['booking_details'].get('preferred_date', 'To be confirmed')}</li>
                        <li><strong>Preferred Time:</strong> {booking_data['booking_details'].get('preferred_time', 'To be confirmed')}</li>
                        <li><strong>Duration:</strong> 30-45 minutes</li>
                    </ul>
                    
                    <h3>What to Expect:</h3>
                    <ul>
                        <li>Professional measurements by experienced tailors</li>
                        <li>Posture analysis for perfect fit</li>
                        <li>Fabric consultation and recommendations</li>
                        <li>Style advice and design suggestions</li>
                        <li>Digital measurement card for future reference</li>
                    </ul>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>Shop Information:</h3>
                    <p><strong>Phone:</strong> {business_info.get('phone', 'Contact via email')}</p>
                    <p><strong>Email:</strong> {business_info.get('email', 'N/A')}</p>
                    <p><strong>Address:</strong> {business_info.get('address', 'N/A')}</p>
                </div>
            </div>
            
            <div style="background: #374151; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px;">
                <p>This is an automated message from {business_info.get('name', 'Tailor Shop')}.</p>
                <p>If you need to reschedule or have questions, please contact us directly.</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(customer_email, subject, html_content, 'html')

    def send_order_inquiry_confirmation(self, inquiry_data, business_info):
        """Send order inquiry confirmation email to customer"""
        customer_email = inquiry_data['customer_info']['email']
        customer_name = inquiry_data['customer_info']['name']
        
        subject = f"Order Inquiry Received - {business_info.get('name', 'Business')}"
        
        html_content = f"""
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background: linear-gradient(135deg, #8b4513 0%, #d2691e 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1>Order Inquiry Received</h1>
                <p>{business_info.get('name', 'Business')}</p>
            </div>
            
            <div style="padding: 20px; background: #f8fafc;">
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2>Dear {customer_name},</h2>
                    <p>Thank you for your order inquiry. We have received your request and our team will review it carefully. You can expect to receive a detailed quote within 24-48 hours.</p>
                    
                    <h3>Your Inquiry Details:</h3>
                    <ul>
                        <li><strong>Service:</strong> {inquiry_data['order_details']['service_type']}</li>
                        <li><strong>Description:</strong> {inquiry_data['order_details'].get('description', 'Custom work as discussed')}</li>
                        <li><strong>Timeline:</strong> {inquiry_data['order_details'].get('timeline', 'Standard')}</li>
                    </ul>
                    
                    <h3>Next Steps:</h3>
                    <ol>
                        <li>Our team will review your requirements</li>
                        <li>We'll prepare a detailed quote with pricing and timeline</li>
                        <li>You'll receive the quote via email within 24-48 hours</li>
                        <li>Once approved, we'll schedule your measurement session</li>
                        <li>Production begins after measurements and deposit</li>
                    </ol>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>Contact Us:</h3>
                    <p>If you have additional questions or want to discuss your project further:</p>
                    <p><strong>Phone:</strong> {business_info.get('phone', 'Contact via email')}</p>
                    <p><strong>Email:</strong> {business_info.get('email', 'N/A')}</p>
                </div>
            </div>
            
            <div style="background: #374151; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px;">
                <p>Thank you for choosing {business_info.get('name', 'us')} for your custom tailoring needs.</p>
                <p>We look forward to creating something perfect for you!</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(customer_email, subject, html_content, 'html')

    def send_business_notification(self, business_email, notification_type, data):
        """Send notification email to business owner"""
        subject_map = {
            'new_consultation': 'New Consultation Request',
            'new_measurement_booking': 'New Measurement Appointment',
            'new_order_inquiry': 'New Order Inquiry',
            'new_contact': 'New Contact Message'
        }
        
        subject = f"{subject_map.get(notification_type, 'New Notification')} - Break-Even Platform"
        
        html_content = f"""
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background: #1f2937; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1>Break-Even Platform</h1>
                <p>New Activity on Your Mini-Website</p>
            </div>
            
            <div style="padding: 20px;">
                <div style="background: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #3b82f6;">
                    <h2>{subject_map.get(notification_type, 'New Notification')}</h2>
                    <p>You have received a new {notification_type.replace('_', ' ')} through your mini-website.</p>
                    
                    <p><strong>Please log in to your dashboard to view details and respond to the customer.</strong></p>
                    
                    <a href="http://localhost:3001/dashboard" style="background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">View Dashboard</a>
                </div>
                
                <p>This notification was sent automatically by the Break-Even platform when a customer interacted with your mini-website.</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(business_email, subject, html_content, 'html')
    
    # New methods for booking and order emails
    
    def send_booking_request_confirmation(self, booking, business):
        """Send booking request confirmation to customer"""
        customer_email = booking.customer_email
        customer_name = booking.customer_name
        business_name = business.get('website_name', 'Our Business')
        
        subject = f"Booking Request Received - {business_name}"
        
        html_content = f"""
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1>Booking Request Received</h1>
                <p>{business_name}</p>
            </div>
            
            <div style="padding: 20px; background: #f8fafc;">
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2>Dear {customer_name},</h2>
                    <p>Thank you for your booking request. We have received your information and will contact you within 24 hours to confirm your appointment.</p>
                    
                    <h3>Booking Details:</h3>
                    <ul>
                        <li><strong>Service:</strong> {booking.service_type}</li>
                        <li><strong>Attorney:</strong> {booking.attorney_name}</li>
                        <li><strong>Requested Date:</strong> {booking.date.strftime('%B %d, %Y')}</li>
                        <li><strong>Requested Time:</strong> {booking.time}</li>
                        <li><strong>Status:</strong> Pending Confirmation</li>
                    </ul>
                    
                    {f'<p><strong>Your Notes:</strong> {booking.notes}</p>' if booking.notes else ''}
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>Contact Information:</h3>
                    <p><strong>Phone:</strong> {business.get('contact_info', {}).get('phone', 'N/A')}</p>
                    <p><strong>Email:</strong> {business.get('contact_info', {}).get('email', 'N/A')}</p>
                </div>
            </div>
            
            <div style="background: #374151; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px;">
                <p>This is an automated message from {business_name}.</p>
                <p>We will contact you soon to confirm your appointment.</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(customer_email, subject, html_content, 'html')
    
    def send_booking_confirmation(self, booking, business):
        """Send booking confirmation to customer"""
        customer_email = booking.customer_email
        customer_name = booking.customer_name
        business_name = business.get('website_name', 'Our Business')
        
        subject = f"Appointment Confirmed - {business_name}"
        
        html_content = f"""
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1>CHECK Appointment Confirmed!</h1>
                <p>{business_name}</p>
            </div>
            
            <div style="padding: 20px; background: #f8fafc;">
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2>Dear {customer_name},</h2>
                    <p>Great news! Your appointment has been confirmed.</p>
                    
                    <h3>Confirmed Appointment Details:</h3>
                    <ul>
                        <li><strong>Service:</strong> {booking.service_type}</li>
                        <li><strong>Attorney:</strong> {booking.attorney_name}</li>
                        <li><strong>Date:</strong> {booking.date.strftime('%B %d, %Y')}</li>
                        <li><strong>Time:</strong> {booking.time}</li>
                        <li><strong>Status:</strong> CONFIRMED</li>
                    </ul>
                    
                    <h3>What to Bring:</h3>
                    <ul>
                        <li>Valid ID</li>
                        <li>Any relevant documents</li>
                        <li>List of questions</li>
                    </ul>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>Contact Information:</h3>
                    <p><strong>Phone:</strong> {business.get('contact_info', {}).get('phone', 'N/A')}</p>
                    <p><strong>Email:</strong> {business.get('contact_info', {}).get('email', 'N/A')}</p>
                    <p><strong>Address:</strong> {business.get('area', 'N/A')}</p>
                </div>
            </div>
            
            <div style="background: #374151; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px;">
                <p>We look forward to seeing you!</p>
                <p>If you need to reschedule, please contact us at least 24 hours in advance.</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(customer_email, subject, html_content, 'html')
    
    def send_booking_cancellation(self, booking, business):
        """Send booking cancellation notification"""
        customer_email = booking.customer_email
        customer_name = booking.customer_name
        business_name = business.get('website_name', 'Our Business')
        
        subject = f"Appointment Cancelled - {business_name}"
        
        html_content = f"""
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background: #dc2626; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1>Appointment Cancelled</h1>
                <p>{business_name}</p>
            </div>
            
            <div style="padding: 20px; background: #f8fafc;">
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2>Dear {customer_name},</h2>
                    <p>Your appointment has been cancelled.</p>
                    
                    <h3>Cancelled Appointment:</h3>
                    <ul>
                        <li><strong>Service:</strong> {booking.service_type}</li>
                        <li><strong>Attorney:</strong> {booking.attorney_name}</li>
                        <li><strong>Date:</strong> {booking.date.strftime('%B %d, %Y')}</li>
                        <li><strong>Time:</strong> {booking.time}</li>
                    </ul>
                    
                    {f'<p><strong>Reason:</strong> {booking.cancellation_reason}</p>' if booking.cancellation_reason else ''}
                    
                    <p>If you would like to reschedule, please contact us or book a new appointment.</p>
                </div>
            </div>
            
            <div style="background: #374151; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px;">
                <p>Contact us: {business.get('contact_info', {}).get('phone', 'N/A')}</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(customer_email, subject, html_content, 'html')
    
    def send_new_booking_notification(self, booking, business, owner):
        """Send new booking notification to business owner"""
        owner_email = owner.get('email')
        business_name = business.get('website_name', 'Your Business')
        
        subject = f"New Booking Request - {business_name}"
        
        html_content = f"""
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background: #1f2937; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1>ROCKET New Booking Request!</h1>
                <p>{business_name}</p>
            </div>
            
            <div style="padding: 20px; background: #f8fafc;">
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2>You have a new booking request!</h2>
                    
                    <h3>Customer Information:</h3>
                    <ul>
                        <li><strong>Name:</strong> {booking.customer_name}</li>
                        <li><strong>Email:</strong> {booking.customer_email}</li>
                        <li><strong>Phone:</strong> {booking.customer_phone}</li>
                    </ul>
                    
                    <h3>Booking Details:</h3>
                    <ul>
                        <li><strong>Service:</strong> {booking.service_type}</li>
                        <li><strong>Attorney:</strong> {booking.attorney_name}</li>
                        <li><strong>Date:</strong> {booking.date.strftime('%B %d, %Y')}</li>
                        <li><strong>Time:</strong> {booking.time}</li>
                    </ul>
                    
                    {f'<p><strong>Customer Notes:</strong> {booking.notes}</p>' if booking.notes else ''}
                    
                    <a href="http://localhost:3001/bookings" style="background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin-top: 20px;">View in Dashboard</a>
                </div>
            </div>
            
            <div style="background: #374151; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px;">
                <p>Log in to your dashboard to confirm or manage this booking.</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(owner_email, subject, html_content, 'html')
    
    def send_order_confirmation(self, order, business):
        """Send order confirmation to customer"""
        customer_email = order.customer_email
        customer_name = order.customer_name
        business_name = business.get('website_name', 'Our Business')
        
        items_html = ''.join([f"<li>{item['product_name']} x {item['quantity']} - ${item['price']}</li>" 
                              for item in order.items])
        
        subject = f"Order Confirmed - {business_name}"
        
        html_content = f"""
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background: linear-gradient(135deg, #8b4513 0%, #d2691e 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1>CHECK Order Confirmed!</h1>
                <p>{business_name}</p>
            </div>
            
            <div style="padding: 20px; background: #f8fafc;">
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2>Dear {customer_name},</h2>
                    <p>Thank you for your order! We have received your request and will begin processing it shortly.</p>
                    
                    <h3>Order Details:</h3>
                    <ul>{items_html}</ul>
                    
                    <p><strong>Total Amount:</strong> ${order.total_amount}</p>
                    <p><strong>Status:</strong> {order.status.upper()}</p>
                    
                    {f'<p><strong>Delivery Address:</strong> {order.delivery_address}</p>' if order.delivery_address else ''}
                    {f'<p><strong>Notes:</strong> {order.notes}</p>' if order.notes else ''}
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>What's Next?</h3>
                    <ol>
                        <li>We'll review your order details</li>
                        <li>Contact you for measurements (if needed)</li>
                        <li>Begin production</li>
                        <li>Keep you updated on progress</li>
                        <li>Deliver your custom order</li>
                    </ol>
                </div>
            </div>
            
            <div style="background: #374151; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px;">
                <p>Contact us: {business.get('contact_info', {}).get('phone', 'N/A')}</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(customer_email, subject, html_content, 'html')
    
    def send_order_status_update(self, order, business, new_status):
        """Send order status update to customer"""
        customer_email = order.customer_email
        customer_name = order.customer_name
        business_name = business.get('website_name', 'Our Business')
        
        status_messages = {
            'processing': 'Your order is now being processed!',
            'completed': 'Your order is ready!',
            'cancelled': 'Your order has been cancelled.'
        }
        
        subject = f"Order Update - {business_name}"
        
        html_content = f"""
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background: linear-gradient(135deg, #8b4513 0%, #d2691e 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1>Order Status Update</h1>
                <p>{business_name}</p>
            </div>
            
            <div style="padding: 20px; background: #f8fafc;">
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2>Dear {customer_name},</h2>
                    <p>{status_messages.get(new_status, 'Your order status has been updated.')}</p>
                    
                    <p><strong>New Status:</strong> {new_status.upper()}</p>
                    
                    {f'<p><strong>Tracking Number:</strong> {order.tracking_number}</p>' if order.tracking_number else ''}
                </div>
            </div>
            
            <div style="background: #374151; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px;">
                <p>Contact us: {business.get('contact_info', {}).get('phone', 'N/A')}</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(customer_email, subject, html_content, 'html')

# Initialize global email service
email_service = None

def get_email_service():
    """Get or create email service instance"""
    global email_service
    if email_service is None:
        email_service = EmailService()
    return email_service