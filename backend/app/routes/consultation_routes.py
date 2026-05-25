from flask import Blueprint, request, jsonify
from flask_mail import Message
from app import mail
import logging

consultation_bp = Blueprint('consultation', __name__)

@consultation_bp.route('/send-consultation-confirmation', methods=['POST'])
def send_consultation_confirmation():
    """Send consultation confirmation email"""
    try:
        data = request.get_json()
        
        # Extract consultation details
        client_name = data.get('clientName')
        practice_area = data.get('practiceArea')
        preferred_date = data.get('preferredDate')
        client_email = data.get('email')
        phone = data.get('phone', '')
        message_text = data.get('message', '')
        
        # Create professional email content
        subject = f"Consultation Confirmed - {practice_area}"
        
        body = f"""
Dear {client_name},

Thank you for scheduling a consultation with our law firm. We are pleased to confirm your appointment.

Consultation Details:
- Practice Area: {practice_area}
- Preferred Date: {preferred_date}
- Client: {client_name}
- Email: {client_email}
{f"- Phone: {phone}" if phone else ""}

{f"Your Message: {message_text}" if message_text else ""}

Our legal team will contact you soon to finalize the appointment details and discuss your legal matter.

We look forward to assisting you with your legal needs.

Best regards,
Legal Services Team

---
This is an automated confirmation email. Please do not reply to this message.
        """
        
        # Send email to the business owner
        msg = Message(
            subject=subject,
            sender='noreply@breakeven.com',
            recipients=['pulluripranavi@gmail.com'],
            body=body
        )
        
        mail.send(msg)
        
        logging.info(f"Consultation confirmation email sent for {client_name}")
        
        return jsonify({
            'success': True,
            'message': 'Consultation confirmation email sent successfully'
        }), 200
        
    except Exception as e:
        logging.error(f"Error sending consultation confirmation email: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to send confirmation email'
        }), 500

@consultation_bp.route('/send-consultation-cancellation', methods=['POST'])
def send_consultation_cancellation():
    """Send consultation cancellation email"""
    try:
        data = request.get_json()
        
        # Extract consultation details
        client_name = data.get('clientName')
        practice_area = data.get('practiceArea')
        preferred_date = data.get('preferredDate')
        client_email = data.get('email')
        
        # Create professional email content
        subject = f"Consultation Cancelled - {practice_area}"
        
        body = f"""
Dear {client_name},

We regret to inform you that your scheduled consultation has been cancelled.

Cancelled Consultation Details:
- Practice Area: {practice_area}
- Preferred Date: {preferred_date}
- Client: {client_name}
- Email: {client_email}

If you would like to reschedule or have any questions, please contact us directly.

We apologize for any inconvenience this may cause.

Best regards,
Legal Services Team

---
This is an automated notification email. Please do not reply to this message.
        """
        
        # Send email to the business owner
        msg = Message(
            subject=subject,
            sender='noreply@breakeven.com',
            recipients=['pulluripranavi@gmail.com'],
            body=body
        )
        
        mail.send(msg)
        
        logging.info(f"Consultation cancellation email sent for {client_name}")
        
        return jsonify({
            'success': True,
            'message': 'Consultation cancellation email sent successfully'
        }), 200
        
    except Exception as e:
        logging.error(f"Error sending consultation cancellation email: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to send cancellation email'
        }), 500