from datetime import datetime
from bson import ObjectId

class Order:
    """Model for product orders (e.g., tailor shop orders)"""
    
    def __init__(self, business_id, customer_name, customer_email, customer_phone,
                 items, total_amount, delivery_address='', notes=''):
        self.business_id = ObjectId(business_id) if isinstance(business_id, str) else business_id
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.customer_phone = customer_phone
        self.items = items  # List of {product_id, product_name, quantity, price, customizations}
        self.total_amount = total_amount
        self.delivery_address = delivery_address
        self.notes = notes
        self.status = 'pending'  # pending, processing, completed, cancelled
        self.measurements = {}  # For tailor shops: {chest, waist, length, etc.}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.processing_started_at = None
        self.completed_at = None
        self.cancelled_at = None
        self.cancellation_reason = None
        self.tracking_number = None
        
    def to_dict(self):
        return {
            'business_id': self.business_id,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'items': self.items,
            'total_amount': self.total_amount,
            'delivery_address': self.delivery_address,
            'notes': self.notes,
            'status': self.status,
            'measurements': self.measurements,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'processing_started_at': self.processing_started_at,
            'completed_at': self.completed_at,
            'cancelled_at': self.cancelled_at,
            'cancellation_reason': self.cancellation_reason,
            'tracking_number': self.tracking_number
        }
    
    @staticmethod
    def from_dict(data):
        order = Order(
            business_id=data['business_id'],
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data['customer_phone'],
            items=data['items'],
            total_amount=data['total_amount'],
            delivery_address=data.get('delivery_address', ''),
            notes=data.get('notes', '')
        )
        order.status = data.get('status', 'pending')
        order.measurements = data.get('measurements', {})
        order.created_at = data.get('created_at', datetime.utcnow())
        order.updated_at = data.get('updated_at', datetime.utcnow())
        order.processing_started_at = data.get('processing_started_at')
        order.completed_at = data.get('completed_at')
        order.cancelled_at = data.get('cancelled_at')
        order.cancellation_reason = data.get('cancellation_reason')
        order.tracking_number = data.get('tracking_number')
        return order
    
    def update_status(self, new_status):
        """Update order status"""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        if new_status == 'processing' and not self.processing_started_at:
            self.processing_started_at = datetime.utcnow()
        elif new_status == 'completed' and not self.completed_at:
            self.completed_at = datetime.utcnow()
        elif new_status == 'cancelled' and not self.cancelled_at:
            self.cancelled_at = datetime.utcnow()
    
    def cancel(self, reason=''):
        """Cancel the order"""
        self.status = 'cancelled'
        self.cancelled_at = datetime.utcnow()
        self.cancellation_reason = reason
        self.updated_at = datetime.utcnow()
    
    def add_measurements(self, measurements):
        """Add customer measurements"""
        self.measurements = measurements
        self.updated_at = datetime.utcnow()
    
    def set_tracking_number(self, tracking_number):
        """Set tracking number for delivery"""
        self.tracking_number = tracking_number
        self.updated_at = datetime.utcnow()
