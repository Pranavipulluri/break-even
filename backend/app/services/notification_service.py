from flask_mail import Message
from app import mail, mongo, socketio
from datetime import datetime
from bson import ObjectId
import json

class NotificationService:
    def __init__(self):
        pass
    
    def send_email_notification(self, recipient_email, subject, template, **kwargs):
        """Send email notification"""
        try:
            msg = Message(
                subject=subject,
                recipients=[recipient_email],
                html=template.format(**kwargs),
                sender=mail.default_sender
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Email notification failed: {e}")
            return False
    
    def send_realtime_notification(self, user_id, notification_type, data):
        """Send real-time notification via WebSocket"""
        try:
            notification = {
                'type': notification_type,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Send to user's room
            socketio.emit(notification_type, notification, room=str(user_id))
            
            # Store notification in database
            self.store_notification(user_id, notification)
            
            return True
        except Exception as e:
            print(f"Real-time notification failed: {e}")
            return False
    
    def store_notification(self, user_id, notification):
        """Store notification in database"""
        try:
            notification_doc = {
                'user_id': ObjectId(user_id),
                'type': notification['type'],
                'data': notification['data'],
                'timestamp': datetime.utcnow(),
                'read': False
            }
            
            mongo.db.notifications.insert_one(notification_doc)
            
            # Keep only last 100 notifications per user
            notifications = list(mongo.db.notifications.find({
                'user_id': ObjectId(user_id)
            }).sort('timestamp', -1))
            
            if len(notifications) > 100:
                old_notifications = notifications[100:]
                old_ids = [n['_id'] for n in old_notifications]
                mongo.db.notifications.delete_many({'_id': {'$in': old_ids}})
            
        except Exception as e:
            print(f"Failed to store notification: {e}")
    
    def notify_new_message(self, user_id, message_data):
        """Notify business owner of new message"""
        # Real-time notification
        self.send_realtime_notification(
            user_id, 
            'new_message', 
            {
                'customer_name': message_data.get('customer_name'),
                'content_preview': message_data.get('content', '')[:100],
                'message_id': str(message_data.get('_id'))
            }
        )
        
        # Email notification (if enabled)
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if user and user.get('email_notifications', True):
            self.send_email_notification(
                user['email'],
                f"New message from {message_data.get('customer_name')}",
                """
                <h2>New Customer Message</h2>
                <p>Hello {business_name},</p>
                <p>You have received a new message from <strong>{customer_name}</strong>:</p>
                <blockquote style="border-left: 4px solid #3b82f6; padding-left: 16px; margin: 16px 0;">
                    {message_content}
                </blockquote>
                <p>Please log in to your Break-even dashboard to respond.</p>
                """,
                business_name=user.get('business_name', user['name']),
                customer_name=message_data.get('customer_name'),
                message_content=message_data.get('content', '')
            )
    
    def notify_new_customer(self, user_id, customer_data):
        """Notify business owner of new customer registration"""
        self.send_realtime_notification(
            user_id,
            'new_customer',
            {
                'customer_name': customer_data.get('name'),
                'customer_email': customer_data.get('email'),
                'registration_source': customer_data.get('registration_source')
            }
        )
    
    def notify_qr_scan(self, user_id, scan_data):
        """Notify business owner of QR code scan"""
        self.send_realtime_notification(
            user_id,
            'qr_scan',
            {
                'total_scans': scan_data.get('total_scans'),
                'scans_today': scan_data.get('scans_today')
            }
        )
    
    def notify_low_stock(self, user_id, product_data):
        """Notify business owner of low stock"""
        self.send_realtime_notification(
            user_id,
            'low_stock',
            {
                'product_name': product_data.get('name'),
                'current_stock': product_data.get('stock'),
                'product_id': str(product_data.get('_id'))
            }
        )
    
    def get_user_notifications(self, user_id, limit=50):
        """Get user's notifications"""
        try:
            notifications = list(mongo.db.notifications.find({
                'user_id': ObjectId(user_id)
            }).sort('timestamp', -1).limit(limit))
            
            # Convert ObjectId to string
            for notification in notifications:
                notification['_id'] = str(notification['_id'])
                notification['user_id'] = str(notification['user_id'])
            
            return notifications
        except Exception as e:
            print(f"Error fetching notifications: {e}")
            return []
    
    def mark_notifications_read(self, user_id, notification_ids=None):
        """Mark notifications as read"""
        try:
            query = {'user_id': ObjectId(user_id)}
            
            if notification_ids:
                query['_id'] = {'$in': [ObjectId(nid) for nid in notification_ids]}
            
            mongo.db.notifications.update_many(
                query,
                {'$set': {'read': True}}
            )
            
            return True
        except Exception as e:
            print(f"Error marking notifications as read: {e}")
            return False