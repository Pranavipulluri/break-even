from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.services.sentiment_service import SentimentService
from bson import ObjectId
from datetime import datetime, timedelta
from collections import defaultdict, Counter

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/overview', methods=['GET'])
@jwt_required()
def get_analytics_overview():
    try:
        current_user_id = get_jwt_identity()
        
        # Date range
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Messages analytics
        messages = list(mongo.db.messages.find({
            'recipient_id': ObjectId(current_user_id),
            'created_at': {'$gte': start_date}
        }))
        
        # Customer analytics
        customers = list(mongo.db.child_customers.find({
            'business_owner_id': ObjectId(current_user_id),
            'created_at': {'$gte': start_date}
        }))
        
        # QR scans analytics
        qr_analytics = mongo.db.qr_analytics.find_one({
            'user_id': ObjectId(current_user_id)
        })
        
        # Website visits analytics
        website_visits = list(mongo.db.website_analytics.find({
            'business_owner_id': ObjectId(current_user_id),
            'visited_at': {'$gte': start_date}
        }))
        
        # Group data by date
        daily_data = defaultdict(lambda: {
            'messages': 0,
            'customers': 0,
            'visits': 0,
            'date': None
        })
        
        # Process messages
        for message in messages:
            date_key = message['created_at'].date()
            daily_data[date_key]['messages'] += 1
            daily_data[date_key]['date'] = date_key.isoformat()
        
        # Process customers
        for customer in customers:
            date_key = customer['created_at'].date()
            daily_data[date_key]['customers'] += 1
            daily_data[date_key]['date'] = date_key.isoformat()
        
        # Process visits
        for visit in website_visits:
            date_key = visit['visited_at'].date()
            daily_data[date_key]['visits'] += 1
            daily_data[date_key]['date'] = date_key.isoformat()
        
        # Convert to list and sort
        analytics_data = sorted(daily_data.values(), key=lambda x: x['date'] or '1900-01-01')
        
        return jsonify({
            'timeSeriesData': analytics_data,
            'totalMessages': len(messages),
            'totalCustomers': len(customers),
            'totalScans': qr_analytics.get('total_scans', 0) if qr_analytics else 0,
            'totalVisits': len(website_visits)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/analytics/sentiment', methods=['GET'])
@jwt_required()
def get_sentiment_analysis():
    try:
        current_user_id = get_jwt_identity()
        
        # Get messages and feedback
        messages = list(mongo.db.messages.find({
            'recipient_id': ObjectId(current_user_id)
        }))
        
        feedback_entries = list(mongo.db.customer_feedback.find({
            'business_owner_id': ObjectId(current_user_id)
        }))
        
        sentiment_service = SentimentService()
        
        # Analyze message sentiment
        message_sentiments = []
        for message in messages:
            if message.get('content'):
                sentiment = sentiment_service.analyze_sentiment(message['content'])
                message_sentiments.append({
                    'id': str(message['_id']),
                    'content': message['content'][:100] + '...' if len(message['content']) > 100 else message['content'],
                    'sentiment': sentiment,
                    'customer_name': message.get('customer_name', 'Anonymous'),
                    'created_at': message['created_at']
                })
        
        # Analyze feedback sentiment
        feedback_sentiments = []
        for feedback in feedback_entries:
            if feedback.get('feedback_text'):
                sentiment = sentiment_service.analyze_sentiment(feedback['feedback_text'])
                feedback_sentiments.append({
                    'id': str(feedback['_id']),
                    'feedback': feedback['feedback_text'][:100] + '...' if len(feedback['feedback_text']) > 100 else feedback['feedback_text'],
                    'sentiment': sentiment,
                    'rating': feedback.get('rating'),
                    'created_at': feedback['created_at']
                })
        
        # Calculate sentiment distribution
        all_sentiments = [m['sentiment']['label'] for m in message_sentiments] + [f['sentiment']['label'] for f in feedback_sentiments]
        sentiment_distribution = Counter(all_sentiments)
        
        # Calculate average sentiment score
        all_scores = [m['sentiment']['score'] for m in message_sentiments] + [f['sentiment']['score'] for f in feedback_sentiments]
        avg_sentiment_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        return jsonify({
            'messageSentiments': message_sentiments,
            'feedbackSentiments': feedback_sentiments,
            'sentimentDistribution': dict(sentiment_distribution),
            'averageSentimentScore': avg_sentiment_score,
            'totalAnalyzed': len(message_sentiments) + len(feedback_sentiments)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/analytics/customers', methods=['GET'])
@jwt_required()
def get_customer_analytics():
    try:
        current_user_id = get_jwt_identity()
        
        # Get customer data
        customers = list(mongo.db.child_customers.find({
            'business_owner_id': ObjectId(current_user_id)
        }))
        
        # Geographic distribution
        location_counter = Counter()
        for customer in customers:
            location = customer.get('location', 'Unknown')
            location_counter[location] += 1
        
        # Registration trends (last 6 months)
        monthly_registrations = defaultdict(int)
        for customer in customers:
            month_key = customer['created_at'].strftime('%Y-%m')
            monthly_registrations[month_key] += 1
        
        # Sort monthly data
        sorted_months = sorted(monthly_registrations.items())
        registration_trend = [
            {'month': month, 'registrations': count}
            for month, count in sorted_months[-6:]  # Last 6 months
        ]
        
        # Customer engagement (based on messages sent)
        customer_engagement = defaultdict(int)
        messages = list(mongo.db.messages.find({
            'recipient_id': ObjectId(current_user_id)
        }))
        
        for message in messages:
            customer_email = message.get('customer_email')
            if customer_email:
                customer_engagement[customer_email] += 1
        
        # Top engaged customers
        top_customers = sorted(
            customer_engagement.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return jsonify({
            'totalCustomers': len(customers),
            'locationDistribution': dict(location_counter),
            'registrationTrend': registration_trend,
            'topEngagedCustomers': [
                {'email': email, 'messageCount': count}
                for email, count in top_customers
            ],
            'averageEngagement': sum(customer_engagement.values()) / len(customer_engagement) if customer_engagement else 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/analytics/products', methods=['GET'])
@jwt_required()
def get_product_analytics():
    try:
        current_user_id = get_jwt_identity()
        
        # Get products
        products = list(mongo.db.products.find({
            'user_id': ObjectId(current_user_id),
            'is_active': True
        }))
        
        # Get product interactions (views, inquiries)
        product_interactions = list(mongo.db.product_interactions.find({
            'business_owner_id': ObjectId(current_user_id)
        }))
        
        # Calculate product popularity
        product_views = defaultdict(int)
        product_inquiries = defaultdict(int)
        
        for interaction in product_interactions:
            product_id = str(interaction['product_id'])
            if interaction['interaction_type'] == 'view':
                product_views[product_id] += 1
            elif interaction['interaction_type'] == 'inquiry':
                product_inquiries[product_id] += 1
        
        # Combine with product data
        product_analytics = []
        for product in products:
            product_id = str(product['_id'])
            product_analytics.append({
                'id': product_id,
                'name': product['name'],
                'category': product['category'],
                'price': product['price'],
                'stock': product['stock'],
                'views': product_views.get(product_id, 0),
                'inquiries': product_inquiries.get(product_id, 0),
                'popularity_score': product_views.get(product_id, 0) + product_inquiries.get(product_id, 0) * 2
            })
        
        # Sort by popularity
        product_analytics.sort(key=lambda x: x['popularity_score'], reverse=True)
        
        # Category distribution
        category_counter = Counter(product['category'] for product in products)
        
        # Low stock alerts
        low_stock_products = [
            product for product in products
            if product['stock'] < 10  # Configurable threshold
        ]
        
        return jsonify({
            'productAnalytics': product_analytics,
            'categoryDistribution': dict(category_counter),
            'lowStockAlerts': len(low_stock_products),
            'totalProducts': len(products),
            'totalViews': sum(product_views.values()),
            'totalInquiries': sum(product_inquiries.values())
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

