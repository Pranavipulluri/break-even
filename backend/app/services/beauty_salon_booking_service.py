"""
Beauty Salon Booking Service - Handles appointment scheduling and management
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

logger = logging.getLogger(__name__)

class BeautySalonBookingService:
    """Service for managing spa/salon appointments and bookings"""
    
    def __init__(self):
        self.booking_slots = self._generate_default_slots()
    
    def setup_booking_system(self, salon_data: dict) -> dict:
        """Setup booking system for the salon"""
        try:
            salon_id = salon_data.get('salon_id')
            salon_name = salon_data.get('salon_name', 'Beauty Salon')
            
            logger.info(f"Setting up booking system for: {salon_name}")
            
            # Configure booking system
            booking_config = {
                'salon_id': salon_id,
                'salon_name': salon_name,
                'services': salon_data.get('services', []),
                'staff_members': salon_data.get('staff_members', []),
                'business_hours': salon_data.get('business_hours', {}),
                'booking_enabled': True
            }
            
            return {
                'success': True,
                'booking_config': booking_config,
                'booking_url': f'/booking/{salon_id}',
                'admin_url': f'/admin/bookings/{salon_id}'
            }
            
        except Exception as e:
            logger.error(f"Error setting up booking system: {e}")
            return {
                'success': False,
                'error': f'Booking system setup failed: {str(e)}'
            }
    
    def get_salon_statistics(self, salon_id: str) -> dict:
        """Get salon statistics and dashboard data"""
        try:
            # Mock statistics data - in a real implementation, this would query the database
            stats = {
                'total_bookings': 0,
                'upcoming_appointments': 0,
                'revenue_this_month': 0,
                'popular_services': [],
                'staff_utilization': {},
                'customer_count': 0
            }
            
            return {
                'success': True,
                'salon_id': salon_id,
                'statistics': stats
            }
            
        except Exception as e:
            logger.error(f"Error getting salon statistics: {e}")
            return {
                'success': False,
                'error': f'Failed to get statistics: {str(e)}'
            }
        
    def _generate_default_slots(self) -> Dict:
        """Generate default available time slots"""
        slots = {}
        
        # Generate slots for next 30 days
        base_date = datetime.now().date()
        for i in range(30):
            date = base_date + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            # Skip Sundays (assuming closed)
            if date.weekday() == 6:
                slots[date_str] = []
                continue
            
            # Generate hourly slots from 9 AM to 6 PM
            daily_slots = []
            for hour in range(9, 18):
                slot_time = f"{hour:02d}:00"
                daily_slots.append({
                    'time': slot_time,
                    'available': True,
                    'staff_member': None,
                    'service': None
                })
            
            slots[date_str] = daily_slots
        
        return slots
    
    def process_appointment_booking(self, booking_data: Dict) -> Dict:
        """Process a new appointment booking"""
        try:
            # Generate appointment ID
            appointment_id = f"SPA_{uuid.uuid4().hex[:8].upper()}"
            
            # Extract booking details
            salon_id = booking_data.get('salon_id')
            client_name = booking_data.get('clientName')
            client_email = booking_data.get('clientEmail')
            client_phone = booking_data.get('clientPhone')
            preferred_staff = booking_data.get('preferredStaff')
            service_type = booking_data.get('serviceType')
            appointment_date = booking_data.get('appointmentDate')
            appointment_time = booking_data.get('appointmentTime')
            special_requests = booking_data.get('specialRequests')
            
            # Validate required fields
            if not all([client_name, client_email, service_type, appointment_date, appointment_time]):
                return {
                    "success": False,
                    "error": "Missing required booking information"
                }
            
            # Check availability (simplified - in real implementation, check against database)
            is_available = self._check_availability(appointment_date, appointment_time, preferred_staff)
            
            if not is_available:
                return {
                    "success": False,
                    "error": "Selected time slot is not available"
                }
            
            # Create appointment record
            appointment = {
                "appointment_id": appointment_id,
                "salon_id": salon_id,
                "client_name": client_name,
                "client_email": client_email,
                "client_phone": client_phone,
                "preferred_staff": preferred_staff,
                "service_type": service_type,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "special_requests": special_requests,
                "status": "pending_confirmation",
                "created_at": datetime.now().isoformat(),
                "estimated_duration": self._get_service_duration(service_type),
                "estimated_price": self._get_service_price(service_type)
            }
            
            # In a real implementation, save to database here
            logger.info(f"Appointment booking processed: {appointment_id}")
            
            # Send confirmation email (simulated)
            self._send_booking_confirmation(appointment)
            
            return {
                "success": True,
                "appointment_id": appointment_id,
                "appointment_details": appointment,
                "confirmation_message": f"Thank you {client_name}! Your appointment request has been received. We will contact you within 24 hours to confirm your {service_type} appointment on {appointment_date} at {appointment_time}."
            }
            
        except Exception as e:
            logger.error(f"Error processing appointment booking: {e}")
            return {
                "success": False,
                "error": "Unable to process booking at this time"
            }
    
    def _check_availability(self, date: str, time: str, staff_member: Optional[str] = None) -> bool:
        """Check if a time slot is available"""
        try:
            # Simplified availability check
            # In real implementation, check against database
            date_slots = self.booking_slots.get(date, [])
            
            for slot in date_slots:
                if slot['time'] == time:
                    if staff_member:
                        # Check specific staff availability
                        return slot['available'] and (slot['staff_member'] is None or slot['staff_member'] == staff_member)
                    else:
                        # Check general availability
                        return slot['available']
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return False
    
    def _get_service_duration(self, service_type: str) -> int:
        """Get estimated service duration in minutes"""
        duration_map = {
            'Facial Treatments': 60,
            'Massage Therapy': 90,
            'Hair Styling': 45,
            'Nail Care': 30,
            'Spa Packages': 180,
            'Skincare Consultation': 30,
            'Manicure': 30,
            'Pedicure': 45,
            'Hair Cut': 30,
            'Hair Color': 120,
            'Eyebrow Threading': 15,
            'Waxing': 30
        }
        
        return duration_map.get(service_type, 60)  # Default 60 minutes
    
    def _get_service_price(self, service_type: str) -> float:
        """Get estimated service price"""
        price_map = {
            'Facial Treatments': 80.0,
            'Massage Therapy': 100.0,
            'Hair Styling': 60.0,
            'Nail Care': 40.0,
            'Spa Packages': 200.0,
            'Skincare Consultation': 50.0,
            'Manicure': 25.0,
            'Pedicure': 35.0,
            'Hair Cut': 40.0,
            'Hair Color': 80.0,
            'Eyebrow Threading': 15.0,
            'Waxing': 30.0
        }
        
        return price_map.get(service_type, 50.0)  # Default $50
    
    def _send_booking_confirmation(self, appointment: Dict) -> bool:
        """Send booking confirmation email (simulated)"""
        try:
            # In real implementation, integrate with email service
            logger.info(f"Booking confirmation sent to {appointment['client_email']} for appointment {appointment['appointment_id']}")
            return True
        except Exception as e:
            logger.error(f"Error sending booking confirmation: {e}")
            return False
    
    def get_available_slots(self, salon_id: str, date: str, service_type: Optional[str] = None) -> Dict:
        """Get available appointment slots for a specific date"""
        try:
            available_slots = []
            date_slots = self.booking_slots.get(date, [])
            
            for slot in date_slots:
                if slot['available']:
                    slot_info = {
                        'time': slot['time'],
                        'available_staff': self._get_available_staff(date, slot['time']),
                        'services_available': True
                    }
                    
                    if service_type:
                        # Add service-specific information
                        slot_info['estimated_duration'] = self._get_service_duration(service_type)
                        slot_info['estimated_price'] = self._get_service_price(service_type)
                    
                    available_slots.append(slot_info)
            
            return {
                "success": True,
                "date": date,
                "available_slots": available_slots,
                "salon_id": salon_id
            }
            
        except Exception as e:
            logger.error(f"Error getting available slots: {e}")
            return {
                "success": False,
                "error": "Unable to retrieve available slots"
            }
    
    def _get_available_staff(self, date: str, time: str) -> List[str]:
        """Get list of available staff members for a specific time slot"""
        # Simplified - in real implementation, check staff schedules
        default_staff = [
            "Head Stylist",
            "Spa Therapist", 
            "Beauty Specialist",
            "Massage Therapist"
        ]
        
        return default_staff
    
    def confirm_appointment(self, appointment_id: str) -> Dict:
        """Confirm a pending appointment"""
        try:
            # In real implementation, update database
            logger.info(f"Appointment confirmed: {appointment_id}")
            
            return {
                "success": True,
                "appointment_id": appointment_id,
                "status": "confirmed",
                "message": "Appointment has been confirmed"
            }
            
        except Exception as e:
            logger.error(f"Error confirming appointment: {e}")
            return {
                "success": False,
                "error": "Unable to confirm appointment"
            }
    
    def cancel_appointment(self, appointment_id: str, reason: Optional[str] = None) -> Dict:
        """Cancel an appointment"""
        try:
            # In real implementation, update database and send notification
            logger.info(f"Appointment cancelled: {appointment_id}, Reason: {reason}")
            
            return {
                "success": True,
                "appointment_id": appointment_id,
                "status": "cancelled",
                "message": "Appointment has been cancelled"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return {
                "success": False,
                "error": "Unable to cancel appointment"
            }
    
    def reschedule_appointment(self, appointment_id: str, new_date: str, new_time: str) -> Dict:
        """Reschedule an existing appointment"""
        try:
            # Check new slot availability
            is_available = self._check_availability(new_date, new_time)
            
            if not is_available:
                return {
                    "success": False,
                    "error": "New time slot is not available"
                }
            
            # In real implementation, update database
            logger.info(f"Appointment rescheduled: {appointment_id} to {new_date} {new_time}")
            
            return {
                "success": True,
                "appointment_id": appointment_id,
                "new_date": new_date,
                "new_time": new_time,
                "status": "rescheduled",
                "message": "Appointment has been rescheduled"
            }
            
        except Exception as e:
            logger.error(f"Error rescheduling appointment: {e}")
            return {
                "success": False,
                "error": "Unable to reschedule appointment"
            }

    def get_recent_appointments(self, salon_id: str, limit: int = 10) -> list:
        """Get recent appointments for the salon"""
        try:
            logger.info(f"Getting recent appointments for salon {salon_id}")
            
            # In a real implementation, this would query the database
            # For now, return sample data
            recent_appointments = []
            
            from datetime import datetime, timedelta
            import random
            
            # Generate sample recent appointments
            services = ["Facial Treatment", "Massage Therapy", "Hair Styling", "Manicure", "Pedicure"]
            statuses = ["completed", "cancelled", "no-show", "confirmed"]
            
            for i in range(min(limit, 8)):  # Generate up to 8 recent appointments
                appointment_date = datetime.now() - timedelta(days=random.randint(1, 30))
                
                appointment = {
                    "appointment_id": f"APT_{random.randint(100000, 999999)}",
                    "client_name": f"Client {i+1}",
                    "client_email": f"client{i+1}@example.com",
                    "service": random.choice(services),
                    "staff_member": "Staff Member",
                    "date": appointment_date.strftime('%Y-%m-%d'),
                    "time": f"{random.randint(9, 17):02d}:00",
                    "status": random.choice(statuses),
                    "duration": random.choice([30, 60, 90]),
                    "price": random.choice([50, 75, 100, 120])
                }
                recent_appointments.append(appointment)
            
            # Sort by date (most recent first)
            recent_appointments.sort(key=lambda x: x['date'], reverse=True)
            
            return recent_appointments
            
        except Exception as e:
            logger.error(f"Error getting recent appointments: {e}")
            return []