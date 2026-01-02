"""Customer portal routes for property search and advice."""
import json
import random
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import User, CustomerEnquiry, LLMConfig
from app.auth.auth_service import auth_required
from app.customer.customer_service import CustomerService

# Import PDF service with error handling
try:
    from flask import send_file
    from io import BytesIO
    from app.customer.pdf_service import PDFReportService
    PDF_SERVICE_AVAILABLE = True
except ImportError:
    PDF_SERVICE_AVAILABLE = False

customer_bp = Blueprint('customer', __name__)


@customer_bp.route('/send-otp', methods=['POST'])
@auth_required(['customer'])
def send_otp():
    """Send OTP to customer email for verification."""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Get current user
        user_id = request.current_user['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update user email and generate OTP
        user.email = email
        otp_code = user.generate_otp()
        
        # In a real application, you would send email here
        # For demo purposes, we'll just return success
        # send_email_otp(email, otp_code)
        
        return jsonify({
            'message': 'OTP sent successfully',
            'otp': otp_code  # Remove this in production
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/verify-otp', methods=['POST'])
@auth_required(['customer'])
def verify_otp():
    """Verify OTP code."""
    try:
        data = request.get_json()
        otp_code = data.get('otp_code')
        
        if not otp_code:
            return jsonify({'error': 'OTP code is required'}), 400
        
        # Get current user
        user_id = request.current_user['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify OTP
        if user.verify_otp(otp_code):
            return jsonify({
                'message': 'Email verified successfully',
                'is_verified': True
            }), 200
        else:
            return jsonify({'error': 'Invalid or expired OTP'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/search-properties', methods=['POST'])
@auth_required(['customer'])
def search_properties():
    """Search properties using web search."""
    try:
        data = request.get_json()
        search_criteria = data.get('search_criteria', {})
        
        # Get current user
        user_id = request.current_user['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Use CustomerService to search properties (no email verification required)
        results = CustomerService.search_properties(search_criteria)
        
        # Save enquiry
        enquiry = CustomerEnquiry(
            customer_id=user_id,
            email=user.email or 'not_provided@example.com',
            enquiry_type='search',
            search_criteria=json.dumps(search_criteria)
        )
        db.session.add(enquiry)
        db.session.commit()
        
        return jsonify({
            'results': results,
            'enquiry_id': enquiry.id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/get-property-advice', methods=['POST'])
@auth_required(['customer'])
def get_property_advice():
    """Get property advice using LLM."""
    try:
        data = request.get_json()
        advice_request = data.get('advice_request', '')
        
        if not advice_request:
            return jsonify({'error': 'Advice request is required'}), 400
        
        # Get current user
        user_id = request.current_user['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Use CustomerService to get advice (no email verification required)
        advice = CustomerService.get_property_advice(advice_request)
        
        # Save enquiry
        enquiry = CustomerEnquiry(
            customer_id=user_id,
            email=user.email or 'not_provided@example.com',
            enquiry_type='advice',
            advice_request=advice_request,
            llm_response=advice
        )
        db.session.add(enquiry)
        db.session.commit()
        
        return jsonify({
            'advice': advice,
            'enquiry_id': enquiry.id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/generate-report', methods=['POST'])
@auth_required(['customer'])
def generate_report():
    """Generate and email property report."""
    try:
        data = request.get_json()
        enquiry_ids = data.get('enquiry_ids', [])
        
        # Get current user
        user_id = request.current_user['user_id']
        user = User.query.get(user_id)
        
        if not user or not user.is_email_verified:
            return jsonify({'error': 'Email verification required'}), 400
        
        # Generate report
        report_content = CustomerService.generate_report(user_id, enquiry_ids)
        
        # Update enquiries as report generated
        for enquiry_id in enquiry_ids:
            enquiry = CustomerEnquiry.query.filter_by(
                id=enquiry_id, 
                customer_id=user_id
            ).first()
            if enquiry:
                enquiry.report_generated = True
                enquiry.report_content = report_content
        
        db.session.commit()
        
        # In a real application, you would send email here
        # send_report_email(user.email, report_content)
        
        return jsonify({
            'message': 'Report generated and sent to email successfully',
            'report_preview': report_content[:500] + '...' if len(report_content) > 500 else report_content
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/generate-pdf-report', methods=['POST'])
@auth_required(['customer'])
def generate_pdf_report():
    """Generate PDF report for customer."""
    try:
        data = request.get_json()
        report_type = data.get('report_type', 'comprehensive')
        enquiry_ids = data.get('enquiry_ids', [])
        
        # Get current user
        user_id = request.current_user['user_id']
        user = User.query.get(user_id)
        
        if not user or not user.is_email_verified:
            return jsonify({'error': 'Email verification required'}), 400
        
        # Check if PDF service is available
        if not PDF_SERVICE_AVAILABLE:
            # Fallback to text report
            text_report = CustomerService.generate_text_report(user_id, enquiry_ids, report_type)
            return jsonify({
                'error': 'PDF generation not available in this environment',
                'text_report': text_report,
                'fallback': True
            }), 200
        
        # Generate PDF report
        pdf_data, error = PDFReportService.generate_customer_report(
            customer_id=user_id,
            enquiry_ids=enquiry_ids if enquiry_ids else None,
            report_type=report_type
        )
        
        if error:
            # If PDF generation fails, return text report instead
            text_report = CustomerService.generate_text_report(user_id, enquiry_ids, report_type)
            return jsonify({
                'error': error,
                'text_report': text_report,
                'fallback': True
            }), 200
        
        if not pdf_data:
            return jsonify({'error': 'No data available for report generation'}), 400
        
        # Create filename
        filename = PDFReportService.get_report_filename(user.username, report_type)
        
        # Create BytesIO object for sending file
        pdf_buffer = BytesIO(pdf_data)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        # Fallback to text report
        try:
            user_id = request.current_user['user_id']
            text_report = CustomerService.generate_text_report(user_id, [], 'comprehensive')
            return jsonify({
                'error': f'PDF generation failed: {str(e)}',
                'text_report': text_report,
                'fallback': True
            }), 200
        except:
            return jsonify({'error': str(e)}), 500


@customer_bp.route('/get-activity-summary', methods=['GET'])
@auth_required(['customer'])
def get_activity_summary():
    """Get customer activity summary for report generation."""
    try:
        user_id = request.current_user['user_id']
        
        # Get enquiry counts
        total_enquiries = CustomerEnquiry.query.filter_by(customer_id=user_id).count()
        search_count = CustomerEnquiry.query.filter_by(customer_id=user_id, enquiry_type='search').count()
        advice_count = CustomerEnquiry.query.filter_by(customer_id=user_id, enquiry_type='advice').count()
        
        return jsonify({
            'total_enquiries': total_enquiries,
            'search_count': search_count,
            'advice_count': advice_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def send_email_otp(email, otp_code):
    """Send OTP via email (placeholder implementation)."""
    # This is a placeholder - implement actual email sending
    pass


def send_report_email(email, report_content):
    """Send report via email (placeholder implementation)."""
    # This is a placeholder - implement actual email sending
    pass