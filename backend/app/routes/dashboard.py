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
        
        # Get messages count from all collections
        biz_oid = ObjectId(current_user_id)
        total_messages = (
            mongo.db.messages.count_documents({'recipient_id': biz_oid}) +
            mongo.db.contact_messages.count_documents({'business_id': biz_oid}) +
            mongo.db.client_messages.count_documents({'business_id': biz_oid})
        )
        
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
        
        # Get recent activity from all message collections
        recent_messages = list(mongo.db.messages.find({
            'recipient_id': biz_oid
        }).sort('created_at', -1).limit(5))
        
        recent_contact = list(mongo.db.contact_messages.find({
            'business_id': biz_oid
        }).sort('created_at', -1).limit(5))
        
        recent_client = list(mongo.db.client_messages.find({
            'business_id': biz_oid
        }).sort('created_at', -1).limit(5))
        
        # Normalize and merge recent messages
        normalized_messages = []
        for msg in recent_messages:
            normalized_messages.append({
                'id': str(msg['_id']),
                'content': msg.get('content', '')[:50] + '...' if len(msg.get('content', '')) > 50 else msg.get('content', ''),
                'customer_name': msg.get('customer_name', 'Anonymous'),
                'created_at': msg['created_at']
            })
            
        for msg in recent_contact:
            cust_info = msg.get('customer_info', {}) or {}
            cust_name = f"{cust_info.get('first_name', '')} {cust_info.get('last_name', '')}".strip() or "Anonymous"
            normalized_messages.append({
                'id': str(msg['_id']),
                'content': msg.get('message', '')[:50] + '...' if len(msg.get('message', '')) > 50 else msg.get('message', ''),
                'customer_name': cust_name,
                'created_at': msg['created_at']
            })
            
        for msg in recent_client:
            cust_info = msg.get('customer_info', {}) or {}
            cust_name = f"{cust_info.get('first_name', '')} {cust_info.get('last_name', '')}".strip() or "Anonymous"
            normalized_messages.append({
                'id': str(msg['_id']),
                'content': msg.get('message', '')[:50] + '...' if len(msg.get('message', '')) > 50 else msg.get('message', ''),
                'customer_name': cust_name,
                'created_at': msg['created_at']
            })
            
        # Sort combined recent messages by date
        def get_date(item):
            dt = item.get('created_at')
            if isinstance(dt, datetime):
                return dt
            return datetime.min
            
        normalized_messages.sort(key=get_date, reverse=True)
        recent_messages_feed = normalized_messages[:5]
        
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
                'messages': recent_messages_feed,
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
        
        biz_oid = ObjectId(current_user_id)
        
        today_messages = (
            mongo.db.messages.count_documents({
                'recipient_id': biz_oid,
                'created_at': {'$gte': today_start, '$lt': today_end}
            }) +
            mongo.db.contact_messages.count_documents({
                'business_id': biz_oid,
                'created_at': {'$gte': today_start, '$lt': today_end}
            }) +
            mongo.db.client_messages.count_documents({
                'business_id': biz_oid,
                'created_at': {'$gte': today_start, '$lt': today_end}
            })
        )
        
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
