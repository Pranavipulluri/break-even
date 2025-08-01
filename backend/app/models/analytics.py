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
