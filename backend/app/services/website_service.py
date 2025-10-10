from flask import current_app
import json
import random
from datetime import datetime
from app.services.ai_service import AIService


class WebsiteService:
    def __init__(self):
        self.ai_service = AIService()
    
    def generate_website_content(self, business_type, business_name, description='', area=''):
        """Generate website content using AI service"""
        try:
            # Create context for AI content generation
            business_context = f"""
            Business Name: {business_name}
            Business Type: {business_type}
            Location: {area}
            Description: {description}
            """
            
            # Generate different sections of content
            content = {
                'hero_section': self._generate_hero_section(business_name, business_type, description, area),
                'about_section': self._generate_about_section(business_name, business_type, description, area),
                'services_section': self._generate_services_section(business_type, business_context),
                'contact_section': self._generate_contact_section(business_name, area),
                'meta_data': self._generate_meta_data(business_name, business_type, area),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return content
            
        except Exception as e:
            print(f"Error generating website content: {e}")
            return self._get_fallback_content(business_name, business_type, area)
    
    def _generate_hero_section(self, business_name, business_type, description, area):
        """Generate hero section content"""
        prompt = f"Create a compelling hero section for {business_name}, a {business_type} business in {area}. {description}"
        
        hero_content = self.ai_service.generate_content('website_content', prompt)
        
        return {
            'headline': f"Welcome to {business_name}",
            'subheadline': hero_content or f"Your trusted {business_type} in {area}",
            'call_to_action': "Contact Us Today",
            'background_style': self._get_background_style(business_type)
        }
    
    def _generate_about_section(self, business_name, business_type, description, area):
        """Generate about section content"""
        prompt = f"Write an engaging about section for {business_name}, a {business_type} business in {area}. Highlight what makes them special. {description}"
        
        about_content = self.ai_service.generate_content('website_content', prompt)
        
        return {
            'title': f"About {business_name}",
            'content': about_content or f"At {business_name}, we are committed to providing excellent {business_type} services to our community in {area}. Our dedication to quality and customer satisfaction sets us apart.",
            'highlights': self._get_business_highlights(business_type)
        }
    
    def _generate_services_section(self, business_type, business_context):
        """Generate services section content"""
        prompt = f"List the main services offered by a {business_type} business. {business_context}"
        
        services_content = self.ai_service.generate_content('website_content', prompt)
        
        return {
            'title': "Our Services",
            'content': services_content or "We offer a comprehensive range of services to meet your needs.",
            'services': self._get_default_services(business_type)
        }
    
    def _generate_contact_section(self, business_name, area):
        """Generate contact section content"""
        return {
            'title': "Get In Touch",
            'content': f"Ready to experience what {business_name} has to offer? Contact us today!",
            'location': area,
            'call_to_action': "Contact Us Now"
        }
    
    def _generate_meta_data(self, business_name, business_type, area):
        """Generate meta data for SEO"""
        return {
            'title': f"{business_name} - {business_type} in {area}",
            'description': f"Visit {business_name} for quality {business_type} services in {area}. Professional service and customer satisfaction guaranteed.",
            'keywords': f"{business_name}, {business_type}, {area}, quality service, professional"
        }
    
    def _get_background_style(self, business_type):
        """Get appropriate background style for business type"""
        styles = {
            'restaurant': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'retail': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'beauty': 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
            'professional': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'health': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            'technology': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            'automotive': 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
            'education': 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)'
        }
        return styles.get(business_type.lower(), 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)')
    
    def _get_business_highlights(self, business_type):
        """Get business highlights based on type"""
        highlights = {
            'restaurant': ['Fresh Ingredients', 'Professional Chefs', 'Cozy Atmosphere', 'Excellent Service'],
            'retail': ['Quality Products', 'Competitive Prices', 'Wide Selection', 'Customer Support'],
            'beauty': ['Professional Stylists', 'Premium Products', 'Relaxing Environment', 'Latest Trends'],
            'professional': ['Expert Team', 'Proven Results', 'Client Focused', 'Reliable Service'],
            'health': ['Qualified Professionals', 'Modern Equipment', 'Personalized Care', 'Health Focused'],
            'technology': ['Cutting-edge Solutions', 'Expert Team', 'Innovation Driven', 'Reliable Support'],
            'automotive': ['Certified Technicians', 'Quality Parts', 'Fast Service', 'Fair Pricing'],
            'education': ['Experienced Teachers', 'Proven Methods', 'Student Success', 'Supportive Environment']
        }
        return highlights.get(business_type.lower(), ['Quality Service', 'Professional Team', 'Customer Satisfaction', 'Reliable Results'])
    
    def _get_default_services(self, business_type):
        """Get default services based on business type"""
        services = {
            'restaurant': [
                {'name': 'Dine-in', 'description': 'Enjoy our delicious meals in our comfortable restaurant'},
                {'name': 'Takeaway', 'description': 'Order your favorite dishes for pickup'},
                {'name': 'Catering', 'description': 'Professional catering for your special events'}
            ],
            'retail': [
                {'name': 'In-store Shopping', 'description': 'Browse our wide selection of quality products'},
                {'name': 'Personal Shopping', 'description': 'Get personalized assistance from our experts'},
                {'name': 'Product Consultation', 'description': 'Expert advice to help you make the right choice'}
            ],
            'beauty': [
                {'name': 'Hair Styling', 'description': 'Professional cuts, colors, and styling'},
                {'name': 'Skincare', 'description': 'Rejuvenating treatments for healthy skin'},
                {'name': 'Makeup', 'description': 'Professional makeup for any occasion'}
            ],
            'professional': [
                {'name': 'Consultation', 'description': 'Professional advice tailored to your needs'},
                {'name': 'Service Delivery', 'description': 'High-quality service execution'},
                {'name': 'Follow-up Support', 'description': 'Ongoing support to ensure satisfaction'}
            ]
        }
        return services.get(business_type.lower(), [
            {'name': 'Professional Service', 'description': 'High-quality service delivery'},
            {'name': 'Consultation', 'description': 'Expert advice and guidance'},
            {'name': 'Support', 'description': 'Ongoing customer support'}
        ])
    
    def _get_fallback_content(self, business_name, business_type, area):
        """Provide fallback content when AI generation fails"""
        return {
            'hero_section': {
                'headline': f"Welcome to {business_name}",
                'subheadline': f"Your trusted {business_type} in {area}",
                'call_to_action': "Contact Us Today",
                'background_style': self._get_background_style(business_type)
            },
            'about_section': {
                'title': f"About {business_name}",
                'content': f"Welcome to {business_name}, your premier {business_type} destination in {area}. We are committed to providing excellent service and ensuring customer satisfaction in everything we do.",
                'highlights': self._get_business_highlights(business_type)
            },
            'services_section': {
                'title': "Our Services",
                'content': "We offer a comprehensive range of professional services designed to meet your needs and exceed your expectations.",
                'services': self._get_default_services(business_type)
            },
            'contact_section': {
                'title': "Get In Touch",
                'content': f"Ready to experience what {business_name} has to offer? We'd love to hear from you!",
                'location': area,
                'call_to_action': "Contact Us Now"
            },
            'meta_data': {
                'title': f"{business_name} - {business_type} in {area}",
                'description': f"Visit {business_name} for quality {business_type} services in {area}. Professional service and customer satisfaction guaranteed.",
                'keywords': f"{business_name}, {business_type}, {area}, quality service, professional"
            },
            'generated_at': datetime.utcnow().isoformat(),
            'fallback': True
        }


class GeminiWebsiteService:
    """Enhanced website service using Gemini AI for more sophisticated content generation"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def generate_enhanced_website_content(self, business_data, user_context):
        """Generate enhanced website content with personalization"""
        try:
            # Create comprehensive prompt for Gemini
            prompt = self._create_enhanced_prompt(business_data, user_context)
            
            # Generate content using AI service
            enhanced_content = self.ai_service.generate_content('website_content', prompt, 
                                                              business_context=json.dumps(business_data))
            
            # Structure the content
            return self._structure_enhanced_content(enhanced_content, business_data)
            
        except Exception as e:
            print(f"Error generating enhanced content: {e}")
            # Fallback to basic website service
            basic_service = WebsiteService()
            return basic_service.generate_website_content(
                business_data['business_type'],
                business_data['website_name'],
                business_data.get('description', ''),
                business_data['area']
            )
    
    def _create_enhanced_prompt(self, business_data, user_context):
        """Create comprehensive prompt for enhanced content generation"""
        return f"""
        Create comprehensive, engaging website content for:
        
        Business: {business_data['website_name']}
        Type: {business_data['business_type']}
        Location: {business_data['area']}
        Description: {business_data.get('description', '')}
        
        User Context:
        - Experience Level: {user_context.get('user_experience', 'new')}
        - Location: {user_context.get('location', '')}
        - Previous Businesses: {user_context.get('previous_businesses', [])}
        
        Generate content that is:
        1. Locally relevant and appealing
        2. Professional yet approachable
        3. SEO-optimized with relevant keywords
        4. Engaging and conversion-focused
        5. Mobile-friendly and modern
        
        Include sections for hero, about, services, and contact information.
        Make it compelling and unique to this specific business.
        """
    
    def _structure_enhanced_content(self, content, business_data):
        """Structure the AI-generated content into website sections"""
        # If AI content generation worked, use it; otherwise fall back to template
        if content and len(content) > 100:
            return {
                'hero_section': {
                    'headline': f"Welcome to {business_data['website_name']}",
                    'subheadline': content[:200] + "..." if len(content) > 200 else content,
                    'call_to_action': "Get In Touch",
                    'enhanced': True
                },
                'about_section': {
                    'title': f"About {business_data['website_name']}",
                    'content': content,
                    'enhanced': True
                },
                'services_section': {
                    'title': "Our Services",
                    'content': f"Discover what {business_data['website_name']} can do for you.",
                    'enhanced': True
                },
                'contact_section': {
                    'title': "Contact Us",
                    'content': f"Ready to experience {business_data['website_name']}? Get in touch today!",
                    'location': business_data['area']
                },
                'generated_at': datetime.utcnow().isoformat(),
                'generation_method': 'gemini_enhanced'
            }
        else:
            # Fallback to basic content
            basic_service = WebsiteService()
            return basic_service.generate_website_content(
                business_data['business_type'],
                business_data['website_name'],
                business_data.get('description', ''),
                business_data['area']
            )


class WebsiteTrainingService:
    """Service for collecting training data and improving website generation"""
    
    def collect_user_feedback(self, website_id, feedback_data):
        """Collect user feedback for training purposes"""
        try:
            from app import mongo
            
            feedback_entry = {
                'website_id': website_id,
                'feedback_type': feedback_data.get('type', 'general'),
                'rating': feedback_data.get('rating', 0),
                'comments': feedback_data.get('comments', ''),
                'improvements': feedback_data.get('improvements', []),
                'collected_at': datetime.utcnow()
            }
            
            mongo.db.website_feedback.insert_one(feedback_entry)
            
            # Update training data performance score
            self._update_performance_score(website_id, feedback_data.get('rating', 0))
            
        except Exception as e:
            print(f"Error collecting feedback: {e}")
    
    def get_content_recommendations(self, business_type, area):
        """Get content recommendations based on successful patterns"""
        try:
            from app import mongo
            
            # Find successful websites of similar type in similar areas
            successful_websites = mongo.db.website_training_data.find({
                'business_type': business_type,
                'performance_score': {'$gte': 4.0},
                'area': {'$regex': area, '$options': 'i'}
            }).limit(5)
            
            recommendations = []
            for website in successful_websites:
                recommendations.append({
                    'content_pattern': website.get('generated_content', {}).get('hero_section', {}),
                    'performance_score': website.get('performance_score', 0),
                    'business_name': website.get('business_name', ''),
                    'area': website.get('area', '')
                })
            
            return recommendations
            
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
    
    def analyze_successful_patterns(self, business_type=None):
        """Analyze patterns from successful websites"""
        try:
            from app import mongo
            
            match_criteria = {'performance_score': {'$gte': 4.0}}
            if business_type:
                match_criteria['business_type'] = business_type
            
            patterns = mongo.db.website_training_data.aggregate([
                {'$match': match_criteria},
                {'$group': {
                    '_id': '$business_type',
                    'avg_score': {'$avg': '$performance_score'},
                    'common_features': {'$push': '$generated_content'},
                    'count': {'$sum': 1}
                }},
                {'$sort': {'avg_score': -1}}
            ])
            
            return list(patterns)
            
        except Exception as e:
            print(f"Error analyzing patterns: {e}")
            return []
    
    def _update_performance_score(self, website_id, rating):
        """Update performance score based on user feedback"""
        try:
            from app import mongo
            
            mongo.db.website_training_data.update_one(
                {'website_id': website_id},
                {
                    '$inc': {'feedback_count': 1},
                    '$push': {'ratings': rating},
                    '$set': {'last_feedback': datetime.utcnow()}
                }
            )
            
            # Recalculate average performance score
            training_data = mongo.db.website_training_data.find_one({'website_id': website_id})
            if training_data and 'ratings' in training_data:
                avg_score = sum(training_data['ratings']) / len(training_data['ratings'])
                mongo.db.website_training_data.update_one(
                    {'website_id': website_id},
                    {'$set': {'performance_score': avg_score}}
                )
            
        except Exception as e:
            print(f"Error updating performance score: {e}")
