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
        self.sender_email = os.environ.get('GMAIL_EMAIL', 'pullurisonu798@gmail.com')
        self.sender_password = os.environ.get('GMAIL_APP_PASSWORD', 'nmpl zxcq aqle uoun')
        
        # Fallback credentials for testing (replace with your actual credentials)
        if self.sender_email == 'your-email@gmail.com':
            # You can set these for testing - REPLACE WITH YOUR ACTUAL CREDENTIALS
            self.sender_email = "pullurisonu798@gmail.com"  # Replace with your Gmail
            self.sender_password = "your-16-char-app-password"  # Replace with your App Password
    
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

# Initialize global email service
email_service = None

def get_email_service():
    """Get or create email service instance"""
    global email_service
    if email_service is None:
        email_service = EmailService()
    return email_service