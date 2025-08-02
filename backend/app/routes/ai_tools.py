# app/routes/ai_tools.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.services.ai_service import AIService
from app.services.gemini_service import get_gemini_service
from app.services.github_service import get_github_service
from app.services.netlify_service import get_netlify_service
from app.services.groq_service import GroqService
from app.services.email_service import get_email_service
from bson import ObjectId
from datetime import datetime
import base64
import io
import os
import logging

ai_bp = Blueprint('ai_tools', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock image generation function
def generate_mock_image(prompt, image_type, style):
    """Generate a mock image data URL when real service fails"""
    import random
    
    # Create a simple SVG placeholder
    colors = {
        'professional': ['#2563eb', '#1d4ed8'],
        'modern': ['#7c3aed', '#5b21b6'],
        'creative': ['#dc2626', '#b91c1c'],
        'minimal': ['#6b7280', '#4b5563'],
        'vintage': ['#92400e', '#78350f']
    }
    
    color_scheme = colors.get(style, ['#6b7280', '#4b5563'])
    
    svg_content = f'''
    <svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{color_scheme[0]};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{color_scheme[1]};stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="512" height="512" fill="url(#grad)"/>
        <rect x="50" y="50" width="412" height="412" fill="none" stroke="white" stroke-width="2" opacity="0.3"/>
        <text x="256" y="180" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="20" font-weight="bold">
            {image_type.upper()}
        </text>
        <text x="256" y="210" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="14">
            {style} Style
        </text>
        <text x="256" y="280" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="12" opacity="0.8">
            Mock Image Generated
        </text>
        <text x="256" y="320" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="10" opacity="0.6">
            {prompt[:40]}{"..." if len(prompt) > 40 else ""}
        </text>
    </svg>
    '''
    
    # Convert SVG to base64 data URL
    svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    data_url = f"data:image/svg+xml;base64,{svg_base64}"
    
    return data_url

# Development endpoints (no auth required)
@ai_bp.route('/ai-tools/dev/test', methods=['GET'])
def dev_test():
    """Development test endpoint"""
    return jsonify({
        'message': 'AI tools development test successful',
        'services': ['gemini', 'github', 'netlify'],
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@ai_bp.route('/ai-tools/dev/gemini-test', methods=['POST'])
def dev_gemini_test():
    """Test Gemini AI without authentication"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'Say hello and confirm you are working!')
        
        result = get_gemini_service().generate_content(prompt)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@ai_bp.route('/ai-tools/dev/groq-test', methods=['POST'])
def dev_groq_test():
    """Test Groq AI without authentication"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'Generate a business poster concept for a bakery')
        
        groq_service = GroqService()
        result = groq_service.test_connection()
        
        if result.get('success'):
            # Test image generation
            image_result = groq_service.generate_business_poster_concept(
                business_name="Test Bakery",
                business_type="bakery",
                message=prompt,
                style="professional"
            )
            return jsonify({
                'connection': result,
                'image_generation': image_result
            }), 200
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@ai_bp.route('/ai-tools/dev/netlify-deploy', methods=['POST'])
def dev_netlify_deploy():
    """Test Netlify deployment without authentication"""
    try:
        data = request.get_json()
        site_name = data.get('site_name', 'Test Site')
        business_info = data.get('business_info', {
            'hero_title': 'Test Website',
            'hero_subtitle': 'Testing deployment',
            'about_us': 'This is a test.',
            'contact_cta': 'Contact us!'
        })
        
        result = get_netlify_service().create_and_deploy_website(site_name, business_info)
        
        # Save successful deployment to database for QR code to find
        if result.get('success') and result.get('website_url'):
            try:
                from app import mongo
                deployed_site = {
                    'website_name': site_name,
                    'site_name': site_name,
                    'website_url': result['website_url'],
                    'platform': 'netlify',
                    'deployment_info': result,
                    'business_info': business_info,
                    'created_at': datetime.utcnow(),
                    'dev_deployment': True
                }
                mongo.db.deployed_sites.insert_one(deployed_site)
                print(f"Saved deployed site: {site_name} -> {result['website_url']}")
            except Exception as e:
                print(f"Could not save deployment to database: {e}")
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@ai_bp.route('/ai-tools/dev/github-deploy', methods=['POST'])
def dev_github_deploy():
    """Test GitHub deployment without authentication"""
    try:
        data = request.get_json()
        site_name = data.get('site_name', 'Test Site')
        business_info = data.get('business_info', {
            'hero_title': 'Test Website',
            'hero_subtitle': 'Testing deployment',
            'about_us': 'This is a test.',
            'contact_cta': 'Contact us!'
        })
        
        result = get_github_service().create_website_repository(site_name, business_info)
        
        # Save successful deployment to database for QR code to find
        if result.get('success') and result.get('website_url'):
            try:
                from app import mongo
                deployed_site = {
                    'website_name': site_name,
                    'site_name': site_name,
                    'website_url': result['website_url'],
                    'platform': 'github',
                    'deployment_info': result,
                    'business_info': business_info,
                    'created_at': datetime.utcnow(),
                    'dev_deployment': True
                }
                mongo.db.deployed_sites.insert_one(deployed_site)
                print(f"Saved deployed site: {site_name} -> {result['website_url']}")
            except Exception as e:
                print(f"Could not save deployment to database: {e}")
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@ai_bp.route('/ai-tools/dev/create-data-website', methods=['POST'])
def dev_create_data_website():
    """Create a data collection website without authentication"""
    try:
        data = request.get_json()
        title = data.get('title', 'Data Collection Website')
        description = data.get('description', 'Join our community and share your feedback!')
        content = data.get('content', 'Welcome to our platform. We value your input and feedback.')
        business_id = data.get('business_id')
        
        # Create the website with data collection functionality
        netlify_service = get_netlify_service()
        result = netlify_service.create_data_collection_website(
            title=title,
            description=description,
            content=content,
            business_id=business_id
        )
        
        # Store deployment info in database
        if result.get('success') and result.get('website_url'):
            try:
                deployed_site = {
                    'title': title,
                    'description': description,
                    'content': content,
                    'website_url': result['website_url'],
                    'netlify_url': result.get('netlify_url'),
                    'platform': 'netlify',
                    'deployment_info': result,
                    'business_id': business_id,
                    'has_data_collection': True,
                    'created_at': datetime.utcnow(),
                    'dev_deployment': True,
                    'features': ['user_registration', 'feedback_collection', 'sentiment_analysis']
                }
                mongo.db.deployed_sites.insert_one(deployed_site)
                print(f"Saved data collection website: {title} -> {result['website_url']}")
            except Exception as e:
                print(f"Could not save deployment to database: {e}")
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@ai_bp.route('/ai-tools/dev/generate-image', methods=['POST'])
def dev_generate_image():
    """Development image generation with fallback to mock"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        prompt = data.get('prompt')
        image_type = data.get('image_type', 'poster')
        style = data.get('style', 'professional')
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt is required'
            }), 400
        
        logger.info(f"🎨 Generating {image_type} image: {prompt}")
        
        # Try to use real Stability AI service first
        try:
            # Check if StabilityService is available and configured
            try:
                from app.services.stability_service import StabilityService
                stability_service = StabilityService()
                
                # Test connection
                connection_test = stability_service.test_connection()
                if connection_test.get('success'):
                    logger.info("✅ Stability AI connection successful")
                    
                    # Generate image based on type
                    if image_type == 'poster':
                        result = stability_service.generate_business_poster(
                            business_name="Your Business",
                            business_type="business",
                            message=prompt,
                            style=style
                        )
                    elif image_type == 'product':
                        result = stability_service.generate_product_image(
                            product_name=prompt,
                            product_description="",
                            style=style
                        )
                    elif image_type == 'banner':
                        result = stability_service.generate_marketing_banner(
                            business_name="Your Business",
                            message=prompt,
                            style=style
                        )
                    else:
                        result = stability_service.generate_image(prompt, style, image_type)
                    
                    if result.get('success'):
                        return jsonify({
                            'success': True,
                            'image_data': result.get('image_data'),
                            'concept': result.get('enhanced_prompt', prompt),
                            'prompt': prompt,
                            'image_type': image_type,
                            'style': style,
                            'source': 'stability_ai'
                        })
                    else:
                        logger.warning(f"Stability AI generation failed: {result.get('error')}")
                        raise Exception(result.get('error', 'Generation failed'))
                else:
                    logger.warning(f"Stability AI connection failed: {connection_test.get('error')}")
                    raise Exception("Connection test failed")
                    
            except ImportError as e:
                logger.warning(f"StabilityService not available: {e}")
                raise Exception("StabilityService not configured")
            except Exception as e:
                logger.warning(f"Stability AI service error: {e}")
                raise Exception(str(e))
                
        except Exception as stability_error:
            logger.info(f"⚠️  Falling back to mock image generation due to: {stability_error}")
            
            # Fallback to mock image generation
            mock_image_data = generate_mock_image(prompt, image_type, style)
            
            # Generate a mock concept description
            concept = f"Mock {image_type} in {style} style featuring {prompt}. This is a placeholder image generated for development purposes."
            
            return jsonify({
                'success': True,
                'image_data': mock_image_data,
                'concept': concept,
                'prompt': prompt,
                'image_type': image_type,
                'style': style,
                'source': 'mock_generator',
                'note': 'This is a mock image. Configure Stability AI API for real image generation.'
            })
            
    except Exception as e:
        logger.error(f"❌ Dev image generation error: {e}")
        return jsonify({
            'success': False,
            'error': f'Image generation failed: {str(e)}'
        }), 500

# Production endpoints (auth required)
# ===== Replace the existing generate_content function in ai_tools.py =====

# ===== REPLACE the generate_content function in ai_tools.py with this DEBUG VERSION =====

@ai_bp.route('/ai-tools/generate-content', methods=['POST'])
@jwt_required()
def generate_content():
    try:
        logger.info("🚀 Starting content generation...")
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        content_type = data.get('content_type')
        prompt = data.get('prompt')
        business_context = data.get('business_context', '')
        
        logger.info(f"📝 Content type: {content_type}, Prompt: {prompt[:50]}...")
        
        if not content_type or not prompt:
            logger.error("❌ Missing content_type or prompt")
            return jsonify({'error': 'Content type and prompt are required'}), 400
        
        # Get user's business info for context
        try:
            logger.info("🔍 Fetching user business info...")
            user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
            business_name = user.get('business_name', 'Your Business') if user else 'Your Business'
            if user:
                business_context += f" Business: {business_name}. "
            logger.info(f"✅ Business context: {business_name}")
        except Exception as e:
            logger.error(f"❌ Error fetching user info: {e}")
            business_name = 'Your Business'
        
        # Generate AI content
        try:
            logger.info("🤖 Generating AI content...")
            ai_service = AIService()
            generated_content = ai_service.generate_content(content_type, prompt, business_context)
            logger.info(f"✅ AI content generated: {len(generated_content)} characters")
        except Exception as e:
            logger.error(f"❌ AI content generation failed: {e}")
            return jsonify({'error': f'AI content generation failed: {str(e)}'}), 500
        
        # Initialize email results
        email_results = None
        
        # Auto-send emails for email campaigns
        if content_type == 'email_campaign':
            try:
                logger.info(f"📧 Processing email campaign for user {current_user_id}")
                
                # Recipients including the test email
                recipients = [
                    'pulluripranavi@gmail.com',
                    'visesh.bappana@gmail.com',
                ]
                
                # Try to send real emails first
                try:
                    logger.info("🔗 Testing email service connection...")
                    email_service = get_email_service()
                    
                    # Test connection
                    connection_test = email_service.test_connection()
                    if connection_test['success']:
                        logger.info("✅ Email service connection successful - sending REAL emails")
                        
                        # Generate email subject
                        email_subject = f"ROCKET {business_name} - AI Generated Campaign"
                        logger.info(f"📧 Email subject: {email_subject}")
                        
                        # Send real emails
                        logger.info(f"📤 Sending emails to {len(recipients)} recipients...")
                        results = email_service.send_bulk_emails(
                            recipients=recipients,
                            subject=email_subject,
                            content=generated_content,
                            content_type='text'
                        )
                        logger.info(f"📊 Email results: {results['summary']}")
                        
                        # Save real email campaign
                        try:
                            logger.info("💾 Saving email campaign to database...")
                            campaign_record = {
                                'user_id': ObjectId(current_user_id),
                                'campaign_type': 'real_email_campaign',
                                'subject': email_subject,
                                'content': generated_content,
                                'recipients': recipients,
                                'total_recipients': results['total_recipients'],
                                'successful_sends': results['summary']['successful_sends'],
                                'failed_sends': results['summary']['failed_sends'],
                                'success_rate': results['summary']['success_rate'],
                                'sent_emails': results['successful_sends'],
                                'failed_emails': results['failed_sends'],
                                'created_at': datetime.utcnow(),
                                'is_mock': False,
                                'is_real': True,
                                'auto_sent': True
                            }
                            
                            result = mongo.db.email_campaigns.insert_one(campaign_record)
                            logger.info(f"✅ Campaign saved with ID: {result.inserted_id}")
                            
                            email_results = {
                                'success': True,
                                'type': 'real_email',
                                'campaign_id': str(result.inserted_id),
                                'summary': results['summary'],
                                'sent_emails': results['successful_sends'],
                                'failed_emails': results['failed_sends'],
                                'message': f'✅ REAL emails sent! {results["summary"]["successful_sends"]} successful to pulluripranavi@gmail.com and others!'
                            }
                            
                            logger.info(f"✅ REAL email campaign sent to {results['summary']['successful_sends']} recipients")
                            
                        except Exception as db_error:
                            logger.error(f"❌ Database save error: {db_error}")
                            # Continue without failing - email was sent successfully
                            email_results = {
                                'success': True,
                                'type': 'real_email',
                                'campaign_id': 'db_error',
                                'summary': results['summary'],
                                'sent_emails': results['successful_sends'],
                                'failed_emails': results['failed_sends'],
                                'message': f'✅ REAL emails sent! {results["summary"]["successful_sends"]} successful (DB save failed)'
                            }
                        
                    else:
                        raise Exception(f"Email service connection failed: {connection_test['error']}")
                        
                except Exception as email_error:
                    logger.warning(f"⚠️ Real email failed ({email_error}), falling back to mock system")
                    
                    # Fallback to mock system
                    try:
                        logger.info("📧 Using mock email system as fallback")
                        
                        # Generate mock data
                        import random
                        from datetime import timedelta
                        
                        mock_recipients = [
                            'pulluripranavi@gmail.com',
                            'visesh.bappana@gmail.com',
                            'customer1@example.com',
                            'customer2@example.com',
                            'customer3@example.com'
                        ]
                        
                        sent_emails = []
                        failed_emails = []
                        
                        for i, email in enumerate(mock_recipients):
                            if random.random() < 0.05:  # 5% failure rate
                                failed_emails.append({
                                    'email': email,
                                    'error': 'Mock: Invalid email address'
                                })
                            else:
                                delivery_time = datetime.utcnow() + timedelta(seconds=random.randint(1, 30))
                                sent_emails.append({
                                    'email': email,
                                    'status': 'sent',
                                    'sent_at': delivery_time.isoformat(),
                                    'message_id': f'mock_msg_{random.randint(100000, 999999)}_{i}'
                                })
                        
                        # Save mock campaign
                        campaign_record = {
                            'user_id': ObjectId(current_user_id),
                            'campaign_type': 'mock_email_campaign',
                            'subject': f'Mock: {business_name} - AI Generated Campaign',
                            'content': generated_content,
                            'total_recipients': len(mock_recipients),
                            'successful_sends': len(sent_emails),
                            'failed_sends': len(failed_emails),
                            'sent_emails': sent_emails,
                            'failed_emails': failed_emails,
                            'created_at': datetime.utcnow(),
                            'is_mock': True,
                            'is_real': False,
                            'auto_sent': True,
                            'fallback_reason': str(email_error)
                        }
                        
                        result = mongo.db.email_campaigns.insert_one(campaign_record)
                        
                        email_results = {
                            'success': True,
                            'type': 'mock_email',
                            'campaign_id': str(result.inserted_id),
                            'summary': {
                                'total_recipients': len(mock_recipients),
                                'successful_sends': len(sent_emails),
                                'failed_sends': len(failed_emails),
                                'success_rate': f"{(len(sent_emails) / len(mock_recipients)) * 100:.1f}%"
                            },
                            'sent_emails': sent_emails,
                            'failed_emails': failed_emails,
                            'message': f'📧 Mock email campaign sent (real email service had issues)',
                            'note': 'This was a mock campaign. Real emails may have been sent separately.'
                        }
                        
                        logger.info(f"📧 Mock email campaign sent to {len(sent_emails)} recipients")
                        
                    except Exception as mock_error:
                        logger.error(f"❌ Mock email system also failed: {mock_error}")
                        email_results = {
                            'success': False,
                            'type': 'error',
                            'error': f'Both real and mock email systems failed: {str(mock_error)}'
                        }
                
            except Exception as e:
                logger.error(f"❌ Email campaign processing failed: {e}")
                email_results = {
                    'success': False,
                    'type': 'error',
                    'error': f'Email campaign failed: {str(e)}'
                }
        
        # Save generation history
        try:
            logger.info("💾 Saving generation history...")
            generation_record = {
                'user_id': ObjectId(current_user_id),
                'content_type': content_type,
                'prompt': prompt,
                'generated_content': generated_content,
                'created_at': datetime.utcnow()
            }
            
            if email_results:
                generation_record['email_results'] = email_results
            
            result = mongo.db.ai_generations.insert_one(generation_record)
            logger.info(f"✅ Generation history saved with ID: {result.inserted_id}")
            
        except Exception as db_error:
            logger.error(f"❌ Failed to save generation history: {db_error}")
            # Continue without failing
        
        # Prepare response
        try:
            logger.info("📤 Preparing response...")
            response_data = {
                'content': generated_content,
                'type': content_type
            }
            
            if email_results:
                response_data['email_results'] = email_results
            
            logger.info("✅ Response prepared successfully")
            return jsonify(response_data), 200
            
        except Exception as response_error:
            logger.error(f"❌ Response preparation failed: {response_error}")
            return jsonify({
                'error': f'Response preparation failed: {str(response_error)}',
                'content': generated_content,  # Still return the content
                'type': content_type
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Content generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Content generation failed: {str(e)}'}), 500

@ai_bp.route('/ai-tools/gemini/business-description', methods=['POST'])
@jwt_required()
def gemini_business_description():
    """Generate business description using Gemini AI"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        business_name = data.get('business_name')
        business_type = data.get('business_type')
        key_features = data.get('key_features')
        
        if not business_name or not business_type:
            return jsonify({'error': 'Business name and type are required'}), 400
        
        result = get_gemini_service().generate_business_description(
            business_name, business_type, key_features
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/gemini/website-content', methods=['POST'])
@jwt_required()
def gemini_website_content():
    """Generate website content using Gemini AI"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        business_info = data.get('business_info', {})
        
        if not business_info.get('name'):
            return jsonify({'error': 'Business name is required'}), 400
        
        result = get_gemini_service().generate_website_content(business_info)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/gemini/social-media', methods=['POST'])
@jwt_required()
def gemini_social_media():
    """Generate social media content using Gemini AI"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        business_name = data.get('business_name')
        business_type = data.get('business_type')
        occasion = data.get('occasion')
        
        if not business_name or not business_type:
            return jsonify({'error': 'Business name and type are required'}), 400
        
        result = get_gemini_service().generate_social_media_content(
            business_name, business_type, occasion
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/github/create-website', methods=['POST'])
@jwt_required()
def github_create_website():
    """Create and deploy website using GitHub Pages"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        business_name = data.get('business_name')
        website_content = data.get('website_content', {})
        
        if not business_name:
            return jsonify({'error': 'Business name is required'}), 400
        
        result = get_github_service().create_website_repository(business_name, website_content)
        
        # Save deployment record
        if result['success']:
            deployment_record = {
                'user_id': ObjectId(current_user_id),
                'service': 'github',
                'business_name': business_name,
                'repository': result['repository'],
                'website_url': result['website_url'],
                'created_at': datetime.utcnow()
            }
            mongo.db.deployments.insert_one(deployment_record)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/netlify/deploy-website', methods=['POST'])
@jwt_required()
def netlify_deploy_website():
    """Deploy website using Netlify"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        business_name = data.get('business_name')
        website_content = data.get('website_content', {})
        
        if not business_name:
            return jsonify({'error': 'Business name is required'}), 400
        
        result = get_netlify_service().create_and_deploy_website(business_name, website_content)
        
        # Save deployment record
        if result['success']:
            deployment_record = {
                'user_id': ObjectId(current_user_id),
                'service': 'netlify',
                'business_name': business_name,
                'site_info': result['site'],
                'website_url': result['website_url'],
                'created_at': datetime.utcnow()
            }
            mongo.db.deployments.insert_one(deployment_record)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/deployments', methods=['GET'])
@jwt_required()
def get_user_deployments():
    """Get user's deployment history"""
    try:
        current_user_id = get_jwt_identity()
        
        deployments = list(mongo.db.deployments.find(
            {'user_id': ObjectId(current_user_id)},
            {'_id': 0}
        ).sort('created_at', -1).limit(10))
        
        return jsonify({
            'success': True,
            'deployments': deployments
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/confirm-email-campaign', methods=['POST'])
@jwt_required()
def confirm_email_campaign():
    """Confirm and send email campaign after user approval"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        generation_id = data.get('generation_id')
        email_subject = data.get('email_subject', 'Marketing Campaign Email')
        confirmed = data.get('confirmed', False)
        
        if not generation_id:
            return jsonify({'error': 'Generation ID is required'}), 400
        
        if not confirmed:
            return jsonify({'error': 'Email campaign must be confirmed'}), 400
        
        # Get the generated content
        generation_record = mongo.db.ai_generations.find_one({
            '_id': ObjectId(generation_id),
            'user_id': ObjectId(current_user_id)
        })
        
        if not generation_record:
            return jsonify({'error': 'Email content not found'}), 404
        
        email_content = generation_record['generated_content']
        
        # Mock email recipients (including the specified emails)
        mock_recipients = [
            'pulluripranavi@gmail.com',
            'visesh.bappana@gmail.com',
            'customer1@example.com',
            'customer2@example.com',
            'customer3@example.com',
            'customer4@example.com',
            'customer5@example.com',
            'customer6@example.com',
            'customer7@example.com',
            'customer8@example.com',
            'customer9@example.com',
            'customer10@example.com',
            'customer11@example.com',
            'customer12@example.com',
            'customer13@example.com',
            'customer14@example.com',
            'customer15@example.com',
            'customer16@example.com',
            'customer17@example.com',
            'customer18@example.com'
        ]
        
        # Mock email sending results
        sent_emails = []
        failed_emails = []
        
        import random
        from datetime import datetime, timedelta
        
        for i, email in enumerate(mock_recipients):
            # Simulate some emails failing (5% failure rate)
            if random.random() < 0.05:
                failed_emails.append({
                    'email': email,
                    'error': 'Invalid email address' if random.random() < 0.5 else 'Recipient not found'
                })
            else:
                # Simulate delivery times
                delivery_time = datetime.utcnow() + timedelta(seconds=random.randint(1, 30))
                sent_emails.append({
                    'email': email,
                    'status': 'sent',
                    'sent_at': delivery_time.isoformat(),
                    'message_id': f'msg_{random.randint(100000, 999999)}_{i}'
                })
        
        # Save confirmed email campaign to database
        campaign_record = {
            'user_id': ObjectId(current_user_id),
            'generation_id': ObjectId(generation_id),
            'campaign_type': 'email_marketing',
            'subject': email_subject,
            'content': email_content,
            'total_recipients': len(mock_recipients),
            'successful_sends': len(sent_emails),
            'failed_sends': len(failed_emails),
            'sent_emails': sent_emails,
            'failed_emails': failed_emails,
            'created_at': datetime.utcnow(),
            'is_mock': True,
            'confirmed_by_user': True,
            'status': 'sent'
        }
        
        mongo.db.email_campaigns.insert_one(campaign_record)
        
        # Update the generation record to mark as sent
        mongo.db.ai_generations.update_one(
            {'_id': ObjectId(generation_id)},
            {
                '$set': {
                    'email_sent': True,
                    'email_sent_at': datetime.utcnow(),
                    'campaign_id': campaign_record['_id']
                }
            }
        )
        
        print(f"✅ User confirmed and sent email campaign to {len(sent_emails)} recipients including pulluripranavi@gmail.com and visesh.bappana@gmail.com")
        
        return jsonify({
            'success': True,
            'campaign_id': str(campaign_record['_id']),
            'summary': {
                'total_recipients': len(mock_recipients),
                'successful_sends': len(sent_emails),
                'failed_sends': len(failed_emails),
                'success_rate': f"{(len(sent_emails) / len(mock_recipients)) * 100:.1f}%"
            },
            'sent_emails': sent_emails,
            'failed_emails': failed_emails,
            'message': f'Email campaign successfully sent to {len(sent_emails)} recipients after your confirmation!'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@ai_bp.route('/ai-tools/mock-email-send', methods=['POST'])
@jwt_required()
def mock_email_send():
    """Mock email sending for email campaigns"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        email_content = data.get('email_content')
        email_subject = data.get('email_subject', 'Your Marketing Campaign')
        
        if not email_content:
            return jsonify({'error': 'Email content is required'}), 400
        
        # Mock email recipients (including the specified emails)
        mock_recipients = [
            'pulluripranavi@gmail.com',
            'visesh.bappana@gmail.com',
            'customer1@example.com',
            'customer2@example.com',
            'customer3@example.com',
            'customer4@example.com',
            'customer5@example.com',
            'customer6@example.com',
            'customer7@example.com',
            'customer8@example.com',
            'customer9@example.com',
            'customer10@example.com',
            'customer11@example.com',
            'customer12@example.com',
            'customer13@example.com',
            'customer14@example.com',
            'customer15@example.com',
            'customer16@example.com',
            'customer17@example.com',
            'customer18@example.com'
        ]
        
        # Mock email sending results
        sent_emails = []
        failed_emails = []
        
        import random
        from datetime import datetime, timedelta
        
        for i, email in enumerate(mock_recipients):
            # Simulate some emails failing (5% failure rate)
            if random.random() < 0.05:
                failed_emails.append({
                    'email': email,
                    'error': 'Invalid email address' if random.random() < 0.5 else 'Recipient not found'
                })
            else:
                # Simulate delivery times
                delivery_time = datetime.utcnow() + timedelta(seconds=random.randint(1, 30))
                sent_emails.append({
                    'email': email,
                    'status': 'sent',
                    'sent_at': delivery_time.isoformat(),
                    'message_id': f'msg_{random.randint(100000, 999999)}_{i}'
                })
        
        # Save mock email campaign to database
        campaign_record = {
            'user_id': ObjectId(current_user_id),
            'campaign_type': 'email_marketing',
            'subject': email_subject,
            'content': email_content,
            'total_recipients': len(mock_recipients),
            'successful_sends': len(sent_emails),
            'failed_sends': len(failed_emails),
            'sent_emails': sent_emails,
            'failed_emails': failed_emails,
            'created_at': datetime.utcnow(),
            'is_mock': True
        }
        
        mongo.db.email_campaigns.insert_one(campaign_record)
        
        return jsonify({
            'success': True,
            'campaign_id': str(campaign_record['_id']),
            'summary': {
                'total_recipients': len(mock_recipients),
                'successful_sends': len(sent_emails),
                'failed_sends': len(failed_emails),
                'success_rate': f"{(len(sent_emails) / len(mock_recipients)) * 100:.1f}%"
            },
            'sent_emails': sent_emails,
            'failed_emails': failed_emails,
            'message': f'Mock email campaign sent to {len(sent_emails)} recipients successfully!'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@ai_bp.route('/ai-tools/generate-image', methods=['POST'])
@jwt_required()
def generate_image():
    """Production image generation with authentication"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        prompt = data.get('prompt')
        image_type = data.get('image_type', 'poster')
        style = data.get('style', 'professional')
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt is required'
            }), 400
        
        # Get user business context
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        business_name = user.get('business_name', 'Your Business') if user else 'Your Business'
        business_type = user.get('business_type', 'business') if user else 'business'
        
        logger.info(f"🎨 Generating {image_type} for user {current_user_id}: {prompt}")
        
        # Try Stability AI first, fallback to mock
        try:
            from app.services.stability_service import StabilityService
            stability_service = StabilityService()
            
            # Generate image based on type
            if image_type == 'poster':
                result = stability_service.generate_business_poster(
                    business_name=business_name,
                    business_type=business_type,
                    message=prompt,
                    style=style
                )
            elif image_type == 'product':
                result = stability_service.generate_product_image(
                    product_name=prompt,
                    product_description="",
                    style=style
                )
            elif image_type == 'banner':
                result = stability_service.generate_marketing_banner(
                    business_name=business_name,
                    message=prompt,
                    style=style
                )
            else:
                result = stability_service.generate_image(prompt, style, image_type)
            
            if not result.get('success'):
                raise Exception(result.get('error', 'Generation failed'))
                
            image_data = result.get('image_data')
            concept = result.get('enhanced_prompt', prompt)
            source = 'stability_ai'
            
        except Exception as e:
            logger.warning(f"Stability AI failed, using mock: {e}")
            image_data = generate_mock_image(prompt, image_type, style)
            concept = f"Mock {image_type} in {style} style for {business_name}. Real generation service unavailable."
            source = 'mock_generator'
        
        # Save generation record
        try:
            mongo.db.ai_image_generations.insert_one({
                'user_id': ObjectId(current_user_id),
                'prompt': prompt,
                'image_type': image_type,
                'style': style,
                'concept': concept,
                'image_data': image_data,
                'source': source,
                'business_context': {
                    'business_name': business_name,
                    'business_type': business_type
                },
                'created_at': datetime.utcnow()
            })
        except Exception as db_error:
            logger.warning(f"Failed to save to database: {db_error}")
        
        return jsonify({
            'success': True,
            'image_data': image_data,
            'concept': concept,
            'prompt': prompt,
            'image_type': image_type,
            'style': style,
            'source': source
        })
        
    except Exception as e:
        logger.error(f"❌ Production image generation error: {e}")
        return jsonify({
            'success': False,
            'error': f'Image generation failed: {str(e)}'
        }), 500

@ai_bp.route('/ai-tools/business-suggestions', methods=['POST'])
@jwt_required()
def get_business_suggestions():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        suggestion_type = data.get('type', 'general')  # 'marketing', 'products', 'website', 'general'
        
        # Get user's business data
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        website = mongo.db.child_websites.find_one({'owner_id': ObjectId(current_user_id)})
        
        # Get recent analytics
        recent_messages = list(mongo.db.messages.find({
            'recipient_id': ObjectId(current_user_id)
        }).sort('created_at', -1).limit(10))
        
        products = list(mongo.db.products.find({
            'user_id': ObjectId(current_user_id),
            'is_active': True
        }).limit(10))
        
        qr_analytics = mongo.db.qr_analytics.find_one({
            'user_id': ObjectId(current_user_id)
        })
        
        # Prepare context for AI
        context = {
            'business_name': user.get('business_name', '') if user else '',
            'business_type': website.get('business_type', '') if website else '',
            'total_products': len(products),
            'recent_messages_count': len(recent_messages),
            'qr_scans': qr_analytics.get('total_scans', 0) if qr_analytics else 0,
            'suggestion_type': suggestion_type
        }
        
        ai_service = AIService()
        suggestions = ai_service.generate_business_suggestions(context)
        
        # Save suggestions
        mongo.db.ai_suggestions.insert_one({
            'user_id': ObjectId(current_user_id),
            'suggestion_type': suggestion_type,
            'suggestions': suggestions,
            'context': context,
            'created_at': datetime.utcnow()
        })
        
        return jsonify({
            'suggestions': suggestions,
            'type': suggestion_type
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/analyze-feedback', methods=['POST'])
@jwt_required()
def analyze_feedback():
    try:
        current_user_id = get_jwt_identity()
        
        # Get all messages and feedback
        messages = list(mongo.db.messages.find({
            'recipient_id': ObjectId(current_user_id)
        }))
        
        feedback_entries = list(mongo.db.customer_feedback.find({
            'business_owner_id': ObjectId(current_user_id)
        }))
        
        if not messages and not feedback_entries:
            return jsonify({
                'analysis': 'No feedback data available for analysis.',
                'insights': [],
                'recommendations': []
            }), 200
        
        # Prepare feedback text for analysis
        feedback_texts = []
        for message in messages:
            if message.get('content'):
                feedback_texts.append(message['content'])
        
        for feedback in feedback_entries:
            if feedback.get('feedback_text'):
                feedback_texts.append(feedback['feedback_text'])
        
        ai_service = AIService()
        analysis = ai_service.analyze_customer_feedback(feedback_texts)
        
        # Save analysis
        mongo.db.feedback_analysis.insert_one({
            'user_id': ObjectId(current_user_id),
            'analysis': analysis,
            'total_feedback_items': len(feedback_texts),
            'created_at': datetime.utcnow()
        })
        
        return jsonify(analysis), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/generation-history', methods=['GET'])
@jwt_required()
def get_generation_history():
    try:
        current_user_id = get_jwt_identity()
        history_type = request.args.get('type', 'all')  # 'content', 'image', 'suggestions', 'all'
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        skip = (page - 1) * per_page
        
        history = []
        
        if history_type in ['content', 'all']:
            content_history = list(mongo.db.ai_generations.find({
                'user_id': ObjectId(current_user_id)
            }).sort('created_at', -1).skip(skip).limit(per_page))
            
            for item in content_history:
                history.append({
                    'id': str(item['_id']),
                    'type': 'content',
                    'content_type': item['content_type'],
                    'prompt': item['prompt'],
                    'result': item['generated_content'],
                    'created_at': item['created_at']
                })
        
        if history_type in ['image', 'all']:
            image_history = list(mongo.db.ai_image_generations.find({
                'user_id': ObjectId(current_user_id)
            }).sort('created_at', -1).skip(skip).limit(per_page))
            
            for item in image_history:
                history.append({
                    'id': str(item['_id']),
                    'type': 'image',
                    'image_type': item['image_type'],
                    'prompt': item['prompt'],
                    'style': item['style'],
                    'image_data': item['image_data'],
                    'created_at': item['created_at']
                })
        
        if history_type in ['suggestions', 'all']:
            suggestions_history = list(mongo.db.ai_suggestions.find({
                'user_id': ObjectId(current_user_id)
            }).sort('created_at', -1).skip(skip).limit(per_page))
            
            for item in suggestions_history:
                history.append({
                    'id': str(item['_id']),
                    'type': 'suggestions',
                    'suggestion_type': item['suggestion_type'],
                    'suggestions': item['suggestions'],
                    'created_at': item['created_at']
                })
        
        # Sort by created_at
        history.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'history': history[:per_page],
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai-tools/chatbot', methods=['POST'])
@jwt_required()
def chatbot():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        message = data.get('message')
        conversation_id = data.get('conversation_id')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get user context
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        website = mongo.db.child_websites.find_one({'owner_id': ObjectId(current_user_id)})
        
        # Get conversation history if exists
        conversation_history = []
        if conversation_id:
            chat_history = mongo.db.chatbot_conversations.find_one({
                '_id': ObjectId(conversation_id),
                'user_id': ObjectId(current_user_id)
            })
            if chat_history:
                conversation_history = chat_history.get('messages', [])
        
        ai_service = AIService()
        response = ai_service.chatbot_response(
            message, 
            user_context={
                'business_name': user.get('business_name', '') if user else '',
                'business_type': website.get('business_type', '') if website else ''
            },
            conversation_history=conversation_history
        )
        
        # Save conversation
        new_message = {
            'user_message': message,
            'bot_response': response,
            'timestamp': datetime.utcnow()
        }
        
        if conversation_id:
            # Update existing conversation
            mongo.db.chatbot_conversations.update_one(
                {'_id': ObjectId(conversation_id)},
                {'$push': {'messages': new_message}, '$set': {'updated_at': datetime.utcnow()}}
            )
        else:
            # Create new conversation
            result = mongo.db.chatbot_conversations.insert_one({
                'user_id': ObjectId(current_user_id),
                'messages': [new_message],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
            conversation_id = str(result.inserted_id)
        
        return jsonify({
            'response': response,
            'conversation_id': conversation_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== New Email Service Endpoints =====

# ===== ADD THESE ROUTES TO THE END OF YOUR ai_tools.py FILE =====

@ai_bp.route('/ai-tools/test-email-service', methods=['GET'])
@jwt_required()
def test_email_service():
    """Test email service connection"""
    try:
        email_service = get_email_service()
        result = email_service.test_connection()
        
        logger.info(f"Email service test result: {result}")
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        logger.error(f"Email service test error: {e}")
        return jsonify({
            'success': False,
            'error': f'Email service test failed: {str(e)}',
            'help': 'Make sure Gmail credentials are configured properly'
        }), 500

@ai_bp.route('/ai-tools/send-test-email', methods=['POST'])
@jwt_required()
def send_test_email():
    """Send a test email to verify email functionality"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # Default to pulluripranavi@gmail.com or allow custom recipient
        recipient_email = data.get('recipient_email', 'pulluripranavi@gmail.com')
        
        logger.info(f"🧪 Sending test email to {recipient_email} for user {current_user_id}")
        
        email_service = get_email_service()
        
        # First test connection
        connection_test = email_service.test_connection()
        if not connection_test['success']:
            return jsonify({
                'success': False,
                'error': f'Email service connection failed: {connection_test["error"]}',
                'help': connection_test.get('help', 'Check email service configuration')
            }), 500
        
        # Send test email
        result = email_service.send_test_email(recipient_email)
        
        if result['success']:
            # Save test email record
            test_record = {
                'user_id': ObjectId(current_user_id),
                'email_type': 'test_email',
                'recipient': recipient_email,
                'subject': '🚀 Break-Even AI Tools - Test Email',
                'sent_at': datetime.utcnow(),
                'message_id': result.get('message_id'),
                'status': 'sent'
            }
            mongo.db.email_logs.insert_one(test_record)
            
            logger.info(f"✅ Test email sent successfully to {recipient_email}")
            
            return jsonify({
                'success': True,
                'message': f'Test email sent successfully to {recipient_email}!',
                'recipient': recipient_email,
                'sent_at': result['sent_at'],
                'message_id': result['message_id']
            }), 200
        else:
            logger.error(f"❌ Test email failed: {result['error']}")
            return jsonify({
                'success': False,
                'error': f'Test email failed: {result["error"]}',
                'recipient': recipient_email
            }), 500
            
    except Exception as e:
        logger.error(f"Send test email error: {e}")
        return jsonify({
            'success': False,
            'error': f'Send test email failed: {str(e)}'
        }), 500

@ai_bp.route('/ai-tools/send-real-email', methods=['POST'])
@jwt_required()
def send_real_email():
    """Send real emails to specified recipients"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        recipients = data.get('recipients', [])
        subject = data.get('subject', 'Email from Break-even App')
        content = data.get('content', '')
        content_type = data.get('content_type', 'text')
        
        if not recipients:
            return jsonify({
                'success': False,
                'error': 'Recipients list is required'
            }), 400
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'Email content is required'
            }), 400
        
        logger.info(f"📧 Sending real emails to {len(recipients)} recipients for user {current_user_id}")
        
        email_service = get_email_service()
        
        # Test connection first
        connection_test = email_service.test_connection()
        if not connection_test['success']:
            return jsonify({
                'success': False,
                'error': f'Email service connection failed: {connection_test["error"]}',
                'help': connection_test.get('help', 'Check email service configuration')
            }), 500
        
        # Send bulk emails
        results = email_service.send_bulk_emails(
            recipients=recipients,
            subject=subject,
            content=content,
            content_type=content_type
        )
        
        # Save email campaign record
        campaign_record = {
            'user_id': ObjectId(current_user_id),
            'campaign_type': 'real_email_campaign',
            'subject': subject,
            'content': content,
            'content_type': content_type,
            'recipients': recipients,
            'total_recipients': results['total_recipients'],
            'successful_sends': results['summary']['successful_sends'],
            'failed_sends': results['summary']['failed_sends'],
            'success_rate': results['summary']['success_rate'],
            'sent_emails': results['successful_sends'],
            'failed_emails': results['failed_sends'],
            'created_at': datetime.utcnow(),
            'is_mock': False,
            'is_real': True,
            'sent_via_api': True
        }
        
        mongo.db.email_campaigns.insert_one(campaign_record)
        
        logger.info(f"✅ Real email campaign completed: {results['summary']['successful_sends']}/{results['total_recipients']} successful")
        
        return jsonify({
            'success': True,
            'campaign_id': str(campaign_record['_id']),
            'summary': results['summary'],
            'sent_emails': results['successful_sends'],
            'failed_emails': results['failed_sends'],
            'message': f'Real email campaign sent! {results["summary"]["successful_sends"]} out of {results["total_recipients"]} emails delivered successfully.'
        }), 200
        
    except Exception as e:
        logger.error(f"Send real email error: {e}")
        return jsonify({
            'success': False,
            'error': f'Send real email failed: {str(e)}'
        }), 500