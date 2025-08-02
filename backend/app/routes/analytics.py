from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.services.sentiment_service import SentimentService
from bson import ObjectId
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

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


# Email configuration for website integration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')

def send_email(to_email, subject, body, html_body=None):
    """Send email using SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add plain text part
        msg.attach(MIMEText(body, 'plain'))
        
        # Add HTML part if provided
        if html_body:
            msg.attach(MIMEText(html_body, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        logging.error(f"Email sending failed: {str(e)}")
        return False

@analytics_bp.route('/subscribers', methods=['GET'])
@jwt_required()
def get_subscribers():
    """Get all website subscribers"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        website_source = request.args.get('website_source')
        
        # Build query
        query = {}
        if website_source:
            query['website_source'] = website_source
        
        # Get total count
        total = mongo.db.website_subscribers.count_documents(query)
        
        # Get subscribers with pagination
        subscribers = list(mongo.db.website_subscribers.find(query)
                         .sort('created_at', -1)
                         .skip((page - 1) * limit)
                         .limit(limit))
        
        # Convert ObjectId to string
        for subscriber in subscribers:
            subscriber['_id'] = str(subscriber['_id'])
        
        return jsonify({
            'success': True,
            'subscribers': subscribers,
            'pagination': {
                'current_page': page,
                'total_pages': (total + limit - 1) // limit,
                'total_subscribers': total,
                'has_next': page * limit < total,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/feedback-analytics', methods=['GET'])
@jwt_required()
def get_feedback_analytics():
    """Get feedback analytics and sentiment analysis"""
    try:
        website_source = request.args.get('website_source')
        days = int(request.args.get('days', 30))
        
        # Date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Build query
        query = {'created_at': {'$gte': start_date, '$lte': end_date}}
        if website_source:
            query['website_source'] = website_source
        
        # Get feedback data
        feedback_data = list(mongo.db.website_feedback.find(query))
        
        # Calculate analytics
        total_feedback = len(feedback_data)
        sentiment_breakdown = {'positive': 0, 'negative': 0, 'neutral': 0}
        rating_data = []
        word_cloud_data = {}
        
        for feedback in feedback_data:
            # Sentiment breakdown
            sentiment = feedback.get('sentiment', {}).get('label', 'neutral')
            sentiment_breakdown[sentiment] += 1
            
            # Rating data
            if feedback.get('rating'):
                rating_data.append(feedback['rating'])
            
            # Word frequency for word cloud
            words = feedback.get('feedback', '').lower().split()
            for word in words:
                if len(word) > 3:  # Filter out short words
                    word_cloud_data[word] = word_cloud_data.get(word, 0) + 1
        
        # Calculate averages
        avg_rating = sum(rating_data) / len(rating_data) if rating_data else 0
        avg_sentiment_score = sum([f.get('sentiment', {}).get('score', 0) for f in feedback_data]) / total_feedback if total_feedback > 0 else 0
        
        # Top words for word cloud
        top_words = sorted(word_cloud_data.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Recent feedback
        recent_feedback = list(mongo.db.website_feedback.find(query)
                             .sort('created_at', -1)
                             .limit(10))
        
        for feedback in recent_feedback:
            feedback['_id'] = str(feedback['_id'])
        
        return jsonify({
            'success': True,
            'analytics': {
                'total_feedback': total_feedback,
                'sentiment_breakdown': sentiment_breakdown,
                'avg_rating': round(avg_rating, 2),
                'avg_sentiment_score': round(avg_sentiment_score, 3),
                'rating_distribution': {
                    '5': rating_data.count(5),
                    '4': rating_data.count(4),
                    '3': rating_data.count(3),
                    '2': rating_data.count(2),
                    '1': rating_data.count(1)
                },
                'word_cloud': top_words,
                'recent_feedback': recent_feedback,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/send-campaign', methods=['POST'])
@jwt_required()
def send_email_campaign():
    """Send email campaign to subscribers"""
    try:
        data = request.get_json()
        subject = data.get('subject', '')
        message = data.get('message', '')
        html_message = data.get('html_message', '')
        website_source = data.get('website_source')
        subscriber_filter = data.get('filter', 'all')  # all, newsletter_only, active_only
        
        if not subject or not message:
            return jsonify({
                'success': False,
                'error': 'Subject and message are required'
            }), 400
        
        # Build subscriber query
        query = {}
        if website_source:
            query['website_source'] = website_source
        
        if subscriber_filter == 'newsletter_only':
            query['newsletter_signup'] = True
        elif subscriber_filter == 'active_only':
            query['active'] = True
        
        # Get subscribers
        subscribers = list(mongo.db.website_subscribers.find(query, {'email': 1, 'name': 1}))
        
        if not subscribers:
            return jsonify({
                'success': False,
                'error': 'No subscribers found matching criteria'
            }), 400
        
        # Send emails
        sent_count = 0
        failed_emails = []
        
        for subscriber in subscribers:
            email = subscriber.get('email')
            name = subscriber.get('name', 'Valued Customer')
            
            # Personalize message
            personalized_message = message.replace('{{name}}', name)
            personalized_html = html_message.replace('{{name}}', name) if html_message else None
            
            if send_email(email, subject, personalized_message, personalized_html):
                sent_count += 1
            else:
                failed_emails.append(email)
        
        # Log campaign
        campaign_log = {
            'subject': subject,
            'message': message,
            'website_source': website_source,
            'filter_used': subscriber_filter,
            'total_subscribers': len(subscribers),
            'sent_count': sent_count,
            'failed_count': len(failed_emails),
            'failed_emails': failed_emails,
            'sent_by': get_jwt_identity(),
            'sent_at': datetime.now()
        }
        
        mongo.db.email_campaigns.insert_one(campaign_log)
        
        return jsonify({
            'success': True,
            'message': f'Campaign sent successfully',
            'stats': {
                'total_subscribers': len(subscribers),
                'sent_count': sent_count,
                'failed_count': len(failed_emails),
                'success_rate': (sent_count / len(subscribers)) * 100 if subscribers else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/dashboard-summary', methods=['GET'])
@jwt_required()
def get_dashboard_summary():
    """Get dashboard summary with key metrics"""
    try:
        # Date ranges
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Total subscribers
        total_subscribers = mongo.db.website_subscribers.count_documents({})
        new_subscribers_week = mongo.db.website_subscribers.count_documents({
            'created_at': {'$gte': week_ago}
        })
        
        # Total feedback
        total_feedback = mongo.db.website_feedback.count_documents({})
        new_feedback_week = mongo.db.website_feedback.count_documents({
            'created_at': {'$gte': week_ago}
        })
        
        # Sentiment summary (last 30 days)
        recent_feedback = list(mongo.db.website_feedback.find({
            'created_at': {'$gte': month_ago}
        }, {'sentiment': 1}))
        
        sentiment_summary = {'positive': 0, 'negative': 0, 'neutral': 0}
        for feedback in recent_feedback:
            sentiment = feedback.get('sentiment', {}).get('label', 'neutral')
            sentiment_summary[sentiment] += 1
        
        # Website sources
        website_sources = list(mongo.db.website_subscribers.aggregate([
            {'$group': {'_id': '$website_source', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]))
        
        # Recent activity
        recent_registrations = list(mongo.db.website_subscribers.find({})
                                  .sort('created_at', -1)
                                  .limit(5)
                                  .projection({'email': 1, 'name': 1, 'website_source': 1, 'created_at': 1}))
        
        for reg in recent_registrations:
            reg['_id'] = str(reg['_id'])
        
        return jsonify({
            'success': True,
            'summary': {
                'subscribers': {
                    'total': total_subscribers,
                    'new_this_week': new_subscribers_week,
                    'growth_rate': (new_subscribers_week / max(1, total_subscribers - new_subscribers_week)) * 100
                },
                'feedback': {
                    'total': total_feedback,
                    'new_this_week': new_feedback_week,
                    'sentiment_summary': sentiment_summary
                },
                'website_sources': website_sources,
                'recent_activity': recent_registrations
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/product-interests', methods=['GET'])
@jwt_required()
def get_product_interests():
    """Get product interest analytics"""
    try:
        current_user_id = get_jwt_identity()
        days = int(request.args.get('days', 30))
        website_source = request.args.get('website_source')
        
        # Date filter
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Build query
        query = {
            'business_id': ObjectId(current_user_id),
            'created_at': {'$gte': start_date}
        }
        
        if website_source:
            query['website_source'] = website_source
        
        # Get product interests
        interests = list(mongo.db.product_interests.find(query).sort('created_at', -1))
        
        # Convert ObjectId to string
        for interest in interests:
            interest['_id'] = str(interest['_id'])
            interest['business_id'] = str(interest['business_id'])
        
        # Analytics
        total_interests = len(interests)
        
        # Budget range distribution
        budget_distribution = {}
        timeline_distribution = {}
        lead_scores = []
        
        for interest in interests:
            # Budget range
            budget = interest.get('budget_range', 'not_specified')
            budget_distribution[budget] = budget_distribution.get(budget, 0) + 1
            
            # Purchase timeline
            timeline = interest.get('purchase_timeline', 'not_specified')
            timeline_distribution[timeline] = timeline_distribution.get(timeline, 0) + 1
            
            # Lead scores
            if 'lead_score' in interest:
                lead_scores.append(interest['lead_score'])
        
        # Average lead score
        avg_lead_score = sum(lead_scores) / len(lead_scores) if lead_scores else 0
        
        # High-value leads (score > 70)
        high_value_leads = len([score for score in lead_scores if score > 70])
        
        return jsonify({
            'success': True,
            'interests': interests,
            'analytics': {
                'total_interests': total_interests,
                'avg_lead_score': round(avg_lead_score, 2),
                'high_value_leads': high_value_leads,
                'budget_distribution': budget_distribution,
                'timeline_distribution': timeline_distribution
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/newsletter-analytics', methods=['GET'])
@jwt_required()
def get_newsletter_analytics():
    """Get newsletter subscription analytics"""
    try:
        current_user_id = get_jwt_identity()
        days = int(request.args.get('days', 30))
        website_source = request.args.get('website_source')
        
        # Date filter
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Build query
        query = {
            'business_id': ObjectId(current_user_id),
            'subscribed_at': {'$gte': start_date}
        }
        
        if website_source:
            query['website_source'] = website_source
        
        # Get newsletter subscribers
        subscribers = list(mongo.db.newsletter_subscribers.find(query))
        
        # Interest distribution
        interest_distribution = {}
        source_distribution = {}
        
        for subscriber in subscribers:
            # Interests
            interests = subscriber.get('interests', [])
            for interest in interests:
                interest_distribution[interest] = interest_distribution.get(interest, 0) + 1
            
            # Source
            source = subscriber.get('source', 'unknown')
            source_distribution[source] = source_distribution.get(source, 0) + 1
        
        # Growth over time (daily for last 30 days)
        growth_data = []
        for i in range(days):
            day_start = datetime.utcnow() - timedelta(days=i+1)
            day_end = datetime.utcnow() - timedelta(days=i)
            
            day_query = query.copy()
            day_query['subscribed_at'] = {'$gte': day_start, '$lt': day_end}
            
            count = mongo.db.newsletter_subscribers.count_documents(day_query)
            growth_data.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'subscribers': count
            })
        
        growth_data.reverse()  # Oldest to newest
        
        return jsonify({
            'success': True,
            'analytics': {
                'total_subscribers': len(subscribers),
                'interest_distribution': interest_distribution,
                'source_distribution': source_distribution,
                'growth_data': growth_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/ai-insights', methods=['GET'])
@jwt_required()
def get_ai_insights():
    """Get AI-powered business insights and recommendations"""
    try:
        current_user_id = get_jwt_identity()
        days = int(request.args.get('days', 30))
        
        # Get business context for AI analysis
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Collect comprehensive business data
        business_data = {
            'business_name': user.get('business_name', 'Business'),
            'business_type': user.get('business_type', 'General'),
            'industry': user.get('industry', 'General'),
            'location': user.get('area', 'N/A')
        }
        
        # Get performance metrics
        metrics = {}
        
        # Customer metrics
        total_customers = mongo.db.child_customers.count_documents({
            'business_owner_id': ObjectId(current_user_id)
        })
        new_customers = mongo.db.child_customers.count_documents({
            'business_owner_id': ObjectId(current_user_id),
            'created_at': {'$gte': start_date}
        })
        
        # Message metrics
        total_messages = mongo.db.messages.count_documents({
            'recipient_id': ObjectId(current_user_id)
        })
        recent_messages = mongo.db.messages.count_documents({
            'recipient_id': ObjectId(current_user_id),
            'created_at': {'$gte': start_date}
        })
        
        # Product metrics
        total_products = mongo.db.products.count_documents({
            'user_id': ObjectId(current_user_id),
            'is_active': True
        })
        
        # QR Analytics
        qr_analytics = mongo.db.qr_analytics.find_one({
            'user_id': ObjectId(current_user_id)
        })
        total_scans = qr_analytics.get('total_scans', 0) if qr_analytics else 0
        
        # Website visits
        website_visits = mongo.db.website_analytics.count_documents({
            'business_owner_id': ObjectId(current_user_id),
            'visited_at': {'$gte': start_date}
        })
        
        # Feedback analysis
        feedback_entries = list(mongo.db.customer_feedback.find({
            'business_owner_id': ObjectId(current_user_id),
            'created_at': {'$gte': start_date}
        }))
        
        # Sentiment analysis
        positive_feedback = sum(1 for f in feedback_entries if f.get('sentiment', {}).get('label') == 'positive')
        negative_feedback = sum(1 for f in feedback_entries if f.get('sentiment', {}).get('label') == 'negative')
        
        metrics = {
            'total_customers': total_customers,
            'new_customers': new_customers,
            'customer_growth_rate': (new_customers / max(1, total_customers - new_customers)) * 100,
            'total_messages': total_messages,
            'recent_messages': recent_messages,
            'message_response_rate': (recent_messages / max(1, new_customers)) * 100,
            'total_products': total_products,
            'total_scans': total_scans,
            'website_visits': website_visits,
            'total_feedback': len(feedback_entries),
            'positive_feedback': positive_feedback,
            'negative_feedback': negative_feedback,
            'customer_satisfaction': (positive_feedback / max(1, len(feedback_entries))) * 100
        }
        
        # Use AI service to generate insights
        from app.services.ai_service import AIService
        ai_service = AIService()
        
        # Generate comprehensive business insights
        insight_context = {
            'business_data': business_data,
            'metrics': metrics,
            'time_period': f'{days} days',
            'analysis_date': end_date.isoformat()
        }
        
        # Generate AI insights using existing method
        ai_context = {
            'business_name': business_data['business_name'],
            'business_type': business_data['business_type'],
            'total_products': metrics['total_products'],
            'recent_messages_count': metrics['recent_messages'],
            'qr_scans': metrics['total_scans'],
            'suggestion_type': 'comprehensive_analysis'
        }
        
        insights = ai_service.generate_business_suggestions(ai_context)
        
        return jsonify({
            'success': True,
            'insights': insights,
            'business_data': business_data,
            'metrics': metrics,
            'analysis_period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"AI insights error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate AI insights'
        }), 500

@analytics_bp.route('/analytics/chatbot-performance', methods=['GET'])
@jwt_required()
def get_chatbot_performance():
    """Get chatbot performance and effectiveness metrics"""
    try:
        current_user_id = get_jwt_identity()
        days = int(request.args.get('days', 30))
        
        # Date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get chatbot conversations
        conversations = list(mongo.db.chatbot_conversations.find({
            'user_id': ObjectId(current_user_id),
            'created_at': {'$gte': start_date, '$lte': end_date}
        }))
        
        # Get chatbot messages
        messages = list(mongo.db.chatbot_messages.find({
            'user_id': ObjectId(current_user_id),
            'created_at': {'$gte': start_date, '$lte': end_date}
        }))
        
        # Calculate performance metrics
        total_conversations = len(conversations)
        total_messages = len(messages)
        
        # Average conversation length
        avg_conversation_length = (
            sum(conv.get('message_count', 0) for conv in conversations) / total_conversations
            if total_conversations > 0 else 0
        )
        
        # Conversation duration analysis
        durations = []
        for conv in conversations:
            if conv.get('last_message_at'):
                duration = (conv['last_message_at'] - conv['created_at']).total_seconds() / 60
                durations.append(duration)
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Daily usage trend
        daily_usage = []
        for i in range(days):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_conversations = sum(1 for conv in conversations 
                                  if day_start <= conv['created_at'] < day_end)
            day_messages = sum(1 for msg in messages 
                             if day_start <= msg['created_at'] < day_end)
            
            daily_usage.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'conversations': day_conversations,
                'messages': day_messages
            })
        
        # Get training status
        training_data = mongo.db.chatbot_training.find_one({
            'user_id': ObjectId(current_user_id)
        })
        
        # Most common topics/themes
        common_themes = []
        if training_data:
            common_themes = training_data.get('common_customer_concerns', [])[:5]
        
        return jsonify({
            'success': True,
            'performance': {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'avg_conversation_length': round(avg_conversation_length, 2),
                'avg_duration_minutes': round(avg_duration, 2),
                'conversations_per_day': round(total_conversations / days, 2),
                'messages_per_day': round(total_messages / days, 2),
                'daily_usage': daily_usage,
                'common_themes': common_themes,
                'training_status': {
                    'is_trained': bool(training_data),
                    'last_trained': training_data['generated_at'].isoformat() if training_data else None,
                    'insights_count': (
                        len(training_data.get('common_customer_concerns', [])) +
                        len(training_data.get('frequently_asked_questions', []))
                        if training_data else 0
                    )
                }
            },
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Chatbot performance error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get chatbot performance data'
        }), 500

