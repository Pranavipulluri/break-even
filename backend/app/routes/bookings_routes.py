from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.models.booking import Booking
from app.services.email_service import EmailService
from bson import ObjectId
from datetime import datetime, timedelta

bookings_routes_bp = Blueprint('bookings_routes', __name__)
email_service = EmailService()

@bookings_routes_bp.route('/bookings/create', methods=['POST'])
def create_booking():
    """Create a new booking from mini-site (no auth required)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['business_id', 'customer_name', 'customer_email', 
                          'customer_phone', 'service_type', 'date', 'time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create booking
        booking = Booking(
            business_id=data['business_id'],
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data['customer_phone'],
            service_type=data['service_type'],
            attorney_name=data.get('attorney_name', 'Staff'),
            date=data['date'],
            time=data['time'],
            notes=data.get('notes', '')
        )
        
        # Insert into database
        result = mongo.db.bookings.insert_one(booking.to_dict())
        booking_id = str(result.inserted_id)
        
        # Get business info for email
        business = mongo.db.child_websites.find_one({'_id': ObjectId(data['business_id'])})
        
        # Send confirmation email to customer
        try:
            email_service.send_booking_request_confirmation(booking, business)
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        # Notify business owner
        try:
            owner = mongo.db.users.find_one({'_id': business['owner_id']})
            if owner:
                email_service.send_new_booking_notification(booking, business, owner)
        except Exception as e:
            print(f"Owner notification failed: {e}")
        
        return jsonify({
            'message': 'Booking request submitted successfully',
            'booking_id': booking_id,
            'status': 'pending'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bookings_routes_bp.route('/bookings/business/<business_id>', methods=['GET'])
@jwt_required()
def get_business_bookings(business_id):
    """Get all bookings for a business"""
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
        attorney = request.args.get('attorney')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        # Build query
        query = {'business_id': ObjectId(business_id)}
        if status:
            query['status'] = status
        if attorney:
            query['attorney_name'] = attorney
        if date_from or date_to:
            query['date'] = {}
            if date_from:
                query['date']['$gte'] = datetime.fromisoformat(date_from)
            if date_to:
                query['date']['$lte'] = datetime.fromisoformat(date_to)
        
        # Get bookings
        bookings = list(mongo.db.bookings.find(query)
                       .sort('date', 1)
                       .skip(skip)
                       .limit(limit))
        
        # Convert ObjectIds to strings
        for booking in bookings:
            booking['_id'] = str(booking['_id'])
            booking['business_id'] = str(booking['business_id'])
            if isinstance(booking.get('date'), datetime):
                booking['date'] = booking['date'].isoformat()
        
        # Get total count
        total_count = mongo.db.bookings.count_documents(query)
        
        return jsonify({
            'bookings': bookings,
            'total': total_count,
            'limit': limit,
            'skip': skip
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bookings_routes_bp.route('/bookings/<booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    """Get booking details"""
    try:
        current_user_id = get_jwt_identity()
        
        booking = mongo.db.bookings.find_one({'_id': ObjectId(booking_id)})
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Verify business ownership
        business = mongo.db.child_websites.find_one({
            '_id': booking['business_id'],
            'owner_id': ObjectId(current_user_id)
        })
        
        if not business:
            return jsonify({'error': 'Unauthorized'}), 403
        
        booking['_id'] = str(booking['_id'])
        booking['business_id'] = str(booking['business_id'])
        if isinstance(booking.get('date'), datetime):
            booking['date'] = booking['date'].isoformat()
        
        return jsonify({'booking': booking}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bookings_routes_bp.route('/bookings/<booking_id>/confirm', methods=['PATCH'])
@jwt_required()
def confirm_booking(booking_id):
    """Confirm a booking"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get booking
        booking_data = mongo.db.bookings.find_one({'_id': ObjectId(booking_id)})
        if not booking_data:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Verify business ownership
        business = mongo.db.child_websites.find_one({
            '_id': booking_data['business_id'],
            'owner_id': ObjectId(current_user_id)
        })
        
        if not business:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Confirm booking
        booking = Booking.from_dict(booking_data)
        booking.confirm()
        
        # Update in database
        mongo.db.bookings.update_one(
            {'_id': ObjectId(booking_id)},
            {'$set': booking.to_dict()}
        )
        
        # Send confirmation email
        try:
            email_service.send_booking_confirmation(booking, business)
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        return jsonify({
            'message': 'Booking confirmed successfully',
            'status': 'confirmed'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bookings_routes_bp.route('/bookings/<booking_id>/cancel', methods=['PATCH'])
@jwt_required()
def cancel_booking(booking_id):
    """Cancel a booking"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get booking
        booking_data = mongo.db.bookings.find_one({'_id': ObjectId(booking_id)})
        if not booking_data:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Verify business ownership
        business = mongo.db.child_websites.find_one({
            '_id': booking_data['business_id'],
            'owner_id': ObjectId(current_user_id)
        })
        
        if not business:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Cancel booking
        booking = Booking.from_dict(booking_data)
        booking.cancel(reason=data.get('reason', ''))
        
        # Update in database
        mongo.db.bookings.update_one(
            {'_id': ObjectId(booking_id)},
            {'$set': booking.to_dict()}
        )
        
        # Send cancellation email
        try:
            email_service.send_booking_cancellation(booking, business)
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        return jsonify({
            'message': 'Booking cancelled successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bookings_routes_bp.route('/bookings/<booking_id>/complete', methods=['PATCH'])
@jwt_required()
def complete_booking(booking_id):
    """Mark booking as completed"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get booking
        booking_data = mongo.db.bookings.find_one({'_id': ObjectId(booking_id)})
        if not booking_data:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Verify business ownership
        business = mongo.db.child_websites.find_one({
            '_id': booking_data['business_id'],
            'owner_id': ObjectId(current_user_id)
        })
        
        if not business:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Complete booking
        booking = Booking.from_dict(booking_data)
        booking.complete()
        
        # Update in database
        mongo.db.bookings.update_one(
            {'_id': ObjectId(booking_id)},
            {'$set': booking.to_dict()}
        )
        
        return jsonify({
            'message': 'Booking marked as completed',
            'status': 'completed'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bookings_routes_bp.route('/bookings/stats/<business_id>', methods=['GET'])
@jwt_required()
def get_booking_stats(business_id):
    """Get booking statistics for a business"""
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
                'count': {'$sum': 1}
            }}
        ]
        
        stats = list(mongo.db.bookings.aggregate(pipeline))
        
        # Format stats
        result = {
            'total_bookings': 0,
            'pending': 0,
            'confirmed': 0,
            'completed': 0,
            'cancelled': 0
        }
        
        for stat in stats:
            status = stat['_id']
            count = stat['count']
            result['total_bookings'] += count
            result[status] = count
        
        # Get upcoming bookings
        upcoming = mongo.db.bookings.count_documents({
            'business_id': ObjectId(business_id),
            'date': {'$gte': datetime.utcnow()},
            'status': {'$in': ['pending', 'confirmed']}
        })
        result['upcoming'] = upcoming
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bookings_routes_bp.route('/bookings/available-slots/<business_id>', methods=['GET'])
def get_available_slots(business_id):
    """Get available time slots for booking"""
    try:
        date_str = request.args.get('date')
        attorney = request.args.get('attorney')
        
        if not date_str:
            return jsonify({'error': 'date parameter is required'}), 400
        
        date = datetime.fromisoformat(date_str)
        
        # Get business hours
        business = mongo.db.child_websites.find_one({'_id': ObjectId(business_id)})
        if not business:
            return jsonify({'error': 'Business not found'}), 404
        
        # Get existing bookings for the date
        query = {
            'business_id': ObjectId(business_id),
            'date': date,
            'status': {'$in': ['pending', 'confirmed']}
        }
        if attorney:
            query['attorney_name'] = attorney
        
        booked_slots = list(mongo.db.bookings.find(query, {'time': 1}))
        booked_times = [b['time'] for b in booked_slots]
        
        # Generate available slots (9 AM to 5 PM, 1-hour intervals)
        all_slots = []
        for hour in range(9, 17):
            time_str = f"{hour:02d}:00"
            if time_str not in booked_times:
                all_slots.append(time_str)
        
        return jsonify({
            'date': date_str,
            'available_slots': all_slots,
            'booked_slots': booked_times
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
