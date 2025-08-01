
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.models.product import Product
from bson import ObjectId
from datetime import datetime

products_bp = Blueprint('products', _name_)

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
        update_data = {
            **data,
            'updated_at': datetime.utcnow()
        }
        
        mongo.db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update_data}
        )
        
        # Get updated product
        updated_product = mongo.db.products.find_one({'_id': ObjectId(product_id)})
        updated_product['_id'] = str(updated_product['_id'])
        updated_product['user_id'] = str(updated_product['user_id'])
        
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
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
