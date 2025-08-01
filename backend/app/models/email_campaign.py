from datetime import datetime
from bson import ObjectId

class EmailCampaign:
    def __init__(self, business_owner_id, subject, content, target_customers=None):
        self.business_owner_id = ObjectId(business_owner_id)
        self.subject = subject
        self.content = content
        self.target_customers = target_customers or []
        self.status = 'draft'  # draft, sending, sent, failed
        self.created_at = datetime.utcnow()
        self.sent_at = None
        self.total_recipients = 0
        self.successful_sends = 0
        self.failed_sends = 0
        self.open_rate = 0.0
        self.click_rate = 0.0
        
    def to_dict(self):
        return {
            'business_owner_id': self.business_owner_id,
            'subject': self.subject,
            'content': self.content,
            'target_customers': self.target_customers,
            'status': self.status,
            'created_at': self.created_at,
            'sent_at': self.sent_at,
            'total_recipients': self.total_recipients,
            'successful_sends': self.successful_sends,
            'failed_sends': self.failed_sends,
            'open_rate': self.open_rate,
            'click_rate': self.click_rate
        }

class EmailLog:
    def __init__(self, campaign_id, customer_id, customer_email, status='sent'):
        self.campaign_id = ObjectId(campaign_id)
        self.customer_id = ObjectId(customer_id)
        self.customer_email = customer_email
        self.status = status  # sent, failed, opened, clicked
        self.sent_at = datetime.utcnow()
        self.opened_at = None
        self.clicked_at = None
        self.error_message = None
        
    def to_dict(self):
        return {
            'campaign_id': self.campaign_id,
            'customer_id': self.customer_id,
            'customer_email': self.customer_email,
            'status': self.status,
            'sent_at': self.sent_at,
            'opened_at': self.opened_at,
            'clicked_at': self.clicked_at,
            'error_message': self.error_message
        }