
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.services.qr_service import QRService
from bson import ObjectId
import io

qr_bp = Blueprint('qr', _name_)

@qr_bp.route('/qr-code', methods=['GET'])
@jwt_required()
def get_qr_code():
    try:
        current_user_id = get_jwt_identity()
        
        # Get user's website URL
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        website_url = f"{current_app.config['WEBSITE_BASE_URL']}/{user.get('business_name', current_user_id)}"
       # Get QR analytics
        qr_analytics = mongo.db.qr_analytics.find_one({'user_id': ObjectId(current_user_id)})
        if not qr_analytics:
            qr_analytics = {
                'user_id': ObjectId(current_user_id),
                'total_scans': 0,
                'scans_today': 0,
                'last_scan': None,
                'created_at': datetime.utcnow()
            }
            mongo.db.qr_analytics.insert_one(qr_analytics)
        
        return jsonify({
            'websiteUrl': website_url,
            'totalScans': qr_analytics.get('total_scans', 0),
            'scansToday': qr_analytics.get('scans_today', 0),
            'lastScan': qr_analytics.get('last_scan')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@qr_bp.route('/qr-code/generate', methods=['POST'])
@jwt_required()
def generate_qr_code():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        size = data.get('size', 256)
        format = data.get('format', 'PNG')
        
        # Get user's website URL
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        website_url = f"{current_app.config['WEBSITE_BASE_URL']}/{user.get('business_name', current_user_id)}"
        
        # Generate QR code
        qr_service = QRService()
        qr_image = qr_service.generate_qr_code(website_url, size)
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        qr_image.save(img_bytes, format=format)
        img_bytes.seek(0)
        
        return send_file(
            img_bytes,
            mimetype=f'image/{format.lower()}',
            as_attachment=True,
            download_name=f'qr-code.{format.lower()}'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qr_bp.route('/qr-code/scan', methods=['POST'])
def track_qr_scan():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        # Update scan analytics
        from datetime import datetime, date
        today = date.today()
        
        mongo.db.qr_analytics.update_one(
            {'user_id': ObjectId(user_id)},
            {
                '$inc': {'total_scans': 1},
                '$set': {'last_scan': datetime.utcnow()},
                '$inc': {'scans_today': 1} if mongo.db.qr_analytics.find_one({
                    'user_id': ObjectId(user_id),
                    'last_scan_date': today
                }) else '$set': {'scans_today': 1, 'last_scan_date': today}
            },
            upsert=True
        )
        
        return jsonify({'message': 'Scan tracked successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

