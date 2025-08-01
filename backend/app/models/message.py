
from datetime import datetime
from bson import ObjectId

class Message:
    def __init__(self, recipient_id, content, customer_name, customer_email, 
                 customer_phone=None, website_id=None, message_type='inquiry'):
        self.recipient_id = ObjectId(recipient_id)
        self.content = content
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.customer_phone = customer_phone
        self.website_id = website_id
        self.message_type = message_type
        self.created_at = datetime.utcnow()
        self.is_read = False
        self.reply = None
        self.replied_at = None
        self.status = 'new'  # new, read, replied
        
    def to_dict(self):
        return {
            'recipient_id': self.recipient_id,
            'content': self.content,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'website_id': self.website_id,
            'message_type': self.message_type,
            'created_at': self.created_at,
            'is_read': self.is_read,
            'reply': self.reply,
            'replied_at': self.replied_at,
            'status': self.status
        }
    
    @staticmethod
    def from_dict(data):
        message = Message(
            recipient_id=data['recipient_id'],
            content=data['content'],
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data.get('customer_phone'),
            website_id=data.get('website_id'),
            message_type=data.get('message_type', 'inquiry')
        )
        message.created_at = data.get('created_at', datetime.utcnow())
        message.is_read = data.get('is_read', False)
        message.reply = data.get('reply')
        message.replied_at = data.get('replied_at')
        message.status = data.get('status', 'new')
        return message

