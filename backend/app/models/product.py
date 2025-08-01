
from datetime import datetime
from bson import ObjectId

class Product:
    def _init_(self, name, description, price, stock, category, user_id, sku=None, image=None):
        self.name = name
        self.description = description
        self.price = float(price)
        self.stock = int(stock)
        self.category = category
        self.user_id = ObjectId(user_id)
        self.sku = sku
        self.image = image
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_active = True
        
    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'category': self.category,
            'user_id': str(self.user_id),
            'sku': self.sku,
            'image': self.image,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active
        }
    @staticmethod
    def from_dict(data):
        product = Product(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            stock=data['stock'],
            category=data['category'],
            user_id=data['user_id']
        )
        product.sku = data.get('sku')
        product.image = data.get('image')
        product.created_at = data.get('created_at', datetime.utcnow())
        product.updated_at = data.get('updated_at', datetime.utcnow())
        product.is_active = data.get('is_active', True)
        return product


