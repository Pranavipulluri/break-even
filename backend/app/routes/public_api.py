from flask import Blueprint, request, jsonify
from app import mongo
from bson import ObjectId
from datetime import datetime
import random

public_api_bp = Blueprint('public_api', __name__)

# =================== DISCOVER BUSINESSES ENDPOINTS ===================

@public_api_bp.route('/public/discover/businesses', methods=['GET'])
def discover_businesses():
    """
    Public endpoint to discover businesses created with Break-even platform
    """
    try:
        # Get query parameters
        search = request.args.get('search', '')
        category = request.args.get('category', 'all')
        location = request.args.get('location', '')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        # Build search query
        query = {
            'is_active': True,
            'allow_discovery': {'$ne': False}  # Allow discovery unless explicitly disabled
        }
        
        # Search filter
        if search:
            search_regex = {'$regex': search, '$options': 'i'}
            query['$or'] = [
                {'name': search_regex},
                {'business_description': search_regex},
                {'business_category': search_regex},
                {'business_tags': {'$in': [search_regex]}},
                {'services': {'$elemMatch': {'name': search_regex}}}
            ]
        
        # Category filter
        if category and category != 'all':
            query['business_category'] = category
        
        # Location filter (simple text search for now)
        if location:
            location_regex = {'$regex': location, '$options': 'i'}
            query['$or'] = query.get('$or', []) + [
                {'address': location_regex},
                {'city': location_regex},
                {'state': location_regex}
            ]
        
        # Get businesses
        businesses = list(mongo.db.users.find(query, {
            'password': 0,  # Exclude sensitive data
            'email_verified': 0,
            'verification_token': 0,
            'reset_token': 0
        }).sort('created_at', -1).skip(offset).limit(limit))
        
        # Transform business data for public consumption
        public_businesses = []
        for business in businesses:
            # Get some sample products/services
            products = list(mongo.db.products.find({
                'user_id': business['_id'],
                'is_active': True
            }).limit(3))
            
            # Get some sample feedback
            feedback = list(mongo.db.customer_feedback.find({
                'business_id': business['_id']
            }).sort('created_at', -1).limit(3))
            
            # Calculate average rating
            avg_rating = 4.5  # Default
            review_count = 0
            if feedback:
                ratings = [f.get('rating', 5) for f in feedback if f.get('rating')]
                if ratings:
                    avg_rating = round(sum(ratings) / len(ratings), 1)
                    review_count = len(ratings)
            else:
                # Generate mock ratings for demo
                review_count = random.randint(15, 300)
                avg_rating = round(random.uniform(4.2, 4.9), 1)
            
            # Generate mock distance (in a real app, this would use user's location)
            distance = round(random.uniform(0.5, 5.0), 1)
            
            # Determine business hours
            hours = business.get('business_hours', '9:00 AM - 6:00 PM')
            
            # Get website URL
            website_url = f"{business.get('name', 'business').lower().replace(' ', '-')}.break-even.app"
            
            # Create public business profile
            public_business = {
                'id': str(business['_id']),
                'name': business.get('name', 'Business'),
                'description': business.get('business_description', 'Welcome to our business!'),
                'category': business.get('business_category', 'services'),
                'rating': avg_rating,
                'reviews': review_count,
                'location': business.get('address', 'Location not specified'),
                'city': business.get('city', ''),
                'state': business.get('state', ''),
                'distance': f"{distance} km",
                'phone': business.get('phone', ''),
                'website': website_url,
                'image': business.get('profile_image', f"https://images.unsplash.com/photo-{random.choice(['1560066984-138dadb4c035', '1589829545856-d10d557cf95f', '1517248135467-4c7edcad34c4', '1571019613454-1cb2f99b2d8b', '1460925895917-afdab827c52f', '1548681528-6a5c45b66e42'])}?w=400&h=300&fit=crop"),
                'tags': business.get('business_tags', [])[:3],  # Limit to 3 tags
                'openTime': hours,
                'featured': random.choice([True, False]) if review_count > 50 else False,
                'services': [p.get('name', 'Service') for p in products][:3],
                'joinedDate': business.get('created_at', datetime.utcnow()).strftime('%Y-%m-%d'),
                'isVerified': business.get('is_verified', False),
                'responseTime': f"{random.randint(1, 24)} hours"
            }
            
            public_businesses.append(public_business)
        
        # Get total count for pagination
        total_count = mongo.db.users.count_documents(query)
        
        return jsonify({
            'success': True,
            'businesses': public_businesses,
            'total': total_count,
            'count': len(public_businesses),
            'offset': offset,
            'limit': limit,
            'hasMore': offset + limit < total_count
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching businesses: {str(e)}',
            'businesses': []
        }), 500

@public_api_bp.route('/public/discover/categories', methods=['GET'])
def get_discover_categories():
    """
    Get available business categories for filtering
    """
    try:
        # Get categories from actual businesses
        pipeline = [
            {'$match': {'is_active': True, 'allow_discovery': {'$ne': False}}},
            {'$group': {'_id': '$business_category', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        
        categories_data = list(mongo.db.users.aggregate(pipeline))
        
        # Default categories with icons
        default_categories = [
            {'value': 'beauty', 'label': 'Beauty & Wellness', 'icon': '💄'},
            {'value': 'legal', 'label': 'Legal Services', 'icon': '⚖️'},
            {'value': 'restaurant', 'label': 'Food & Dining', 'icon': '🍽️'},
            {'value': 'fitness', 'label': 'Fitness & Sports', 'icon': '💪'},
            {'value': 'services', 'label': 'Professional Services', 'icon': '💼'},
            {'value': 'healthcare', 'label': 'Healthcare', 'icon': '🏥'},
            {'value': 'education', 'label': 'Education', 'icon': '📚'},
            {'value': 'retail', 'label': 'Retail & Shopping', 'icon': '🛍️'},
            {'value': 'automotive', 'label': 'Automotive', 'icon': '🚗'},
            {'value': 'technology', 'label': 'Technology', 'icon': '💻'}
        ]
        
        # Merge with actual data
        categories = []
        for cat in default_categories:
            count = next((c['count'] for c in categories_data if c['_id'] == cat['value']), 0)
            if count > 0:  # Only show categories with businesses
                categories.append({
                    **cat,
                    'count': count
                })
        
        return jsonify({
            'success': True,
            'categories': categories
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching categories: {str(e)}',
            'categories': []
        }), 500

@public_api_bp.route('/public/discover/featured', methods=['GET'])
def get_featured_businesses():
    """
    Get featured businesses for the discover page
    """
    try:
        limit = int(request.args.get('limit', 6))
        
        # Get businesses with high ratings and recent activity
        pipeline = [
            {'$match': {'is_active': True, 'allow_discovery': {'$ne': False}}},
            {'$lookup': {
                'from': 'customer_feedback',
                'localField': '_id',
                'foreignField': 'business_id',
                'as': 'feedback'
            }},
            {'$addFields': {
                'avgRating': {'$avg': '$feedback.rating'},
                'reviewCount': {'$size': '$feedback'},
                'recentActivity': {'$max': '$feedback.created_at'}
            }},
            {'$match': {
                '$or': [
                    {'reviewCount': {'$gte': 10}},
                    {'created_at': {'$gte': datetime.utcnow().replace(day=1)}}  # Recent businesses
                ]
            }},
            {'$sort': {'avgRating': -1, 'reviewCount': -1}},
            {'$limit': limit},
            {'$project': {
                'password': 0,
                'email_verified': 0,
                'verification_token': 0,
                'reset_token': 0,
                'feedback': 0
            }}
        ]
        
        businesses = list(mongo.db.users.aggregate(pipeline))
        
        # If not enough featured businesses, fill with recent ones
        if len(businesses) < limit:
            additional_needed = limit - len(businesses)
            existing_ids = [b['_id'] for b in businesses]
            
            additional_businesses = list(mongo.db.users.find({
                '_id': {'$nin': existing_ids},
                'is_active': True,
                'allow_discovery': {'$ne': False}
            }, {
                'password': 0,
                'email_verified': 0,
                'verification_token': 0,
                'reset_token': 0
            }).sort('created_at', -1).limit(additional_needed))
            
            businesses.extend(additional_businesses)
        
        # Transform for public consumption (same as discover_businesses)
        featured_businesses = []
        for business in businesses:
            # Generate mock data for demo
            avg_rating = round(random.uniform(4.5, 5.0), 1)
            review_count = random.randint(50, 500)
            distance = round(random.uniform(0.2, 3.0), 1)
            
            featured_business = {
                'id': str(business['_id']),
                'name': business.get('name', 'Business'),
                'description': business.get('business_description', 'Premium business partner'),
                'category': business.get('business_category', 'services'),
                'rating': avg_rating,
                'reviews': review_count,
                'location': business.get('address', 'Prime Location'),
                'distance': f"{distance} km",
                'phone': business.get('phone', ''),
                'website': f"{business.get('name', 'business').lower().replace(' ', '-')}.break-even.app",
                'image': business.get('profile_image', f"https://images.unsplash.com/photo-{random.choice(['1560066984-138dadb4c035', '1589829545856-d10d557cf95f', '1517248135467-4c7edcad34c4'])}?w=400&h=300&fit=crop"),
                'tags': business.get('business_tags', ['Premium', 'Verified', 'Top Rated'])[:3],
                'openTime': business.get('business_hours', '9:00 AM - 8:00 PM'),
                'featured': True,
                'isVerified': True,
                'responseTime': f"{random.randint(1, 6)} hours"
            }
            
            featured_businesses.append(featured_business)
        
        return jsonify({
            'success': True,
            'businesses': featured_businesses,
            'count': len(featured_businesses)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching featured businesses: {str(e)}',
            'businesses': []
        }), 500

@public_api_bp.route('/public/discover/stats', methods=['GET'])
def get_discover_stats():
    """
    Get discovery platform statistics
    """
    try:
        # Get basic stats
        total_businesses = mongo.db.users.count_documents({
            'is_active': True,
            'allow_discovery': {'$ne': False}
        })
        
        # Get category distribution
        category_stats = list(mongo.db.users.aggregate([
            {'$match': {'is_active': True, 'allow_discovery': {'$ne': False}}},
            {'$group': {'_id': '$business_category', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 5}
        ]))
        
        # Calculate total reviews (mock for now)
        total_reviews = total_businesses * random.randint(15, 45)
        
        # Cities with most businesses
        city_stats = list(mongo.db.users.aggregate([
            {'$match': {'is_active': True, 'allow_discovery': {'$ne': False}, 'city': {'$exists': True, '$ne': ''}}},
            {'$group': {'_id': '$city', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 5}
        ]))
        
        return jsonify({
            'success': True,
            'stats': {
                'totalBusinesses': total_businesses,
                'totalReviews': total_reviews,
                'avgRating': 4.6,
                'topCategories': category_stats,
                'topCities': city_stats,
                'newBusinessesThisMonth': random.randint(50, 150)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching stats: {str(e)}',
            'stats': {}
        }), 500

@public_api_bp.route('/public/products/<business_id>', methods=['GET'])
def get_public_products(business_id):
    """
    Public endpoint to fetch products for mini-websites
    No authentication required - for display on child websites
    """
    try:
        # Convert business_id to ObjectId
        user_id = ObjectId(business_id)
        
        # Get products for this business
        products = list(mongo.db.products.find({
            'user_id': user_id,
            'is_active': True
        }).sort('created_at', -1).limit(20))  # Limit to 20 products
        
        # Convert ObjectId to string for JSON serialization
        for product in products:
            product['_id'] = str(product['_id'])
            product['user_id'] = str(product['user_id'])
            
            # Remove sensitive information
            if 'cost' in product:
                del product['cost']
        
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching products: {str(e)}',
            'products': []
        }), 500

@public_api_bp.route('/public/business/<business_id>', methods=['GET'])
def get_public_business_info(business_id):
    """
    Public endpoint to fetch business information for mini-websites
    """
    try:
        # Convert business_id to ObjectId
        user_id = ObjectId(business_id)
        
        # Get user/business information
        user = mongo.db.users.find_one({'_id': user_id})
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Business not found'
            }), 404
        
        # Return public business information
        business_info = {
            'name': user.get('name', 'Our Business'),
            'email': user.get('email', ''),
            'phone': user.get('phone', ''),
            'address': user.get('address', ''),
            'description': user.get('business_description', 'Welcome to our business!'),
            'website': user.get('website', ''),
            'social_media': user.get('social_media', {})
        }
        
        return jsonify({
            'success': True,
            'business': business_info
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching business info: {str(e)}'
        }), 500

@public_api_bp.route('/public/track-visit', methods=['POST'])
def track_website_visit():
    """
    Track visits to mini-websites for analytics
    """
    try:
        data = request.get_json()
        
        visit_data = {
            'business_id': data.get('business_id'),
            'website_source': data.get('website_source'),
            'visitor_ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'timestamp': datetime.utcnow(),
            'page_url': data.get('page_url'),
            'referrer': data.get('referrer')
        }
        
        # Insert visit tracking
        mongo.db.website_visits.insert_one(visit_data)
        
        return jsonify({
            'success': True,
            'message': 'Visit tracked'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error tracking visit: {str(e)}'
        }), 500

# =================== LAW FIRM INTEGRATION ENDPOINTS ===================

@public_api_bp.route('/public/submit-consultation', methods=['POST'])
def submit_consultation_booking():
    """
    Submit consultation booking for law firms
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['businessId', 'firstName', 'lastName', 'email', 'phone', 'practiceArea']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create consultation booking
        booking_data = {
            'business_id': ObjectId(data['businessId']),
            'type': 'consultation',
            'client_info': {
                'first_name': data['firstName'],
                'last_name': data['lastName'],
                'email': data['email'],
                'phone': data['phone'],
                'company': data.get('company', ''),
                'preferred_contact': data.get('preferredContact', 'email')
            },
            'consultation_details': {
                'practice_area': data['practiceArea'],
                'case_description': data.get('caseDescription', ''),
                'urgency_level': data.get('urgencyLevel', 'medium'),
                'preferred_date': data.get('preferredDate'),
                'preferred_time': data.get('preferredTime'),
                'is_existing_case': data.get('isExistingCase', False),
                'budget_range': data.get('budgetRange', '')
            },
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'source': 'mini_website',
            'is_read': False
        }
        
        # Insert booking
        result = mongo.db.consultation_bookings.insert_one(booking_data)
        
        # Register customer if not exists
        register_customer_from_booking(data['businessId'], {
            'name': f"{data['firstName']} {data['lastName']}",
            'email': data['email'],
            'phone': data['phone'],
            'company': data.get('company', ''),
            'source': 'consultation_booking'
        })
        
        # Create notification for business owner
        create_notification(data['businessId'], {
            'type': 'new_consultation',
            'title': 'New Consultation Request',
            'message': f"New consultation request from {data['firstName']} {data['lastName']} for {data['practiceArea']}",
            'booking_id': str(result.inserted_id)
        })
        
        # Send email confirmations
        try:
            from app.services.email_service import get_email_service
            email_service = get_email_service()
            
            # Get business info for email
            business = mongo.db.users.find_one({'_id': ObjectId(data['businessId'])})
            if business:
                business_info = {
                    'name': business.get('name', 'Law Office'),
                    'email': business.get('email', ''),
                    'phone': business.get('phone', ''),
                    'address': business.get('address', '')
                }
                
                # Send confirmation to client
                email_service.send_consultation_confirmation(booking_data, business_info)
                
                # Send notification to business owner
                if business.get('email'):
                    email_service.send_business_notification(
                        business['email'], 
                        'new_consultation', 
                        booking_data
                    )
        except Exception as e:
            print(f"Email sending error: {str(e)}")
        
        # Send real-time notification
        try:
            from app.services.realtime_service import get_realtime_service
            realtime_service = get_realtime_service()
            booking_data['_id'] = result.inserted_id  # Add the ID for real-time notification
            realtime_service.notify_new_booking(
                data['businessId'], 
                'consultation_booking', 
                booking_data
            )
        except Exception as e:
            print(f"Real-time notification error: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Consultation request submitted successfully',
            'booking_id': str(result.inserted_id)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error submitting consultation: {str(e)}'
        }), 500

@public_api_bp.route('/public/submit-legal-contact', methods=['POST'])
def submit_legal_contact():
    """
    Submit contact form for law firms
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['businessId', 'firstName', 'lastName', 'email', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create contact message
        message_data = {
            'business_id': ObjectId(data['businessId']),
            'type': 'contact_inquiry',
            'client_info': {
                'first_name': data['firstName'],
                'last_name': data['lastName'],
                'email': data['email'],
                'phone': data.get('phone', ''),
                'practice_area': data.get('practiceArea', '')
            },
            'message_details': {
                'subject': data['subject'],
                'message': data['message'],
                'urgency_level': data.get('urgencyLevel', 'medium')
            },
            'status': 'new',
            'created_at': datetime.utcnow(),
            'source': 'mini_website',
            'is_read': False
        }
        
        # Insert message
        result = mongo.db.client_messages.insert_one(message_data)
        
        # Register customer
        register_customer_from_booking(data['businessId'], {
            'name': f"{data['firstName']} {data['lastName']}",
            'email': data['email'],
            'phone': data.get('phone', ''),
            'source': 'contact_form'
        })
        
        # Create notification
        create_notification(data['businessId'], {
            'type': 'new_message',
            'title': 'New Contact Message',
            'message': f"New message from {data['firstName']} {data['lastName']}: {data['subject']}",
            'message_id': str(result.inserted_id)
        })
        
        # Send real-time notification
        try:
            from app.services.realtime_service import get_realtime_service
            realtime_service = get_realtime_service()
            message_data['_id'] = result.inserted_id  # Add the ID for real-time notification
            realtime_service.notify_new_message(
                data['businessId'], 
                'legal_contact', 
                message_data
            )
        except Exception as e:
            print(f"Real-time notification error: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully',
            'message_id': str(result.inserted_id)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error sending message: {str(e)}'
        }), 500

# =================== TAILOR SHOP INTEGRATION ENDPOINTS ===================

@public_api_bp.route('/public/submit-measurement-booking', methods=['POST'])
def submit_measurement_booking():
    """
    Submit measurement booking for tailor shops
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['businessId', 'firstName', 'lastName', 'email', 'phone', 'service', 'preferredDate', 'preferredTime']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create measurement booking
        booking_data = {
            'business_id': ObjectId(data['businessId']),
            'type': 'measurement_session',
            'customer_info': {
                'first_name': data['firstName'],
                'last_name': data['lastName'],
                'email': data['email'],
                'phone': data['phone']
            },
            'booking_details': {
                'service_type': data['service'],
                'preferred_date': data['preferredDate'],
                'preferred_time': data['preferredTime'],
                'special_requirements': data.get('notes', ''),
                'urgency_level': data.get('urgencyLevel', 'normal')
            },
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'source': 'mini_website',
            'is_read': False,
            'appointment_confirmed': False
        }
        
        # Insert booking
        result = mongo.db.measurement_bookings.insert_one(booking_data)
        
        # Register customer
        register_customer_from_booking(data['businessId'], {
            'name': f"{data['firstName']} {data['lastName']}",
            'email': data['email'],
            'phone': data['phone'],
            'source': 'measurement_booking'
        })
        
        # Create notification
        create_notification(data['businessId'], {
            'type': 'new_measurement_booking',
            'title': 'New Measurement Appointment',
            'message': f"New measurement booking from {data['firstName']} {data['lastName']} for {data['service']}",
            'booking_id': str(result.inserted_id)
        })
        
        # Send email confirmations
        try:
            from app.services.email_service import get_email_service
            email_service = get_email_service()
            
            # Get business info for email
            business = mongo.db.users.find_one({'_id': ObjectId(data['businessId'])})
            if business:
                business_info = {
                    'name': business.get('name', 'Tailor Shop'),
                    'email': business.get('email', ''),
                    'phone': business.get('phone', ''),
                    'address': business.get('address', '')
                }
                
                # Send confirmation to customer
                email_service.send_measurement_confirmation(booking_data, business_info)
                
                # Send notification to business owner
                if business.get('email'):
                    email_service.send_business_notification(
                        business['email'], 
                        'new_measurement_booking', 
                        booking_data
                    )
        except Exception as e:
            print(f"Email sending error: {str(e)}")
        
        # Send real-time notification
        try:
            from app.services.realtime_service import get_realtime_service
            realtime_service = get_realtime_service()
            booking_data['_id'] = result.inserted_id  # Add the ID for real-time notification
            realtime_service.notify_new_booking(
                data['businessId'], 
                'measurement_booking', 
                booking_data
            )
        except Exception as e:
            print(f"Real-time notification error: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Measurement booking submitted successfully',
            'booking_id': str(result.inserted_id)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error submitting measurement booking: {str(e)}'
        }), 500

@public_api_bp.route('/public/submit-order-inquiry', methods=['POST'])
def submit_order_inquiry():
    """
    Submit order inquiry for tailor shops
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['businessId', 'name', 'email', 'phone', 'service']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create order inquiry
        inquiry_data = {
            'business_id': ObjectId(data['businessId']),
            'type': 'order_inquiry',
            'customer_info': {
                'name': data['name'],
                'email': data['email'],
                'phone': data['phone']
            },
            'order_details': {
                'service_type': data['service'],
                'description': data.get('description', ''),
                'budget_range': data.get('budgetRange', ''),
                'timeline': data.get('timeline', ''),
                'fabric_preferences': data.get('fabricPreferences', ''),
                'measurements_taken': data.get('measurementsTaken', False)
            },
            'status': 'new',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'source': 'mini_website',
            'is_read': False,
            'quote_requested': True
        }
        
        # Insert inquiry
        result = mongo.db.order_inquiries.insert_one(inquiry_data)
        
        # Register customer
        register_customer_from_booking(data['businessId'], {
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'source': 'order_inquiry'
        })
        
        # Create notification
        create_notification(data['businessId'], {
            'type': 'new_order_inquiry',
            'title': 'New Order Inquiry',
            'message': f"New order inquiry from {data['name']} for {data['service']}",
            'inquiry_id': str(result.inserted_id)
        })
        
        # Send email confirmations
        try:
            from app.services.email_service import get_email_service
            email_service = get_email_service()
            
            # Get business info for email
            business = mongo.db.users.find_one({'_id': ObjectId(data['businessId'])})
            if business:
                business_info = {
                    'name': business.get('name', 'Business'),
                    'email': business.get('email', ''),
                    'phone': business.get('phone', ''),
                    'address': business.get('address', '')
                }
                
                # Send confirmation to customer
                email_service.send_order_inquiry_confirmation(inquiry_data, business_info)
                
                # Send notification to business owner
                if business.get('email'):
                    email_service.send_business_notification(
                        business['email'], 
                        'new_order_inquiry', 
                        inquiry_data
                    )
        except Exception as e:
            print(f"Email sending error: {str(e)}")
        
        # Send real-time notification
        try:
            from app.services.realtime_service import get_realtime_service
            realtime_service = get_realtime_service()
            inquiry_data['_id'] = result.inserted_id  # Add the ID for real-time notification
            realtime_service.notify_new_booking(
                data['businessId'], 
                'order_inquiry', 
                inquiry_data
            )
        except Exception as e:
            print(f"Real-time notification error: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Order inquiry submitted successfully',
            'inquiry_id': str(result.inserted_id)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error submitting order inquiry: {str(e)}'
        }), 500

@public_api_bp.route('/public/submit-contact', methods=['POST'])
def submit_general_contact():
    """
    Submit general contact form (works for both law firms and tailor shops)
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['businessId', 'firstName', 'lastName', 'email', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create contact message
        message_data = {
            'business_id': ObjectId(data['businessId']),
            'type': 'general_contact',
            'customer_info': {
                'first_name': data['firstName'],
                'last_name': data['lastName'],
                'email': data['email'],
                'phone': data.get('phone', ''),
                'service_interest': data.get('service', '')
            },
            'message_details': {
                'subject': data['subject'],
                'message': data['message']
            },
            'status': 'new',
            'created_at': datetime.utcnow(),
            'source': 'mini_website',
            'is_read': False
        }
        
        # Insert message
        result = mongo.db.contact_messages.insert_one(message_data)
        
        # Register customer
        register_customer_from_booking(data['businessId'], {
            'name': f"{data['firstName']} {data['lastName']}",
            'email': data['email'],
            'phone': data.get('phone', ''),
            'source': 'contact_form'
        })
        
        # Create notification
        create_notification(data['businessId'], {
            'type': 'new_contact',
            'title': 'New Contact Message',
            'message': f"New contact message from {data['firstName']} {data['lastName']}: {data['subject']}",
            'message_id': str(result.inserted_id)
        })
        
        # Send real-time notification
        try:
            from app.services.realtime_service import get_realtime_service
            realtime_service = get_realtime_service()
            message_data['_id'] = result.inserted_id  # Add the ID for real-time notification
            realtime_service.notify_new_message(
                data['businessId'], 
                'general_contact', 
                message_data
            )
        except Exception as e:
            print(f"Real-time notification error: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully',
            'message_id': str(result.inserted_id)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error sending message: {str(e)}'
        }), 500

@public_api_bp.route('/public/submit-feedback', methods=['POST'])
def submit_feedback():
    """
    Submit feedback/review from mini-websites with sentiment analysis
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['businessId', 'rating', 'feedback']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Perform sentiment analysis
        sentiment_result = None
        try:
            from app.services.sentiment_service import SentimentService
            sentiment_service = SentimentService()
            sentiment_result = sentiment_service.analyze_sentiment(data['feedback'])
        except Exception as e:
            print(f"Sentiment analysis error: {str(e)}")
            sentiment_result = {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'method': 'fallback'
            }
        
        # Create feedback entry
        feedback_data = {
            'business_id': ObjectId(data['businessId']),
            'customer_name': data.get('name', 'Anonymous'),
            'customer_email': data.get('email', ''),
            'rating': int(data['rating']),
            'feedback_text': data['feedback'],
            'sentiment_analysis': sentiment_result,
            'created_at': datetime.utcnow(),
            'source': 'mini_website',
            'is_read': False,
            'is_featured': False
        }
        
        # Insert feedback
        result = mongo.db.customer_feedback.insert_one(feedback_data)
        
        # Register customer if email provided
        if data.get('email'):
            register_customer_from_booking(data['businessId'], {
                'name': data.get('name', 'Feedback Submitter'),
                'email': data['email'],
                'source': 'feedback_submission'
            })
        
        # Create notification
        sentiment_emoji = "😊" if sentiment_result.get('sentiment') == 'positive' else "😐" if sentiment_result.get('sentiment') == 'neutral' else "😔"
        create_notification(data['businessId'], {
            'type': 'new_feedback',
            'title': f'New Feedback {sentiment_emoji}',
            'message': f"New {sentiment_result.get('sentiment', 'neutral')} feedback ({data['rating']}/5 stars) from {data.get('name', 'Anonymous')}",
            'feedback_id': str(result.inserted_id),
            'sentiment': sentiment_result.get('sentiment', 'neutral'),
            'rating': data['rating']
        })
        
        # Send real-time notification
        try:
            from app.services.realtime_service import get_realtime_service
            realtime_service = get_realtime_service()
            feedback_data['_id'] = result.inserted_id
            realtime_service.notify_new_feedback(data['businessId'], feedback_data)
        except Exception as e:
            print(f"Real-time notification error: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'sentiment': sentiment_result.get('sentiment', 'neutral'),
            'feedback_id': str(result.inserted_id)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error submitting feedback: {str(e)}'
        }), 500

@public_api_bp.route('/public/submit-newsletter', methods=['POST'])
def submit_newsletter_signup():
    """
    Handle newsletter signups from mini-websites
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['businessId', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Register customer with newsletter subscription
        register_customer_from_booking(data['businessId'], {
            'name': data.get('name', 'Newsletter Subscriber'),
            'email': data['email'],
            'phone': data.get('phone', ''),
            'source': 'newsletter_signup'
        })
        
        # Create notification for business owner
        create_notification(data['businessId'], {
            'type': 'newsletter_signup',
            'title': 'New Newsletter Subscriber',
            'message': f"New newsletter signup: {data.get('name', data['email'])}",
            'email': data['email']
        })
        
        # Send real-time notification
        try:
            from app.services.realtime_service import get_realtime_service
            realtime_service = get_realtime_service()
            subscriber_data = {
                'email': data['email'],
                'name': data.get('name', 'Newsletter Subscriber'),
                'timestamp': datetime.utcnow()
            }
            realtime_service.notify_newsletter_signup(data['businessId'], subscriber_data)
        except Exception as e:
            print(f"Real-time notification error: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Successfully subscribed to newsletter'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing newsletter signup: {str(e)}'
        }), 500

@public_api_bp.route('/public/track-event', methods=['POST'])
def track_user_event():
    """
    Track user events and interactions on mini-websites
    """
    try:
        data = request.get_json()
        
        # Create event tracking
        event_data = {
            'business_id': data.get('businessId'),
            'event_name': data.get('event'),
            'event_data': data.get('data', {}),
            'visitor_ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'timestamp': datetime.utcnow(),
            'page_url': data.get('url'),
            'session_id': data.get('sessionId')
        }
        
        # Insert event tracking
        mongo.db.user_events.insert_one(event_data)
        
        return jsonify({
            'success': True,
            'message': 'Event tracked'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error tracking event: {str(e)}'
        }), 500

# =================== HELPER FUNCTIONS ===================

def register_customer_from_booking(business_id, customer_data):
    """
    Register or update customer information from booking/contact forms
    """
    try:
        business_id = ObjectId(business_id)
        
        # Check if customer already exists
        existing_customer = mongo.db.customers.find_one({
            'business_owner_id': business_id,
            'email': customer_data['email']
        })
        
        if existing_customer:
            # Update last interaction
            mongo.db.customers.update_one(
                {'_id': existing_customer['_id']},
                {
                    '$set': {
                        'last_interaction': datetime.utcnow(),
                        'phone': customer_data.get('phone', existing_customer.get('phone', '')),
                        'name': customer_data.get('name', existing_customer.get('name', ''))
                    },
                    '$addToSet': {
                        'interaction_sources': customer_data.get('source', 'unknown')
                    }
                }
            )
        else:
            # Create new customer
            new_customer = {
                'business_owner_id': business_id,
                'name': customer_data.get('name', ''),
                'email': customer_data['email'],
                'phone': customer_data.get('phone', ''),
                'company': customer_data.get('company', ''),
                'registration_source': customer_data.get('source', 'mini_website'),
                'interaction_sources': [customer_data.get('source', 'unknown')],
                'created_at': datetime.utcnow(),
                'last_interaction': datetime.utcnow(),
                'is_active': True,
                'is_subscribed': True,
                'tags': [],
                'notes': ''
            }
            
            mongo.db.customers.insert_one(new_customer)
            
            # Send real-time notification for new customer
            try:
                from app.services.realtime_service import get_realtime_service
                realtime_service = get_realtime_service()
                realtime_service.notify_new_customer(business_id, new_customer)
            except Exception as e:
                print(f"Real-time customer notification error: {str(e)}")
            
    except Exception as e:
        print(f"Error registering customer: {str(e)}")

def create_notification(business_id, notification_data):
    """
    Create notification for business owner
    """
    try:
        business_id = ObjectId(business_id)
        
        notification = {
            'user_id': business_id,
            'type': notification_data['type'],
            'title': notification_data['title'],
            'message': notification_data['message'],
            'data': {k: v for k, v in notification_data.items() if k not in ['type', 'title', 'message']},
            'created_at': datetime.utcnow(),
            'is_read': False,
            'priority': notification_data.get('priority', 'normal')
        }
        
        mongo.db.notifications.insert_one(notification)
        
    except Exception as e:
        print(f"Error creating notification: {str(e)}")
