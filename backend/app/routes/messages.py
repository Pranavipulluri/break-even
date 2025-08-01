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
        
        skip = (page - 1) * per_page
        
        messages = list(mongo.db.messages.find({
            'recipient_id': ObjectId(current_user_id)
        }).sort('created_at', -1).skip(skip).limit(per_page))
        
        total = mongo.db.messages.count_documents({
            'recipient_id': ObjectId(current_user_id)
        })
        
        # Convert ObjectId to string
        for message in messages:
            message['_id'] = str(message['_id'])
            message['recipient_id'] = str(message['recipient_id'])
            if 'sender_id' in message:
                message['sender_id'] = str(message['sender_id'])
        
        return jsonify({
            'messages': messages,
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
        
        # Check if message exists and belongs to current user
        message = mongo.db.messages.find_one({
            '_id': ObjectId(message_id),
            'recipient_id': ObjectId(current_user_id)
        })
        
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        
        # Update message with reply
        mongo.db.messages.update_one(
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
            user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
            email_service.send_message_reply(
                message['customer_email'],
                message['customer_name'],
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
        
        # Update message status
        result = mongo.db.messages.update_one(
            {
                '_id': ObjectId(message_id),
                'recipient_id': ObjectId(current_user_id)
            },
            {
                '$set': {
                    'is_read': True,
                    'read_at': datetime.utcnow()
                }
            }
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
        
        count = mongo.db.messages.count_documents({
            'recipient_id': ObjectId(current_user_id),
            'is_read': False
        })
        
        return jsonify({'unreadCount': count}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
