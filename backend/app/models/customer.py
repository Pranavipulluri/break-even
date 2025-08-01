from datetime import datetime
from bson import ObjectId

class ChildCustomer:
    def __init__(self, business_owner_id, name, email, phone=None, location=None, 
                 website_id=None, registration_source='website'):
        self.business_owner_id = ObjectId(business_owner_id)
        self.name = name
        self.email = email
        self.phone = phone
        self.location = location
        self.website_id = website_id
        self.registration_source = registration_source
        self.created_at = datetime.utcnow()
        self.last_interaction = datetime.utcnow()
        self.is_subscribed = True
        self.tags = []
        self.notes = ''
        
    def to_dict(self):
        return {
            'business_owner_id': self.business_owner_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'website_id': self.website_id,
            'registration_source': self.registration_source,
            'created_at': self.created_at,
            'last_interaction': self.last_interaction,
            'is_subscribed': self.is_subscribed,
            'tags': self.tags,
            'notes': self.notes
        }
    
    @staticmethod
    def from_dict(data):
        customer = ChildCustomer(
            business_owner_id=data['business_owner_id'],
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            location=data.get('location'),
            website_id=data.get('website_id'),
            registration_source=data.get('registration_source', 'website')
        )
        customer.created_at = data.get('created_at', datetime.utcnow())
        customer.last_interaction = data.get('last_interaction', datetime.utcnow())
        customer.is_subscribed = data.get('is_subscribed', True)
        customer.tags = data.get('tags', [])
        customer.notes = data.get('notes', '')
        return customer


