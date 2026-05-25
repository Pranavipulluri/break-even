from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.models.order import Order
from app.services.email_service import EmailService
from bson import ObjectId
from datetime import datetime

orders_bp = Blueprint('orders', __name__)
email_service = EmailService()

@orders_bp.route('/orders/create', methods=['POST'])
def create_order():
    """Create a new order from mini-site (no auth required)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['business_id', 'customer_name', 'customer_email', 
                          'customer_phone', 'items', 'total_amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create order
        order = Order(
            business_id=data['business_id'],
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data['customer_phone'],
            items=data['items'],
            total_amount=data['total_amount'],
            delivery_address=data.get('delivery_address', ''),
            notes=data.get('notes', '')
        )
        
        # Add measurements if provided
        if 'measurements' in data:
            order.add_measurements(data['measurements'])
        
        # Insert into database
        result = mongo.db.orders.insert_one(order.to_dict())
        order_id = str(result.inserted_id)
        
        # Get business info for email
        business = mongo.db.child_websites.find_one({'_id': ObjectId(data['business_id'])})
        
        # Send confirmation email to customer
        try:
            email_service.send_order_confirmation(order, business)
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        # Notify business owner via WebSocket (if connected)
        # This will be handled by WebSocket service
        
        return jsonify({
            'message': 'Order placed successfully',
            'order_id': order_id,
            'status': 'pending'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/orders/business/<business_id>', methods=['GET'])
@jwt_required()
def get_business_orders(business_id):
    """Get all orders for a business"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify business ownership
        business = mongo.db.child_websites.find_one({
            '_id': ObjectId(business_id),
            'owner_id': ObjectId(current_user_id)
        })
        
        if not business:
            return jsonify({'error': 'Business not found or unauthorized'}), 404
        
        # Get filters from query params
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        # Build query
        query = {'business_id': ObjectId(business_id)}
        if status:
            query['status'] = status
        
        # Get orders
        orders = list(mongo.db.orders.find(query)
                     .sort('created_at', -1)
                     .skip(skip)
                     .limit(limit))
        
        # Convert ObjectIds to strings
        for order in orders:
            order['_id'] = str(order['_id'])
            order['business_id'] = str(order['business_id'])
        
        # Get total count
        total_count = mongo.db.orders.count_documents(query)
        
        return jsonify({
            'orders': orders,
            'total': total_count,
            'limit': limit,
            'skip': skip
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/orders/<order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get order details"""
    try:
        current_user_id = get_jwt_identity()
        
        order = mongo.db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Verify business ownership
        business = mongo.db.child_websites.find_one({
            '_id': order['business_id'],
            'owner_id': ObjectId(current_user_id)
        })
        
        if not business:
            return jsonify({'error': 'Unauthorized'}), 403
        
        order['_id'] = str(order['_id'])
        order['business_id'] = str(order['business_id'])
        
        return jsonify({'order': order}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/orders/<order_id>/status', methods=['PATCH'])
@jwt_required()
def update_order_status(order_id):
    """Update order status"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'error': 'status is required'}), 400
        
        new_status = data['status']
        valid_statuses = ['pending', 'processing', 'completed', 'cancelled']
        
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        # Get order
        order_data = mongo.db.orders.find_one({'_id': ObjectId(order_id)})
        if not order_data:
            return jsonify({'error': 'Order not found'}), 404
        
        # Verify business ownership
        business = mongo.db.child_websites.find_one({
            '_id': order_data['business_id'],
            'owner_id': ObjectId(current_user_id)
        })
        
        if not business:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Update order
        order = Order.from_dict(order_data)
        order.update_status(new_status)
        
        # Add tracking number if provided
        if 'tracking_number' in data:
            order.set_tracking_number(data['tracking_number'])
        
        # Update in database
        mongo.db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': order.to_dict()}
        )
        
        # Send status update email
        try:
            email_service.send_order_status_update(order, business, new_status)
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        return jsonify({
            'message': 'Order status updated successfully',
            'status': new_status
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/orders/<order_id>/cancel', methods=['PATCH'])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get order
        order_data = mongo.db.orders.find_one({'_id': ObjectId(order_id)})
        if not order_data:
            return jsonify({'error': 'Order not found'}), 404
        
        # Verify business ownership
        business = mongo.db.child_websites.find_one({
            '_id': order_data['business_id'],
            'owner_id': ObjectId(current_user_id)
        })
        
        if not business:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Cancel order
        order = Order.from_dict(order_data)
        order.cancel(reason=data.get('reason', ''))
        
        # Update in database
        mongo.db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': order.to_dict()}
        )
        
        # Send cancellation email
        try:
            email_service.send_order_status_update(order, business, 'cancelled')
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        return jsonify({
            'message': 'Order cancelled successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/orders/stats/<business_id>', methods=['GET'])
@jwt_required()
def get_order_stats(business_id):
    """Get order statistics for a business"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify business ownership
        business = mongo.db.child_websites.find_one({
            '_id': ObjectId(business_id),
            'owner_id': ObjectId(current_user_id)
        })
        
        if not business:
            return jsonify({'error': 'Business not found or unauthorized'}), 404
        
        # Get stats
        pipeline = [
            {'$match': {'business_id': ObjectId(business_id)}},
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1},
                'total_amount': {'$sum': '$total_amount'}
            }}
        ]
        
        stats = list(mongo.db.orders.aggregate(pipeline))
        
        # Format stats
        result = {
            'total_orders': 0,
            'total_revenue': 0,
            'pending': 0,
            'processing': 0,
            'completed': 0,
            'cancelled': 0
        }
        
        for stat in stats:
            status = stat['_id']
            count = stat['count']
            amount = stat['total_amount']
            
            result['total_orders'] += count
            result['total_revenue'] += amount
            result[status] = count
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
