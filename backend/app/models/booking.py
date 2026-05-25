from datetime import datetime
from bson import ObjectId

class Booking:
    """Model for attorney/service bookings"""
    
    def __init__(self, business_id, customer_name, customer_email, customer_phone,
                 service_type, attorney_name, date, time, notes=''):
        self.business_id = ObjectId(business_id) if isinstance(business_id, str) else business_id
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.customer_phone = customer_phone
        self.service_type = service_type
        self.attorney_name = attorney_name
        self.date = date if isinstance(date, datetime) else datetime.fromisoformat(date)
        self.time = time
        self.notes = notes
        self.status = 'pending'  # pending, confirmed, cancelled, completed
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.confirmed_at = None
        self.cancelled_at = None
        self.cancellation_reason = None
        
    def to_dict(self):
        return {
            'business_id': self.business_id,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'service_type': self.service_type,
            'attorney_name': self.attorney_name,
            'date': self.date,
            'time': self.time,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'confirmed_at': self.confirmed_at,
            'cancelled_at': self.cancelled_at,
            'cancellation_reason': self.cancellation_reason
        }
    
    @staticmethod
    def from_dict(data):
        booking = Booking(
            business_id=data['business_id'],
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data['customer_phone'],
            service_type=data['service_type'],
            attorney_name=data['attorney_name'],
            date=data['date'],
            time=data['time'],
            notes=data.get('notes', '')
        )
        booking.status = data.get('status', 'pending')
        booking.created_at = data.get('created_at', datetime.utcnow())
        booking.updated_at = data.get('updated_at', datetime.utcnow())
        booking.confirmed_at = data.get('confirmed_at')
        booking.cancelled_at = data.get('cancelled_at')
        booking.cancellation_reason = data.get('cancellation_reason')
        return booking
    
    def confirm(self):
        """Confirm the booking"""
        self.status = 'confirmed'
        self.confirmed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def cancel(self, reason=''):
        """Cancel the booking"""
        self.status = 'cancelled'
        self.cancelled_at = datetime.utcnow()
        self.cancellation_reason = reason
        self.updated_at = datetime.utcnow()
    
    def complete(self):
        """Mark booking as completed"""
        self.status = 'completed'
        self.updated_at = datetime.utcnow()
