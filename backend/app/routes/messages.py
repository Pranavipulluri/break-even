from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo, socketio
from app.models.message import Message
from app.services.email_service import EmailService
from bson import ObjectId
from datetime import datetime
from flask_socketio import emit

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    try:
        current_user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        msg_filter = request.args.get('filter', 'all')
        
        skip = (page - 1) * per_page
        biz_oid = ObjectId(current_user_id)
        
        # 1. Fetch from 'messages'
        db_messages = list(mongo.db.messages.find({'recipient_id': biz_oid}))
        
        # 2. Fetch from 'contact_messages'
        contact_messages = list(mongo.db.contact_messages.find({'business_id': biz_oid}))
        
        # 3. Fetch from 'client_messages'
        client_messages = list(mongo.db.client_messages.find({'business_id': biz_oid}))
        
        # Normalize and merge
        normalized = []
        
        for msg in db_messages:
            normalized.append({
                '_id': str(msg['_id']),
                'recipient_id': str(msg['recipient_id']),
                'customer_name': msg.get('customer_name', 'Anonymous'),
                'customer_email': msg.get('customer_email', ''),
                'customer_phone': msg.get('customer_phone', ''),
                'content': msg.get('content', ''),
                'created_at': msg.get('created_at'),
                'message_type': msg.get('message_type', 'inquiry'),
                'is_read': msg.get('is_read', False),
                'reply': msg.get('reply', ''),
                'reply_sent': bool(msg.get('reply', '')),
                'replied_at': msg.get('replied_at'),
                'status': msg.get('status', 'new')
            })
            
        for msg in contact_messages:
            cust_info = msg.get('customer_info', {}) or {}
            normalized.append({
                '_id': str(msg['_id']),
                'recipient_id': str(msg['business_id']),
                'customer_name': f"{cust_info.get('first_name', '')} {cust_info.get('last_name', '')}".strip() or "Anonymous",
                'customer_email': cust_info.get('email', ''),
                'customer_phone': cust_info.get('phone', ''),
                'content': msg.get('message', ''),
                'created_at': msg.get('created_at'),
                'message_type': 'contact_form',
                'is_read': msg.get('is_read', False),
                'reply': msg.get('reply', ''),
                'reply_sent': bool(msg.get('reply', '')),
                'replied_at': msg.get('replied_at'),
                'status': msg.get('status', 'new')
            })
            
        for msg in client_messages:
            cust_info = msg.get('customer_info', {}) or {}
            normalized.append({
                '_id': str(msg['_id']),
                'recipient_id': str(msg['business_id']),
                'customer_name': f"{cust_info.get('first_name', '')} {cust_info.get('last_name', '')}".strip() or "Anonymous",
                'customer_email': cust_info.get('email', ''),
                'customer_phone': cust_info.get('phone', ''),
                'content': msg.get('message', ''),
                'created_at': msg.get('created_at'),
                'message_type': 'contact_form',
                'is_read': msg.get('is_read', False),
                'reply': msg.get('reply', ''),
                'reply_sent': bool(msg.get('reply', '')),
                'replied_at': msg.get('replied_at'),
                'status': msg.get('status', 'new')
            })
            
        # Apply filter
        if msg_filter == 'unread':
            normalized = [m for m in normalized if not m['is_read']]
        elif msg_filter == 'replied':
            normalized = [m for m in normalized if m['reply_sent']]
            
        # Helper to parse and sort by date
        def get_date(item):
            dt = item.get('created_at')
            if isinstance(dt, datetime):
                return dt
            if isinstance(dt, str):
                try:
                    return datetime.fromisoformat(dt.replace('Z', '+00:00'))
                except Exception:
                    pass
            return datetime.min
            
        normalized.sort(key=get_date, reverse=True)
        
        # Paginate
        total = len(normalized)
        paginated = normalized[skip : skip + per_page]
        
        return jsonify({
            'messages': paginated,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/messages', methods=['POST'])
def create_message():
    """This endpoint is called from child websites"""
    try:
        data = request.get_json()
        
        required_fields = ['recipient_id', 'content', 'customer_name', 'customer_email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create message
        message = Message(
            recipient_id=data['recipient_id'],
            content=data['content'],
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data.get('customer_phone'),
            website_id=data.get('website_id'),
            message_type=data.get('message_type', 'inquiry')
        )
        
        # Insert into database
        result = mongo.db.messages.insert_one(message.to_dict())
        
        # Get the created message
        created_message = mongo.db.messages.find_one({'_id': result.inserted_id})
        created_message['_id'] = str(created_message['_id'])
        created_message['recipient_id'] = str(created_message['recipient_id'])
        
        # Send real-time notification via WebSocket
        socketio.emit('new_message', created_message, room=data['recipient_id'])
        
        # Send email notification to business owner
        try:
            user = mongo.db.users.find_one({'_id': ObjectId(data['recipient_id'])})
            if user:
                email_service = EmailService()
                email_service.send_new_message_notification(
                    user['email'],
                    user['name'],
                    data['customer_name'],
                    data['content']
                )
        except Exception as email_error:
            print(f"Failed to send email notification: {email_error}")
        
        return jsonify({
            'message': 'Message sent successfully',
            'data': created_message
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/messages/<message_id>/reply', methods=['POST'])
@jwt_required()
def reply_to_message(message_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Try messages first
        message = mongo.db.messages.find_one({
            '_id': ObjectId(message_id),
            'recipient_id': ObjectId(current_user_id)
        })
        collection_name = 'messages'
        
        if not message:
            message = mongo.db.contact_messages.find_one({
                '_id': ObjectId(message_id),
                'business_id': ObjectId(current_user_id)
            })
            collection_name = 'contact_messages'
            
        if not message:
            message = mongo.db.client_messages.find_one({
                '_id': ObjectId(message_id),
                'business_id': ObjectId(current_user_id)
            })
            collection_name = 'client_messages'
            
        if not message:
            return jsonify({'error': 'Message not found'}), 404
            
        # Update message with reply
        col = mongo.db[collection_name]
        col.update_one(
            {'_id': ObjectId(message_id)},
            {
                '$set': {
                    'reply': data['reply'],
                    'replied_at': datetime.utcnow(),
                    'status': 'replied'
                }
            }
        )
        
        # Send email reply to customer
        try:
            email_service = EmailService()
            # Map fields for email sending
            cust_email = message.get('customer_email')
            cust_name = message.get('customer_name')
            if not cust_email or not cust_name:
                cust_info = message.get('customer_info', {}) or {}
                cust_email = cust_email or cust_info.get('email')
                cust_name = cust_name or f"{cust_info.get('first_name', '')} {cust_info.get('last_name', '')}".strip() or "Valued Customer"
                
            user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
            email_service.send_message_reply(
                cust_email,
                cust_name,
                user['name'],
                user['business_name'],
                data['reply']
            )
        except Exception as email_error:
            print(f"Failed to send email reply: {email_error}")
            
        return jsonify({'message': 'Reply sent successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/messages/<message_id>/mark-read', methods=['PUT'])
@jwt_required()
def mark_message_read(message_id):
    try:
        current_user_id = get_jwt_identity()
        biz_oid = ObjectId(current_user_id)
        msg_oid = ObjectId(message_id)
        
        # Try messages first
        result = mongo.db.messages.update_one(
            {'_id': msg_oid, 'recipient_id': biz_oid},
            {'$set': {'is_read': True, 'read_at': datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            # Try contact_messages
            result = mongo.db.contact_messages.update_one(
                {'_id': msg_oid, 'business_id': biz_oid},
                {'$set': {'is_read': True, 'read_at': datetime.utcnow()}}
            )
            
        if result.matched_count == 0:
            # Try client_messages
            result = mongo.db.client_messages.update_one(
                {'_id': msg_oid, 'business_id': biz_oid},
                {'$set': {'is_read': True, 'read_at': datetime.utcnow()}}
            )
            
        if result.matched_count == 0:
            return jsonify({'error': 'Message not found'}), 404
            
        return jsonify({'message': 'Message marked as read'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/messages/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    try:
        current_user_id = get_jwt_identity()
        biz_oid = ObjectId(current_user_id)
        
        count_msg = mongo.db.messages.count_documents({
            'recipient_id': biz_oid,
            'is_read': False
        })
        
        count_contact = mongo.db.contact_messages.count_documents({
            'business_id': biz_oid,
            'is_read': False
        })
        
        count_client = mongo.db.client_messages.count_documents({
            'business_id': biz_oid,
            'is_read': False
        })
        
        total_count = count_msg + count_contact + count_client
        
        return jsonify({'unreadCount': total_count}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
