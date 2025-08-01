
from datetime import datetime
from bson import ObjectId

class ChildWebsite:
    def __init__(self, owner_id, website_name, business_type, color_theme, 
                 contact_info, area, description='', logo_url=None, 
                 custom_css=None, custom_domain=None):
        self.owner_id = ObjectId(owner_id)
        self.website_name = website_name
        self.business_type = business_type
        self.color_theme = color_theme
        self.contact_info = contact_info
        self.area = area
        self.description = description
        self.logo_url = logo_url
        self.custom_css = custom_css
        self.custom_domain = custom_domain
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.generated_content = None
        self.seo_settings = {
            'title': website_name,
            'description': description,
            'keywords': []
        }
        
    def to_dict(self):
        return {
            'owner_id': self.owner_id,
            'website_name': self.website_name,
            'business_type': self.business_type,
            'color_theme': self.color_theme,
            'contact_info': self.contact_info,
            'area': self.area,
            'description': self.description,
            'logo_url': self.logo_url,
            'custom_css': self.custom_css,
            'custom_domain': self.custom_domain,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'generated_content': self.generated_content,
            'seo_settings': self.seo_settings
        }
    
    @staticmethod
    def from_dict(data):
        website = ChildWebsite(
            owner_id=data['owner_id'],
            website_name=data['website_name'],
            business_type=data['business_type'],
            color_theme=data['color_theme'],
            contact_info=data['contact_info'],
            area=data['area'],
            description=data.get('description', ''),
            logo_url=data.get('logo_url'),
            custom_css=data.get('custom_css'),
            custom_domain=data.get('custom_domain')
        )
        website.is_active = data.get('is_active', True)
        website.created_at = data.get('created_at', datetime.utcnow())
        website.updated_at = data.get('updated_at', datetime.utcnow())
        website.generated_content = data.get('generated_content')
        website.seo_settings = data.get('seo_settings', {
            'title': data['website_name'],
            'description': data.get('description', ''),
            'keywords': []
        })
        return website


