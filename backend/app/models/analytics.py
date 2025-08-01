from datetime import datetime
from bson import ObjectId

class WebsiteAnalytics:
    def __init__(self, website_id, business_owner_id, visitor_ip, user_agent, page='/', referrer=None):
        self.website_id = website_id
        self.business_owner_id = ObjectId(business_owner_id)
        self.visitor_ip = visitor_ip
        self.user_agent = user_agent
        self.page = page
        self.referrer = referrer
        self.visited_at = datetime.utcnow()
        self.session_id = None
        self.country = None
        self.city = None
        
    def to_dict(self):
        return {
            'website_id': self.website_id,
            'business_owner_id': self.business_owner_id,
            'visitor_ip': self.visitor_ip,
            'user_agent': self.user_agent,
            'page': self.page,
            'referrer': self.referrer,
            'visited_at': self.visited_at,
            'session_id': self.session_id,
            'country': self.country,
            'city': self.city
        }

class QRAnalytics:
    def __init__(self, user_id, website_url):
        self.user_id = ObjectId(user_id)
        self.website_url = website_url
        self.total_scans = 0
        self.scans_today = 0
        self.last_scan = None
        self.last_scan_date = None
        self.created_at = datetime.utcnow()
        self.scan_sources = {}  # Track where scans come from
        
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'website_url': self.website_url,
            'total_scans': self.total_scans,
            'scans_today': self.scans_today,
            'last_scan': self.last_scan,
            'last_scan_date': self.last_scan_date,
            'created_at': self.created_at,
            'scan_sources': self.scan_sources
        }

class BusinessMetrics:
    def __init__(self, user_id):
        self.user_id = ObjectId(user_id)
        self.total_customers = 0
        self.total_messages = 0
        self.total_products = 0
        self.total_qr_scans = 0
        self.total_website_visits = 0
        self.conversion_rate = 0.0
        self.customer_satisfaction = 0.0
        self.updated_at = datetime.utcnow()
        
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'total_customers': self.total_customers,
            'total_messages': self.total_messages,
            'total_products': self.total_products,
            'total_qr_scans': self.total_qr_scans,
            'total_website_visits': self.total_website_visits,
            'conversion_rate': self.conversion_rate,
            'customer_satisfaction': self.customer_satisfaction,
            'updated_at': self.updated_at
        }


#### app/models/email_campaign.py
python
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

