from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from bson import ObjectId
from datetime import datetime, timedelta

bookings_bp = Blueprint('bookings', __name__)

# =================== CONSULTATION BOOKINGS (LAW FIRMS) ===================

@bookings_bp.route('/bookings/consultations', methods=['GET'])
@jwt_required()
def get_consultation_bookings():
    """
    Get all consultation bookings for the authenticated law firm
    """
    try:
        user_id = ObjectId(get_jwt_identity())
        
        # Get filter parameters
        status = request.args.get('status', 'all')
        days = int(request.args.get('days', 30))
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Build query
        query = {'business_id': user_id}
        
        if status != 'all':
            query['status'] = status
            
        # Date filter
        if days > 0:
            start_date = datetime.utcnow() - timedelta(days=days)
            query['created_at'] = {'$gte': start_date}
        
        # Get bookings with pagination
        skip = (page - 1) * limit
        bookings = list(mongo.db.consultation_bookings.find(query)
                       .sort('created_at', -1)
                       .skip(skip)
                       .limit(limit))
        
        # Convert ObjectId to string
        for booking in bookings:
            booking['_id'] = str(booking['_id'])
            booking['business_id'] = str(booking['business_id'])
        
        # Get total count
        total_count = mongo.db.consultation_bookings.count_documents(query)
        
        return jsonify({
            'success': True,
            'bookings': bookings,
            'pagination': {
                'current_page': page,
                'total_pages': (total_count + limit - 1) // limit,
                'total_items': total_count,
                'has_next': page * limit < total_count,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching consultation bookings: {str(e)}'
        }), 500

@bookings_bp.route('/bookings/consultations/<booking_id>', methods=['PUT'])
@jwt_required()
def update_consultation_booking(booking_id):
    """
    Update consultation booking status and details
    """
    try:
        user_id = ObjectId(get_jwt_identity())
        data = request.get_json()
        
        # Verify booking belongs to user
        booking = mongo.db.consultation_bookings.find_one({
            '_id': ObjectId(booking_id),
            'business_id': user_id
        })
        
        if not booking:
            return jsonify({
                'success': False,
                'message': 'Booking not found'
            }), 404
        
        # Prepare update data
        update_data = {
            'updated_at': datetime.utcnow()
        }
        
        # Update allowed fields
        allowed_fields = ['status', 'notes', 'scheduled_date', 'scheduled_time', 'attorney_assigned']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        # Mark as read
        if data.get('mark_as_read'):
            update_data['is_read'] = True
        
        # Update booking
        mongo.db.consultation_bookings.update_one(
            {'_id': ObjectId(booking_id)},
            {'$set': update_data}
        )
        
        return jsonify({
            'success': True,
            'message': 'Booking updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating booking: {str(e)}'
        }), 500

# =================== MEASUREMENT BOOKINGS (TAILOR SHOPS) ===================

@bookings_bp.route('/bookings/measurements', methods=['GET'])
@jwt_required()
def get_measurement_bookings():
    """
    Get all measurement bookings for the authenticated tailor shop
    """
    try:
        user_id = ObjectId(get_jwt_identity())
        
        # Get filter parameters
        status = request.args.get('status', 'all')
        days = int(request.args.get('days', 30))
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Build query
        query = {'business_id': user_id}
        
        if status != 'all':
            query['status'] = status
            
        # Date filter
        if days > 0:
            start_date = datetime.utcnow() - timedelta(days=days)
            query['created_at'] = {'$gte': start_date}
        
        # Get bookings with pagination
        skip = (page - 1) * limit
        bookings = list(mongo.db.measurement_bookings.find(query)
                       .sort('created_at', -1)
                       .skip(skip)
                       .limit(limit))
        
        # Convert ObjectId to string
        for booking in bookings:
            booking['_id'] = str(booking['_id'])
            booking['business_id'] = str(booking['business_id'])
        
        # Get total count
        total_count = mongo.db.measurement_bookings.count_documents(query)
        
        return jsonify({
            'success': True,
            'bookings': bookings,
            'pagination': {
                'current_page': page,
                'total_pages': (total_count + limit - 1) // limit,
                'total_items': total_count,
                'has_next': page * limit < total_count,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching measurement bookings: {str(e)}'
        }), 500

@bookings_bp.route('/bookings/measurements/<booking_id>', methods=['PUT'])
@jwt_required()
def update_measurement_booking(booking_id):
    """
    Update measurement booking status and details
    """
    try:
        user_id = ObjectId(get_jwt_identity())
        data = request.get_json()
        
        # Verify booking belongs to user
        booking = mongo.db.measurement_bookings.find_one({
            '_id': ObjectId(booking_id),
            'business_id': user_id
        })
        
        if not booking:
            return jsonify({
                'success': False,
                'message': 'Booking not found'
            }), 404
        
        # Prepare update data
        update_data = {
            'updated_at': datetime.utcnow()
        }
        
        # Update allowed fields
        allowed_fields = ['status', 'notes', 'confirmed_date', 'confirmed_time', 'tailor_assigned', 'appointment_confirmed']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        # Mark as read
        if data.get('mark_as_read'):
            update_data['is_read'] = True
        
        # Update booking
        mongo.db.measurement_bookings.update_one(
            {'_id': ObjectId(booking_id)},
            {'$set': update_data}
        )
        
        return jsonify({
            'success': True,
            'message': 'Booking updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating booking: {str(e)}'
        }), 500

# =================== ORDER INQUIRIES ===================

@bookings_bp.route('/inquiries/orders', methods=['GET'])
@jwt_required()
def get_order_inquiries():
    """
    Get all order inquiries for the authenticated business
    """
    try:
        user_id = ObjectId(get_jwt_identity())
        
        # Get filter parameters
        status = request.args.get('status', 'all')
        days = int(request.args.get('days', 30))
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Build query
        query = {'business_id': user_id}
        
        if status != 'all':
            query['status'] = status
            
        # Date filter
        if days > 0:
            start_date = datetime.utcnow() - timedelta(days=days)
            query['created_at'] = {'$gte': start_date}
        
        # Get inquiries with pagination
        skip = (page - 1) * limit
        inquiries = list(mongo.db.order_inquiries.find(query)
                        .sort('created_at', -1)
                        .skip(skip)
                        .limit(limit))
        
        # Convert ObjectId to string
        for inquiry in inquiries:
            inquiry['_id'] = str(inquiry['_id'])
            inquiry['business_id'] = str(inquiry['business_id'])
        
        # Get total count
        total_count = mongo.db.order_inquiries.count_documents(query)
        
        return jsonify({
            'success': True,
            'inquiries': inquiries,
            'pagination': {
                'current_page': page,
                'total_pages': (total_count + limit - 1) // limit,
                'total_items': total_count,
                'has_next': page * limit < total_count,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching order inquiries: {str(e)}'
        }), 500

@bookings_bp.route('/inquiries/orders/<inquiry_id>', methods=['PUT'])
@jwt_required()
def update_order_inquiry(inquiry_id):
    """
    Update order inquiry status and details
    """
    try:
        user_id = ObjectId(get_jwt_identity())
        data = request.get_json()
        
        # Verify inquiry belongs to user
        inquiry = mongo.db.order_inquiries.find_one({
            '_id': ObjectId(inquiry_id),
            'business_id': user_id
        })
        
        if not inquiry:
            return jsonify({
                'success': False,
                'message': 'Inquiry not found'
            }), 404
        
        # Prepare update data
        update_data = {
            'updated_at': datetime.utcnow()
        }
        
        # Update allowed fields
        allowed_fields = ['status', 'notes', 'quote_amount', 'quoted_delivery_date', 'assigned_to']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        # Mark as read
        if data.get('mark_as_read'):
            update_data['is_read'] = True
        
        # Update inquiry
        mongo.db.order_inquiries.update_one(
            {'_id': ObjectId(inquiry_id)},
            {'$set': update_data}
        )
        
        return jsonify({
            'success': True,
            'message': 'Inquiry updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating inquiry: {str(e)}'
        }), 500

# =================== CONTACT MESSAGES ===================

@bookings_bp.route('/messages/contact', methods=['GET'])
@jwt_required()
def get_contact_messages():
    """
    Get all contact messages for the authenticated business
    """
    try:
        user_id = ObjectId(get_jwt_identity())
        
        # Get filter parameters
        days = int(request.args.get('days', 30))
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        message_type = request.args.get('type', 'all')
        
        # Build query for both contact message collections
        query = {'business_id': user_id}
        
        # Date filter
        if days > 0:
            start_date = datetime.utcnow() - timedelta(days=days)
            query['created_at'] = {'$gte': start_date}
        
        # Get messages from both collections
        skip = (page - 1) * limit
        
        # Contact messages
        contact_messages = list(mongo.db.contact_messages.find(query)
                               .sort('created_at', -1)
                               .skip(skip)
                               .limit(limit))
        
        # Client messages (for law firms)
        client_messages = list(mongo.db.client_messages.find(query)
                              .sort('created_at', -1)
                              .skip(skip)
                              .limit(limit))
        
        # Combine and sort messages
        all_messages = contact_messages + client_messages
        all_messages.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Take only the limit
        all_messages = all_messages[:limit]
        
        # Convert ObjectId to string
        for message in all_messages:
            message['_id'] = str(message['_id'])
            message['business_id'] = str(message['business_id'])
        
        # Get total count
        total_contact = mongo.db.contact_messages.count_documents(query)
        total_client = mongo.db.client_messages.count_documents(query)
        total_count = total_contact + total_client
        
        return jsonify({
            'success': True,
            'messages': all_messages,
            'pagination': {
                'current_page': page,
                'total_pages': (total_count + limit - 1) // limit,
                'total_items': total_count,
                'has_next': page * limit < total_count,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching contact messages: {str(e)}'
        }), 500

@bookings_bp.route('/messages/contact/<message_id>', methods=['PUT'])
@jwt_required()
def update_contact_message(message_id):
    """
    Update contact message status
    """
    try:
        user_id = ObjectId(get_jwt_identity())
        data = request.get_json()
        
        # Try to find in contact_messages first
        message = mongo.db.contact_messages.find_one({
            '_id': ObjectId(message_id),
            'business_id': user_id
        })
        
        collection = 'contact_messages'
        
        # If not found, try client_messages
        if not message:
            message = mongo.db.client_messages.find_one({
                '_id': ObjectId(message_id),
                'business_id': user_id
            })
            collection = 'client_messages'
        
        if not message:
            return jsonify({
                'success': False,
                'message': 'Message not found'
            }), 404
        
        # Prepare update data
        update_data = {}
        
        # Update allowed fields
        allowed_fields = ['status', 'is_read', 'notes', 'priority']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        # Update message in the correct collection
        if collection == 'contact_messages':
            mongo.db.contact_messages.update_one(
                {'_id': ObjectId(message_id)},
                {'$set': update_data}
            )
        else:
            mongo.db.client_messages.update_one(
                {'_id': ObjectId(message_id)},
                {'$set': update_data}
            )
        
        return jsonify({
            'success': True,
            'message': 'Message updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating message: {str(e)}'
        }), 500

# =================== DASHBOARD STATS ===================

@bookings_bp.route('/bookings/stats', methods=['GET'])
@jwt_required()
def get_booking_stats():
    """
    Get booking and inquiry statistics for dashboard
    """
    try:
        user_id = ObjectId(get_jwt_identity())
        days = int(request.args.get('days', 30))
        
        # Date filter
        start_date = datetime.utcnow() - timedelta(days=days)
        date_query = {'created_at': {'$gte': start_date}}
        
        # Base query
        base_query = {'business_id': user_id}
        query_with_date = {**base_query, **date_query}
        
        # Get consultation bookings stats
        consultation_stats = {
            'total': mongo.db.consultation_bookings.count_documents(base_query),
            'recent': mongo.db.consultation_bookings.count_documents(query_with_date),
            'pending': mongo.db.consultation_bookings.count_documents({**base_query, 'status': 'pending'}),
            'confirmed': mongo.db.consultation_bookings.count_documents({**base_query, 'status': 'confirmed'}),
            'unread': mongo.db.consultation_bookings.count_documents({**base_query, 'is_read': False})
        }
        
        # Get measurement bookings stats
        measurement_stats = {
            'total': mongo.db.measurement_bookings.count_documents(base_query),
            'recent': mongo.db.measurement_bookings.count_documents(query_with_date),
            'pending': mongo.db.measurement_bookings.count_documents({**base_query, 'status': 'pending'}),
            'confirmed': mongo.db.measurement_bookings.count_documents({**base_query, 'status': 'confirmed'}),
            'unread': mongo.db.measurement_bookings.count_documents({**base_query, 'is_read': False})
        }
        
        # Get order inquiries stats
        order_stats = {
            'total': mongo.db.order_inquiries.count_documents(base_query),
            'recent': mongo.db.order_inquiries.count_documents(query_with_date),
            'new': mongo.db.order_inquiries.count_documents({**base_query, 'status': 'new'}),
            'quoted': mongo.db.order_inquiries.count_documents({**base_query, 'status': 'quoted'}),
            'unread': mongo.db.order_inquiries.count_documents({**base_query, 'is_read': False})
        }
        
        # Get message stats
        contact_count = mongo.db.contact_messages.count_documents(base_query)
        client_count = mongo.db.client_messages.count_documents(base_query)
        contact_recent = mongo.db.contact_messages.count_documents(query_with_date)
        client_recent = mongo.db.client_messages.count_documents(query_with_date)
        contact_unread = mongo.db.contact_messages.count_documents({**base_query, 'is_read': False})
        client_unread = mongo.db.client_messages.count_documents({**base_query, 'is_read': False})
        
        message_stats = {
            'total': contact_count + client_count,
            'recent': contact_recent + client_recent,
            'unread': contact_unread + client_unread
        }
        
        return jsonify({
            'success': True,
            'stats': {
                'consultations': consultation_stats,
                'measurements': measurement_stats,
                'orders': order_stats,
                'messages': message_stats,
                'period_days': days
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching booking stats: {str(e)}'
        }), 500