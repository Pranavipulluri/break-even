from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from bson import ObjectId
from datetime import datetime, timedelta
from collections import defaultdict

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    try:
        current_user_id = get_jwt_identity()
        
        # Get total products
        total_products = mongo.db.products.count_documents({
            'user_id': ObjectId(current_user_id),
            'is_active': True
        })
        
        # Get total customers from child websites
        total_customers = mongo.db.child_customers.count_documents({
            'business_owner_id': ObjectId(current_user_id)
        })
        
        # Get messages count
        total_messages = mongo.db.messages.count_documents({
            'recipient_id': ObjectId(current_user_id)
        })
        
        # Get QR scans
        qr_analytics = mongo.db.qr_analytics.find_one({
            'user_id': ObjectId(current_user_id)
        })
        total_scans = qr_analytics.get('total_scans', 0) if qr_analytics else 0
        
        # Get sales data (mock for now - you can implement actual sales tracking)
        monthly_revenue = 0
        orders = list(mongo.db.orders.find({
            'business_owner_id': ObjectId(current_user_id),
            'created_at': {'$gte': datetime.utcnow() - timedelta(days=30)}
        }))
        
        for order in orders:
            monthly_revenue += order.get('total_amount', 0)
        
        # Get recent activity
        recent_messages = list(mongo.db.messages.find({
            'recipient_id': ObjectId(current_user_id)
        }).sort('created_at', -1).limit(5))
        
        recent_customers = list(mongo.db.child_customers.find({
            'business_owner_id': ObjectId(current_user_id)
        }).sort('created_at', -1).limit(5))
        
        # Analytics data for charts
        analytics_data = []
        for i in range(6):
            month_start = datetime.utcnow() - timedelta(days=30*(i+1))
            month_end = datetime.utcnow() - timedelta(days=30*i)
            
            month_orders = list(mongo.db.orders.find({
                'business_owner_id': ObjectId(current_user_id),
                'created_at': {'$gte': month_start, '$lt': month_end}
            }))
            
            sales_count = len(month_orders)
            revenue = sum(order.get('total_amount', 0) for order in month_orders)
            
            analytics_data.append({
                'month': month_start.strftime('%b'),
                'sales': sales_count,
                'revenue': revenue
            })
        
        analytics_data.reverse()
        
        return jsonify({
            'stats': {
                'totalProducts': total_products,
                'totalCustomers': total_customers,
                'totalMessages': total_messages,
                'totalScans': total_scans,
                'monthlyRevenue': monthly_revenue
            },
            'analytics': analytics_data,
            'recentActivity': {
                'messages': [
                    {
                        'id': str(msg['_id']),
                        'content': msg['content'][:50] + '...' if len(msg['content']) > 50 else msg['content'],
                        'customer_name': msg.get('customer_name', 'Anonymous'),
                        'created_at': msg['created_at']
                    } for msg in recent_messages
                ],
                'customers': [
                    {
                        'id': str(customer['_id']),
                        'name': customer['name'],
                        'email': customer['email'],
                        'created_at': customer['created_at']
                    } for customer in recent_customers
                ]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    try:
        current_user_id = get_jwt_identity()
        
        # Get today's stats
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        today_messages = mongo.db.messages.count_documents({
            'recipient_id': ObjectId(current_user_id),
            'created_at': {'$gte': today_start, '$lt': today_end}
        })
        
        today_customers = mongo.db.child_customers.count_documents({
            'business_owner_id': ObjectId(current_user_id),
            'created_at': {'$gte': today_start, '$lt': today_end}
        })
        
        today_scans = 0
        qr_analytics = mongo.db.qr_analytics.find_one({
            'user_id': ObjectId(current_user_id)
        })
        if qr_analytics and qr_analytics.get('last_scan_date') == today_start.date():
            today_scans = qr_analytics.get('scans_today', 0)
        
        return jsonify({
            'todayMessages': today_messages,
            'todayCustomers': today_customers,
            'todayScans': today_scans
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
