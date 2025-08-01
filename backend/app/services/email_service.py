from flask_mail import Message
from app import mail, mongo
from flask import current_app, render_template_string
from datetime import datetime
from bson import ObjectId
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def _init_(self):
        self.sender_email = current_app.config.get('MAIL_USERNAME')
        self.sender_password = current_app.config.get('MAIL_PASSWORD')
    
    def send_new_message_notification(self, recipient_email, recipient_name, customer_name, message_content):
        """Send notification to business owner about new message"""
        try:
            subject = f"New message from {customer_name}"
            
            html_body = f"""
            <html>
                <body>
                    <h2>New Customer Message</h2>
                    <p>Hello {recipient_name},</p>
                    <p>You have received a new message from a customer on your website:</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>From:</strong> {customer_name}</p>
                        <p><strong>Message:</strong></p>
                        <p>{message_content}</p>
                    </div>
                    
                    <p>Please log in to your Break-even dashboard to respond to this message.</p>
                    
                    <p>Best regards,<br>Break-even Team</p>
                </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[recipient_email],
                html=html_body,
                sender=self.sender_email
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Error sending email notification: {e}")
            return False
    
    def send_message_reply(self, customer_email, customer_name, business_name, business_owner_name, reply_content):
        """Send reply to customer"""
        try:
            subject = f"Reply from {business_name}"
            
            html_body = f"""
            <html>
                <body>
                    <h2>{business_name} - Message Reply</h2>
                    <p>Hello {customer_name},</p>
                    <p>Thank you for your message. Here's our response:</p>
                    
                    <div style="background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #2196F3;">
                        <p>{reply_content}</p>
                    </div>
                    
                    <p>If you have any further questions, please don't hesitate to contact us through our website.</p>
                    
                    <p>Best regards,<br>{business_owner_name}<br>{business_name}</p>
                </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[customer_email],
                html=html_body,
                sender=self.sender_email
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Error sending reply email: {e}")
            return False
    
    def send_bulk_email_to_customers(self, business_owner_id, subject, content, target_customers=None):
        """Send bulk email to customers for marketing/updates"""
        try:
            # Get customers
            if target_customers:
                customers = list(mongo.db.child_customers.find({
                    'business_owner_id': ObjectId(business_owner_id),
                    '_id': {'$in': [ObjectId(cid) for cid in target_customers]}
                }))
            else:
                customers = list(mongo.db.child_customers.find({
                    'business_owner_id': ObjectId(business_owner_id)
                }))
            
            # Get business owner info
            business_owner = mongo.db.users.find_one({'_id': ObjectId(business_owner_id)})
            if not business_owner:
                return False
            
            success_count = 0
            total_count = len(customers)
            
            for customer in customers:
                try:
                    html_body = f"""
                    <html>
                        <body>
                            <h2>{business_owner.get('business_name', 'Business Update')}</h2>
                            <p>Hello {customer['name']},</p>
                            
                            <div style="margin: 20px 0;">
                                {content}
                            </div>
                            
                            <p>Thank you for being our valued customer!</p>
                            
                            <p>Best regards,<br>{business_owner['name']}<br>{business_owner.get('business_name', '')}</p>
                            
                            <hr style="margin-top: 30px;">
                            <p style="font-size: 12px; color: #666;">
                                You received this email because you are a registered customer. 
                                If you no longer wish to receive these emails, please contact us.
                            </p>
                        </body>
                    </html>
                    """
                    
                    msg = Message(
                        subject=subject,
                        recipients=[customer['email']],
                        html=html_body,
                        sender=self.sender_email
                    )
                    
                    mail.send(msg)
                    success_count += 1
                    
                    # Log email campaign
                    mongo.db.email_campaigns.insert_one({
                        'business_owner_id': ObjectId(business_owner_id),
                        'customer_id': customer['_id'],
                        'customer_email': customer['email'],
                        'subject': subject,
                        'sent_at': datetime.utcnow(),
                        'status': 'sent'
                    })
                    
                except Exception as email_error:
                    print(f"Failed to send email to {customer['email']}: {email_error}")
                    
                    # Log failed email
                    mongo.db.email_campaigns.insert_one({
                        'business_owner_id': ObjectId(business_owner_id),
                        'customer_id': customer['_id'],
                        'customer_email': customer['email'],
                        'subject': subject,
                        'sent_at': datetime.utcnow(),
                        'status': 'failed',
                        'error': str(email_error)
                    })
            
            return {
                'success': True,
                'sent': success_count,
                'total': total_count,
                'failed': total_count - success_count
            }
            
        except Exception as e:
            print(f"Error in bulk email sending: {e}")
            return False
    
    def send_customer_welcome_email(self, customer_email, customer_name, business_name, business_owner_name):
        """Send welcome email to new customers"""
        try:
            subject = f"Welcome to {business_name}!"
            
            html_body = f"""
            <html>
                <body>
                    <h2>Welcome to {business_name}!</h2>
                    <p>Hello {customer_name},</p>
                    <p>Thank you for registering with us! We're excited to have you as our customer.</p>
                    
                    <div style="background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>What's next?</strong></p>
                        <ul>
                            <li>Browse our products and services</li>
                            <li>Contact us if you have any questions</li>
                            <li>Stay tuned for updates and special offers</li>
                        </ul>
                    </div>
                    
                    <p>If you have any questions, feel free to reach out to us anytime.</p>
                    
                    <p>Best regards,<br>{business_owner_name}<br>{business_name}</p>
                </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[customer_email],
                html=html_body,
                sender=self.sender_email
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Error sending welcome email: {e}")
            return False

