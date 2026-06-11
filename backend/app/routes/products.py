from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.models.product import Product
from bson import ObjectId
from datetime import datetime
import logging

products_bp = Blueprint('products', __name__)
logger = logging.getLogger(__name__)

def trigger_site_redeploy(business_id):
    """Automatically rebuild and deploy child website when products are modified"""
    try:
        b_id_str = str(business_id)
        # Find active schema
        active_schema = mongo.db.website_schemas.find_one({
            'business_id': b_id_str,
            'is_active': True
        })
        if active_schema:
            from app.services.schema_renderer import SchemaRenderer
            from app.services.patch_engine import PatchEngine
            
            rendered_html = SchemaRenderer.render(active_schema)
            # Write to disk
            PatchEngine.write_website_to_disk(b_id_str, rendered_html)
            # Push to Netlify (best-effort)
            PatchEngine._deploy_to_netlify(b_id_str, rendered_html)
            logger.info(f"🔄 Website auto-redeployed on product change for business {b_id_str}")
    except Exception as e:
        logger.warning(f"Could not auto-redeploy site for business {business_id} on product change: {e}")

@products_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    try:
        current_user_id = get_jwt_identity()
        products = list(mongo.db.products.find({
            'user_id': ObjectId(current_user_id),
            'is_active': True
        }))
        
        # Convert ObjectId to string for JSON serialization
        for product in products:
            product['_id'] = str(product['_id'])
            product['user_id'] = str(product['user_id'])
        
        return jsonify(products), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'description', 'price', 'stock', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create product
        product = Product(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            stock=data['stock'],
            category=data['category'],
            user_id=current_user_id,
            sku=data.get('sku'),
            image=data.get('image')
        )
        
        # Insert into database
        result = mongo.db.products.insert_one({
            **product.to_dict(),
            'user_id': ObjectId(current_user_id)
        })
        # Get the created product
        created_product = mongo.db.products.find_one({'_id': result.inserted_id})
        created_product['_id'] = str(created_product['_id'])
        created_product['user_id'] = str(created_product['user_id'])
        
        # Trigger website redeploy to Netlify/disk
        trigger_site_redeploy(current_user_id)
        
        return jsonify(created_product), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/<product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Check if product exists and belongs to current user
        product = mongo.db.products.find_one({
            '_id': ObjectId(product_id),
            'user_id': ObjectId(current_user_id)
        })
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        # Update product
        # Strip immutable / query fields to prevent mongo write errors
        update_data = {k: v for k, v in data.items() if k not in ['_id', 'user_id']}
        
        # Cast types if present
        if 'price' in update_data:
            try:
                update_data['price'] = float(update_data['price'])
            except (ValueError, TypeError):
                pass
        if 'stock' in update_data:
            try:
                update_data['stock'] = int(update_data['stock'])
            except (ValueError, TypeError):
                pass
                
        update_data['updated_at'] = datetime.utcnow()
        
        mongo.db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update_data}
        )
        
        # Get updated product
        updated_product = mongo.db.products.find_one({'_id': ObjectId(product_id)})
        updated_product['_id'] = str(updated_product['_id'])
        updated_product['user_id'] = str(updated_product['user_id'])
        
        # Trigger website redeploy to Netlify/disk
        trigger_site_redeploy(current_user_id)
        
        return jsonify(updated_product), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/<product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    try:
        current_user_id = get_jwt_identity()
        # Check if product exists and belongs to current user
        product = mongo.db.products.find_one({
            '_id': ObjectId(product_id),
            'user_id': ObjectId(current_user_id)
        })
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Soft delete product
        mongo.db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
        )
        
        # Trigger website redeploy to Netlify/disk
        trigger_site_redeploy(current_user_id)
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
