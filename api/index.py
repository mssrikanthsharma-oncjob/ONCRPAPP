"""Vercel-compatible Flask application with full localhost functionality."""
import os
import sys
import jwt
import hashlib
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, send_from_directory, request
from flask_cors import CORS

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, 
           template_folder='../app/templates',
           static_folder='../app/static')

# Configuration matching localhost
app.config['SECRET_KEY'] = 'dev-secret-key-2024'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-2024'

# Enable CORS
CORS(app, origins=['https://oncrp.vercel.app', 'http://localhost:5001'])

# In-memory storage (same as localhost for demo)
users_db = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'sales': {'password': 'sales123', 'role': 'sales_person'},
    'customer': {'password': 'customer123', 'role': 'customer'}
}

# Dummy booking records
bookings_db = [
    {
        'id': 1,
        'customer_name': 'Rajesh Kumar',
        'project': 'Sunrise Apartments',
        'contact': '+91 9876543210',
        'type': '2BHK',
        'agreement_cost': 1200000,
        'amount': 1200000,
        'tax': 120000,
        'refund': 0,
        'trust_fund': 50000,
        'status': 'active',
        'timeline': '2024-03-15',
        'created_by': 'admin',
        'created_at': '2024-01-15T10:30:00'
    },
    {
        'id': 2,
        'customer_name': 'Priya Sharma',
        'project': 'Green Valley Villas',
        'contact': '+91 9876543211',
        'type': '3BHK',
        'agreement_cost': 2500000,
        'amount': 2500000,
        'tax': 250000,
        'refund': 0,
        'trust_fund': 100000,
        'status': 'complete',
        'timeline': '2024-02-20',
        'created_by': 'sales',
        'created_at': '2024-01-10T14:20:00'
    },
    {
        'id': 3,
        'customer_name': 'Amit Patel',
        'project': 'Ocean View Towers',
        'contact': '+91 9876543212',
        'type': '1BHK',
        'agreement_cost': 800000,
        'amount': 800000,
        'tax': 80000,
        'refund': 25000,
        'trust_fund': 30000,
        'status': 'active',
        'timeline': '2024-04-10',
        'created_by': 'admin',
        'created_at': '2024-01-20T09:15:00'
    }
]

enquiries_db = []
llm_config = {'model': 'gpt-3.5-turbo', 'api_key': ''}

def generate_token(username, role):
    """Generate JWT token."""
    payload = {
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route('/')
def index():
    """Serve the main application."""
    try:
        return render_template('index.html')
    except Exception as e:
        return jsonify({
            'error': f'Template error: {str(e)}',
            'message': 'ONC REALTY PARTNERS - Property Advisory Platform',
            'status': 'template_error'
        })

@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'ONC REALTY PARTNERS Property Advisory Platform',
        'version': '2.0.0',
        'environment': 'production'
    })

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    try:
        return send_from_directory('../app/static', filename)
    except Exception as e:
        return jsonify({'error': f'Static file error: {str(e)}'}), 404

# Authentication endpoints (matching localhost exactly)
@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
            
        user = users_db.get(username)
        if not user or user['password'] != password:
            return jsonify({'error': 'Invalid credentials'}), 401
            
        token = generate_token(username, user['role'])
        
        return jsonify({
            'token': token,
            'user': {
                'username': username,
                'role': user['role']
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/auth/verify', methods=['POST'])
def verify():
    """Token verification endpoint."""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token required'}), 400
            
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
            
        return jsonify({
            'valid': True,
            'user': {
                'username': payload['username'],
                'role': payload['role']
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Verification failed: {str(e)}'}), 500

# Customer endpoints (matching localhost functionality)
@app.route('/api/customer/search-property', methods=['POST'])
def search_property():
    """Property search endpoint."""
    try:
        data = request.get_json()
        
        # Demo property search results (same as localhost)
        properties = [
            {
                'id': 1,
                'title': '2BHK Apartment in Bandra',
                'location': 'Bandra West, Mumbai',
                'price': '₹1.2 Cr',
                'area': '850 sq ft',
                'type': '2BHK',
                'description': 'Modern apartment with sea view'
            },
            {
                'id': 2,
                'title': '3BHK Villa in Pune',
                'location': 'Koregaon Park, Pune',
                'price': '₹85 Lakh',
                'area': '1200 sq ft',
                'type': '3BHK',
                'description': 'Spacious villa with garden'
            },
            {
                'id': 3,
                'title': '1BHK Studio in Andheri',
                'location': 'Andheri East, Mumbai',
                'price': '₹75 Lakh',
                'area': '450 sq ft',
                'type': '1BHK',
                'description': 'Compact studio near metro'
            }
        ]
        
        # Store enquiry
        enquiry = {
            'id': len(enquiries_db) + 1,
            'type': 'search',
            'content': data,
            'results': properties,
            'timestamp': datetime.now().isoformat(),
            'email': data.get('email', 'anonymous')
        }
        enquiries_db.append(enquiry)
        
        return jsonify({
            'success': True,
            'properties': properties,
            'message': 'Property search completed'
        })
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/api/customer/advise-property', methods=['POST'])
def advise_property():
    """Property advice endpoint."""
    try:
        data = request.get_json()
        
        # Demo advice response (same as localhost)
        advice = {
            'recommendation': 'Based on your requirements, I recommend looking for properties in Bandra or Andheri areas.',
            'factors': [
                'Good connectivity to business districts',
                'Excellent schools and hospitals nearby',
                'Strong appreciation potential',
                'Well-developed infrastructure'
            ],
            'budget_analysis': 'Your budget is suitable for the selected property types in these areas.',
            'next_steps': [
                'Visit shortlisted properties',
                'Check legal documents',
                'Negotiate price based on market rates',
                'Consider loan pre-approval'
            ]
        }
        
        # Store enquiry
        enquiry = {
            'id': len(enquiries_db) + 1,
            'type': 'advice',
            'content': data,
            'advice': advice,
            'timestamp': datetime.now().isoformat(),
            'email': data.get('email', 'anonymous')
        }
        enquiries_db.append(enquiry)
        
        return jsonify({
            'success': True,
            'advice': advice,
            'message': 'Property advice generated'
        })
        
    except Exception as e:
        return jsonify({'error': f'Advice failed: {str(e)}'}), 500

@app.route('/api/customer/send-otp', methods=['POST'])
def send_otp():
    """Send OTP for email verification."""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email required'}), 400
            
        # Demo OTP (same as localhost)
        otp = '123456'
        
        return jsonify({
            'success': True,
            'message': f'OTP sent to {email}',
            'demo_otp': otp  # Remove in production
        })
        
    except Exception as e:
        return jsonify({'error': f'OTP send failed: {str(e)}'}), 500

@app.route('/api/customer/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP."""
    try:
        data = request.get_json()
        email = data.get('email')
        otp = data.get('otp')
        
        if not email or not otp:
            return jsonify({'error': 'Email and OTP required'}), 400
            
        # Demo verification (accept 123456)
        if otp == '123456':
            return jsonify({
                'success': True,
                'message': 'Email verified successfully'
            })
        else:
            return jsonify({'error': 'Invalid OTP'}), 400
            
    except Exception as e:
        return jsonify({'error': f'OTP verification failed: {str(e)}'}), 500

@app.route('/api/customer/generate-report', methods=['POST'])
def generate_report():
    """Generate PDF report."""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email required'}), 400
            
        # Demo report generation (same as localhost)
        report_data = {
            'report_id': f'RPT_{len(enquiries_db) + 1}',
            'generated_at': datetime.now().isoformat(),
            'email': email,
            'summary': 'Property search and advice report generated successfully',
            'download_url': f'/api/customer/download-report/RPT_{len(enquiries_db) + 1}'
        }
        
        # Store enquiry
        enquiry = {
            'id': len(enquiries_db) + 1,
            'type': 'report',
            'content': data,
            'report': report_data,
            'timestamp': datetime.now().isoformat(),
            'email': email
        }
        enquiries_db.append(enquiry)
        
        return jsonify({
            'success': True,
            'report': report_data,
            'message': 'Report generated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

# Booking endpoints (matching localhost functionality)
@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    """Get all bookings."""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
            
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
            
        return jsonify({
            'success': True,
            'bookings': bookings_db
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get bookings: {str(e)}'}), 500

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    """Create a new booking."""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
            
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
            
        data = request.get_json()
        
        # Create new booking
        new_booking = {
            'id': len(bookings_db) + 1,
            'customer_name': data.get('customer_name'),
            'project': data.get('project'),
            'contact': data.get('contact'),
            'type': data.get('type'),
            'agreement_cost': float(data.get('agreement_cost', 0)),
            'amount': float(data.get('amount', 0)),
            'tax': float(data.get('tax', 0)),
            'refund': float(data.get('refund', 0)),
            'trust_fund': float(data.get('trust_fund', 0)),
            'status': data.get('status', 'active'),
            'timeline': data.get('timeline'),
            'created_by': payload['username'],
            'created_at': datetime.now().isoformat()
        }
        
        bookings_db.append(new_booking)
        
        return jsonify({
            'success': True,
            'booking': new_booking,
            'message': 'Booking created successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to create booking: {str(e)}'}), 500

@app.route('/api/bookings/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    """Update a booking."""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
            
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
            
        data = request.get_json()
        
        # Find booking
        booking = None
        for b in bookings_db:
            if b['id'] == booking_id:
                booking = b
                break
                
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
            
        # Update booking
        booking.update({
            'customer_name': data.get('customer_name', booking['customer_name']),
            'project': data.get('project', booking['project']),
            'contact': data.get('contact', booking['contact']),
            'type': data.get('type', booking['type']),
            'agreement_cost': float(data.get('agreement_cost', booking['agreement_cost'])),
            'amount': float(data.get('amount', booking['amount'])),
            'tax': float(data.get('tax', booking['tax'])),
            'refund': float(data.get('refund', booking['refund'])),
            'trust_fund': float(data.get('trust_fund', booking['trust_fund'])),
            'status': data.get('status', booking['status']),
            'timeline': data.get('timeline', booking['timeline'])
        })
        
        return jsonify({
            'success': True,
            'booking': booking,
            'message': 'Booking updated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to update booking: {str(e)}'}), 500

@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    """Delete a booking."""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
            
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
            
        # Find and remove booking
        global bookings_db
        bookings_db = [b for b in bookings_db if b['id'] != booking_id]
        
        return jsonify({
            'success': True,
            'message': 'Booking deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete booking: {str(e)}'}), 500

# Analytics endpoints (matching localhost functionality)
@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get analytics summary."""
    try:
        # Verify admin token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
            
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload or payload['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
            
        # Calculate analytics from bookings
        total_bookings = len(bookings_db)
        active_bookings = len([b for b in bookings_db if b['status'] == 'active'])
        completed_bookings = len([b for b in bookings_db if b['status'] == 'complete'])
        total_revenue = sum(b['amount'] for b in bookings_db)
        
        return jsonify({
            'success': True,
            'summary': {
                'total_bookings': total_bookings,
                'active_bookings': active_bookings,
                'completed_bookings': completed_bookings,
                'total_revenue': total_revenue,
                'average_booking_value': total_revenue / total_bookings if total_bookings > 0 else 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get analytics: {str(e)}'}), 500

# Admin endpoints (matching localhost functionality)
@app.route('/api/admin/enquiries', methods=['GET'])
def get_enquiries():
    """Get customer enquiries."""
    try:
        # Verify admin token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
            
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload or payload['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
            
        return jsonify({
            'success': True,
            'enquiries': enquiries_db
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get enquiries: {str(e)}'}), 500

@app.route('/api/admin/llm-config', methods=['GET', 'POST'])
def llm_config_endpoint():
    """LLM configuration endpoint."""
    try:
        # Verify admin token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
            
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload or payload['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
            
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'config': llm_config
            })
        else:
            data = request.get_json()
            llm_config.update(data)
            return jsonify({
                'success': True,
                'message': 'LLM configuration saved',
                'config': llm_config
            })
            
    except Exception as e:
        return jsonify({'error': f'LLM config failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)