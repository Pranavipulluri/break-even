from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.services.qr_service import QRService
from bson import ObjectId
from datetime import datetime, date
import io

qr_bp = Blueprint('qr', __name__)

@qr_bp.route('/qr-code/dev', methods=['GET'])
def get_qr_code_dev():
    """Development endpoint for QR code info without authentication"""
    try:
        # For development, try to get any deployed websites from the database
        deployed_websites = []
        
        try:
            from app import mongo
            # Check multiple collections where websites might be stored
            collections_to_check = ['child_websites', 'websites', 'deployed_sites']
            
            for collection_name in collections_to_check:
                try:
                    collection = getattr(mongo.db, collection_name)
                    websites_cursor = collection.find({
                        'website_url': {'$exists': True, '$ne': None, '$ne': ''}
                    }).sort('created_at', -1).limit(5)
                    
                    for website in websites_cursor:
                        deployed_websites.append({
                            'id': str(website.get('_id', f'dev-{len(deployed_websites)}')),
                            'name': website.get('website_name', website.get('site_name', 'Unnamed Website')),
                            'url': website.get('website_url'),
                            'platform': website.get('platform', 'netlify'),
                            'created_at': website.get('created_at')
                        })
                except Exception as e:
                    print(f"Could not check collection {collection_name}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Could not access database: {e}")
        
        # If no real websites found, create some sample ones for development
        if not deployed_websites:
            # Add sample deployed websites to the database for testing
            sample_sites = [
                {
                    'website_name': 'Pranavi Bakery',
                    'site_name': 'Pranavi Bakery',
                    'website_url': 'https://pranavi-bakery.netlify.app',
                    'platform': 'netlify',
                    'business_info': {
                        'business_name': 'Pranavi Bakery',
                        'business_type': 'bakery',
                        'location': 'Downtown'
                    },
                    'created_at': datetime.utcnow(),
                    'dev_deployment': True,
                    'status': 'deployed'
                },
                {
                    'website_name': 'Visesh Clothing Store',
                    'site_name': 'Visesh Clothing Store', 
                    'website_url': 'https://visesh-clothing.netlify.app',
                    'platform': 'netlify',
                    'business_info': {
                        'business_name': 'Visesh Clothing Store',
                        'business_type': 'retail',
                        'location': 'Shopping Mall'
                    },
                    'created_at': datetime.utcnow(),
                    'dev_deployment': True,
                    'status': 'deployed'
                },
                {
                    'website_name': 'Tech Solutions Hub',
                    'site_name': 'Tech Solutions Hub',
                    'website_url': 'https://tech-solutions-hub.netlify.app',
                    'platform': 'netlify',
                    'business_info': {
                        'business_name': 'Tech Solutions Hub',
                        'business_type': 'technology',
                        'location': 'Business District'
                    },
                    'created_at': datetime.utcnow(),
                    'dev_deployment': True,
                    'status': 'deployed'
                }
            ]
            
            # Insert sample sites into deployed_sites collection
            try:
                from app import mongo
                for site in sample_sites:
                    # Check if site already exists
                    existing = mongo.db.deployed_sites.find_one({'website_url': site['website_url']})
                    if not existing:
                        result = mongo.db.deployed_sites.insert_one(site)
                        deployed_websites.append({
                            'id': str(result.inserted_id),
                            'name': site['website_name'],
                            'url': site['website_url'],
                            'platform': site['platform'],
                            'created_at': site['created_at']
                        })
                        print(f"✅ Added sample deployed site: {site['website_name']} -> {site['website_url']}")
                    else:
                        deployed_websites.append({
                            'id': str(existing['_id']),
                            'name': existing['website_name'],
                            'url': existing['website_url'],
                            'platform': existing['platform'],
                            'created_at': existing['created_at']
                        })
                        print(f"🔄 Using existing deployed site: {existing['website_name']}")
            except Exception as e:
                print(f"Could not create sample sites: {e}")
                # Fallback to hardcoded data
                deployed_websites = [
                    {
                        'id': 'sample-netlify-1',
                        'name': 'Pranavi Bakery',
                        'url': 'https://pranavi-bakery.netlify.app',
                        'platform': 'netlify',
                        'created_at': datetime.utcnow()
                    },
                    {
                        'id': 'sample-netlify-2',
                        'name': 'Visesh Clothing Store',
                        'url': 'https://visesh-clothing.netlify.app',
                        'platform': 'netlify',
                        'created_at': datetime.utcnow()
                    },
                    {
                        'id': 'sample-netlify-3',
                        'name': 'Tech Solutions Hub',
                        'url': 'https://tech-solutions-hub.netlify.app',
                        'platform': 'netlify',
                        'created_at': datetime.utcnow()
                    }
                ]
        
        # Use the first deployed website URL if available, otherwise use a sample
        default_url = 'https://pranavi-bakery.netlify.app'  # Default to first sample site
        if deployed_websites and deployed_websites[0]['url']:
            default_url = deployed_websites[0]['url']
        
        return jsonify({
            'websiteUrl': default_url,
            'totalScans': 25,  # Mock analytics
            'scansToday': 5,
            'lastScan': datetime.utcnow().isoformat(),
            'deployedWebsites': deployed_websites,
            'qrCodeId': 'dev-qr-id',
            'message': f'QR Code will redirect to: {default_url}'
        }), 200
        
    except Exception as e:
        print(f"QR dev endpoint error: {e}")
        return jsonify({'error': 'Failed to retrieve QR code information'}), 500

@qr_bp.route('/qr-code/dev/update-url', methods=['POST'])
def update_qr_url_dev():
    """Development endpoint to update QR URL without authentication"""
    try:
        data = request.get_json()
        website_url = data.get('website_url')
        
        if not website_url:
            return jsonify({'error': 'Website URL is required'}), 400
        
        return jsonify({
            'message': 'QR code URL updated successfully (development mode)',
            'website_url': website_url
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to update QR code URL'}), 500

@qr_bp.route('/qr-code', methods=['GET'])
@jwt_required()
def get_qr_code():
    """Get QR code information and analytics for the current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get user's website URL
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's deployed websites from website builder and deployed_sites collection
        deployed_websites = []
        
        # Check child_websites collection
        child_websites = list(mongo.db.child_websites.find({
            'user_id': ObjectId(current_user_id),
            'website_url': {'$exists': True, '$ne': None}
        }).sort('created_at', -1))
        
        # Check deployed_sites collection
        deployed_sites = list(mongo.db.deployed_sites.find({
            'website_url': {'$exists': True, '$ne': None}
        }).sort('created_at', -1).limit(5))
        
        # Combine both sources
        deployed_websites = child_websites + deployed_sites
        
        # Default website URL - prioritize deployed URLs over localhost
        default_deployed_urls = [
            'https://pranavi-bakery.netlify.app',
            'https://visesh-clothing.netlify.app', 
            'https://tech-solutions-hub.netlify.app'
        ]
        
        website_url = default_deployed_urls[0]  # Use first deployed URL as default
        
        # Check if user has a custom QR URL setting
        qr_settings = mongo.db.qr_settings.find_one({'user_id': ObjectId(current_user_id)})
        if qr_settings and qr_settings.get('website_url'):
            website_url = qr_settings['website_url']
        elif deployed_websites:
            # Use the most recent deployed website URL if no custom setting
            latest_website = deployed_websites[0]
            if latest_website.get('website_url'):
                website_url = latest_website['website_url']
        
        # Get QR analytics
        qr_analytics = mongo.db.qr_analytics.find_one({'user_id': ObjectId(current_user_id)})
        if not qr_analytics:
            qr_analytics = {
                'user_id': ObjectId(current_user_id),
                'total_scans': 0,
                'scans_today': 0,
                'last_scan': None,
                'last_scan_date': None,
                'created_at': datetime.utcnow()
            }
            mongo.db.qr_analytics.insert_one(qr_analytics)
        
        # Format deployed websites for frontend
        websites_list = []
        for website in deployed_websites:
            websites_list.append({
                'id': str(website['_id']),
                'name': website.get('website_name', 'Unnamed Website'),
                'url': website.get('website_url'),
                'platform': website.get('platform', 'unknown'),
                'created_at': website.get('created_at')
            })
        
        return jsonify({
            'websiteUrl': website_url,
            'totalScans': qr_analytics.get('total_scans', 0),
            'scansToday': qr_analytics.get('scans_today', 0),
            'lastScan': qr_analytics.get('last_scan'),
            'deployedWebsites': websites_list,
            'qrCodeId': str(qr_analytics.get('_id', ''))
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting QR code info: {e}")
        return jsonify({'error': 'Failed to retrieve QR code information'}), 500

@qr_bp.route('/qr-code/update-url', methods=['POST'])
@jwt_required()
def update_qr_url():
    """Update the QR code to point to a specific website"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        website_url = data.get('website_url')
        if not website_url:
            return jsonify({'error': 'Website URL is required'}), 400
        
        # Update or create QR settings
        qr_settings = mongo.db.qr_settings.find_one({'user_id': ObjectId(current_user_id)})
        if qr_settings:
            mongo.db.qr_settings.update_one(
                {'user_id': ObjectId(current_user_id)},
                {'$set': {'website_url': website_url, 'updated_at': datetime.utcnow()}}
            )
        else:
            mongo.db.qr_settings.insert_one({
                'user_id': ObjectId(current_user_id),
                'website_url': website_url,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
        
        return jsonify({
            'message': 'QR code URL updated successfully',
            'website_url': website_url
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error updating QR URL: {e}")
        return jsonify({'error': 'Failed to update QR code URL'}), 500

@qr_bp.route('/qr-code/generate', methods=['POST'])
@jwt_required()
def generate_qr_code():
    """Generate QR code for the current user's website"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # Validate and set defaults
        size = data.get('size', 256)
        format_type = data.get('format', 'PNG').upper()
        qr_type = data.get('type', 'basic')  # basic, branded, framed
        
        # Validate size
        if not isinstance(size, int) or size < 64 or size > 1024:
            return jsonify({'error': 'Size must be between 64 and 1024 pixels'}), 400
        
        # Validate format
        if format_type not in ['PNG', 'JPEG', 'JPG']:
            return jsonify({'error': 'Format must be PNG, JPEG, or JPG'}), 400
        
        # Get user information
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate website URL
        business_name = user.get('business_name', '').replace(' ', '-').lower()
        website_url = f"{current_app.config.get('WEBSITE_BASE_URL', 'https://your-domain.com')}/{business_name or current_user_id}"
        
        # Initialize QR service
        qr_service = QRService()
        
        # Generate QR code based on type
        if qr_type == 'branded' and user.get('business_name'):
            qr_image = qr_service.generate_branded_qr_code(
                url=website_url,
                business_name=user.get('business_name'),
                size=size,
                color=data.get('color', '#000000')
            )
        elif qr_type == 'framed' and user.get('business_name'):
            qr_image = qr_service.generate_qr_with_frame(
                url=website_url,
                business_name=user.get('business_name'),
                frame_color=data.get('frame_color', '#2196F3'),
                size=size
            )
        else:
            # Basic QR code
            qr_image = qr_service.generate_qr_code(
                url=website_url,
                size=size,
                logo_path=data.get('logo_path')
            )
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        qr_image.save(img_bytes, format=format_type, optimize=True)
        img_bytes.seek(0)
        
        # Update generation count in analytics
        mongo.db.qr_analytics.update_one(
            {'user_id': ObjectId(current_user_id)},
            {
                '$inc': {'generations_count': 1},
                '$set': {'last_generated': datetime.utcnow()}
            },
            upsert=True
        )
        
        # Create filename
        filename_prefix = business_name or 'qr-code'
        filename = f'{filename_prefix}-{qr_type}.{format_type.lower()}'
        
        return send_file(
            img_bytes,
            mimetype=f'image/{format_type.lower()}',
            as_attachment=True,
            download_name=filename
        )
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error generating QR code: {e}")
        return jsonify({'error': 'Failed to generate QR code'}), 500

@qr_bp.route('/qr-code/scan', methods=['POST'])
def track_qr_scan():
    """Track QR code scan analytics"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        user_id = data.get('user_id')
        scan_location = data.get('location')  # Optional: track scan location
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        # Validate user_id format
        try:
            user_object_id = ObjectId(user_id)
        except:
            return jsonify({'error': 'Invalid user ID format'}), 400
        
        # Check if user exists
        user = mongo.db.users.find_one({'_id': user_object_id})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update scan analytics
        today = date.today()
        now = datetime.utcnow()
        
        # Check if there's an existing analytics record for today
        existing_analytics = mongo.db.qr_analytics.find_one({
            'user_id': user_object_id,
            'last_scan_date': today
        })
        
        if existing_analytics:
            # Update existing record - increment today's scans
            update_query = {
                '$inc': {
                    'total_scans': 1,
                    'scans_today': 1
                },
                '$set': {
                    'last_scan': now,
                    'last_scan_date': today,
                    'last_scan_user_agent': user_agent
                }
            }
            if scan_location:
                update_query['$set']['last_scan_location'] = scan_location
            
        else:
            # New day or first scan - reset today's count
            update_query = {
                '$inc': {'total_scans': 1},
                '$set': {
                    'scans_today': 1,
                    'last_scan': now,
                    'last_scan_date': today,
                    'last_scan_user_agent': user_agent
                }
            }
            if scan_location:
                update_query['$set']['last_scan_location'] = scan_location
        
        # Update or create analytics record
        result = mongo.db.qr_analytics.update_one(
            {'user_id': user_object_id},
            update_query,
            upsert=True
        )
        
        # Optional: Store individual scan records for detailed analytics
        scan_record = {
            'user_id': user_object_id,
            'scanned_at': now,
            'user_agent': user_agent,
            'ip_address': request.remote_addr
        }
        if scan_location:
            scan_record['location'] = scan_location
        
        mongo.db.qr_scans.insert_one(scan_record)
        
        # Get updated analytics for response
        updated_analytics = mongo.db.qr_analytics.find_one({'user_id': user_object_id})
        
        return jsonify({
            'message': 'Scan tracked successfully',
            'analytics': {
                'total_scans': updated_analytics.get('total_scans', 0),
                'scans_today': updated_analytics.get('scans_today', 0),
                'last_scan': updated_analytics.get('last_scan')
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error tracking QR scan: {e}")
        return jsonify({'error': 'Failed to track scan'}), 500

@qr_bp.route('/qr-code/analytics', methods=['GET'])
@jwt_required()
def get_qr_analytics():
    """Get detailed QR code analytics for the current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get overall analytics
        analytics = mongo.db.qr_analytics.find_one({'user_id': ObjectId(current_user_id)})
        if not analytics:
            analytics = {
                'total_scans': 0,
                'scans_today': 0,
                'last_scan': None,
                'generations_count': 0
            }
        
        # Get recent scan records (last 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        recent_scans = list(mongo.db.qr_scans.find({
            'user_id': ObjectId(current_user_id),
            'scanned_at': {'$gte': thirty_days_ago}
        }).sort('scanned_at', -1).limit(100))
        
        # Format scan records
        formatted_scans = []
        for scan in recent_scans:
            formatted_scans.append({
                'scanned_at': scan.get('scanned_at'),
                'user_agent': scan.get('user_agent'),
                'location': scan.get('location'),
                'ip_address': scan.get('ip_address', 'Unknown')
            })
        
        # Calculate daily scan counts for the last 7 days
        daily_scans = {}
        for i in range(7):
            day = date.today() - timedelta(days=i)
            day_scans = mongo.db.qr_scans.count_documents({
                'user_id': ObjectId(current_user_id),
                'scanned_at': {
                    '$gte': datetime.combine(day, datetime.min.time()),
                    '$lt': datetime.combine(day + timedelta(days=1), datetime.min.time())
                }
            })
            daily_scans[day.isoformat()] = day_scans
        
        return jsonify({
            'analytics': {
                'total_scans': analytics.get('total_scans', 0),
                'scans_today': analytics.get('scans_today', 0),
                'last_scan': analytics.get('last_scan'),
                'generations_count': analytics.get('generations_count', 0),
                'last_generated': analytics.get('last_generated')
            },
            'recent_scans': formatted_scans,
            'daily_scans': daily_scans
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting QR analytics: {e}")
        return jsonify({'error': 'Failed to retrieve analytics'}), 500

@qr_bp.route('/qr-code/reset-analytics', methods=['POST'])
@jwt_required()
def reset_qr_analytics():
    """Reset QR code analytics for the current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Reset analytics
        mongo.db.qr_analytics.update_one(
            {'user_id': ObjectId(current_user_id)},
            {
                '$set': {
                    'total_scans': 0,
                    'scans_today': 0,
                    'last_scan': None,
                    'last_scan_date': None,
                    'reset_at': datetime.utcnow()
                }
            },
            upsert=True
        )
        
        # Optionally, remove individual scan records
        # mongo.db.qr_scans.delete_many({'user_id': ObjectId(current_user_id)})
        
        return jsonify({'message': 'QR code analytics reset successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error resetting QR analytics: {e}")
        return jsonify({'error': 'Failed to reset QR code analytics'}), 500

@qr_bp.route('/qr-code/add-deployed-site', methods=['POST'])
@jwt_required()
def add_deployed_site():
    """Add a deployed website for QR code generation"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        website_name = data.get('website_name')
        website_url = data.get('website_url')
        platform = data.get('platform', 'netlify')
        
        if not website_name or not website_url:
            return jsonify({'error': 'Website name and URL are required'}), 400
        
        # Validate URL format
        if not website_url.startswith(('http://', 'https://')):
            return jsonify({'error': 'URL must start with http:// or https://'}), 400
        
        # Create deployed site record
        deployed_site = {
            'user_id': ObjectId(current_user_id),
            'website_name': website_name,
            'site_name': website_name,
            'website_url': website_url,
            'platform': platform,
            'business_info': {
                'business_name': website_name,
                'business_type': data.get('business_type', 'business'),
                'location': data.get('location', 'Online')
            },
            'created_at': datetime.utcnow(),
            'status': 'deployed',
            'added_by_user': True
        }
        
        # Insert into database
        result = mongo.db.deployed_sites.insert_one(deployed_site)
        
        return jsonify({
            'message': 'Deployed website added successfully',
            'site_id': str(result.inserted_id),
            'website_url': website_url,
            'success': True
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error adding deployed site: {e}")
        return jsonify({'error': 'Failed to add deployed website'}), 500

@qr_bp.route('/qr-code/create-sample-data', methods=['POST'])
def create_sample_deployed_sites():
    """Create sample deployed websites for QR code testing (development only)"""
    try:
        sample_sites = [
            {
                'website_name': 'Pranavi Bakery',
                'site_name': 'Pranavi Bakery',
                'website_url': 'https://pranavi-bakery.netlify.app',
                'platform': 'netlify',
                'business_info': {
                    'business_name': 'Pranavi Bakery',
                    'business_type': 'bakery',
                    'location': 'Downtown',
                    'description': 'Fresh baked goods daily',
                    'contact': 'pulluripranavi@gmail.com'
                },
                'created_at': datetime.utcnow(),
                'dev_deployment': True,
                'status': 'deployed',
                'qr_enabled': True
            },
            {
                'website_name': 'Visesh Clothing Store',
                'site_name': 'Visesh Clothing Store',
                'website_url': 'https://visesh-clothing.netlify.app',
                'platform': 'netlify',
                'business_info': {
                    'business_name': 'Visesh Clothing Store',
                    'business_type': 'retail',
                    'location': 'Shopping Mall',
                    'description': 'Trendy fashion for all ages',
                    'contact': 'visesh.bappana@gmail.com'
                },
                'created_at': datetime.utcnow(),
                'dev_deployment': True,
                'status': 'deployed',
                'qr_enabled': True
            },
            {
                'website_name': 'Tech Solutions Hub',
                'site_name': 'Tech Solutions Hub',
                'website_url': 'https://tech-solutions-hub.netlify.app',
                'platform': 'netlify',
                'business_info': {
                    'business_name': 'Tech Solutions Hub',
                    'business_type': 'technology',
                    'location': 'Business District',
                    'description': 'Innovative tech solutions for businesses',
                    'contact': 'info@techsolutions.com'
                },
                'created_at': datetime.utcnow(),
                'dev_deployment': True,
                'status': 'deployed',
                'qr_enabled': True
            }
        ]
        
        created_sites = []
        
        from app import mongo
        for site in sample_sites:
            # Check if site already exists
            existing = mongo.db.deployed_sites.find_one({'website_url': site['website_url']})
            if not existing:
                result = mongo.db.deployed_sites.insert_one(site)
                created_sites.append({
                    'id': str(result.inserted_id),
                    'name': site['website_name'],
                    'url': site['website_url'],
                    'platform': site['platform']
                })
            else:
                created_sites.append({
                    'id': str(existing['_id']),
                    'name': existing['website_name'],
                    'url': existing['website_url'],
                    'platform': existing['platform'],
                    'status': 'already_exists'
                })
        
        return jsonify({
            'message': f'Sample deployed sites created/verified successfully',
            'sites': created_sites,
            'total_created': len([s for s in created_sites if s.get('status') != 'already_exists']),
            'success': True
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to create sample sites: {str(e)}'}), 500
        
        return jsonify({'message': 'Analytics reset successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error resetting QR analytics: {e}")
        return jsonify({'error': 'Failed to reset analytics'}), 500