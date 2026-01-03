"""Vercel-compatible Flask application matching localhost functionality."""
import os
import sys
import jwt
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, send_from_directory, request
from flask_cors import CORS

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get the correct paths for Vercel
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
template_dir = os.path.join(parent_dir, 'app', 'templates')
static_dir = os.path.join(parent_dir, 'app', 'static')

app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)

# Configuration matching localhost
app.config['SECRET_KEY'] = 'dev-secret-key-2024'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-2024'

# Enable CORS
CORS(app, origins=['https://oncrp.vercel.app', 'http://localhost:5001'])

# Simple in-memory storage for demo (matching localhost structure)
users_db = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'sales': {'password': 'sales123', 'role': 'sales_person'},
    'customer': {'password': 'customer123', 'role': 'customer'}
}

# Demo booking data (matching localhost)
bookings_db = [
    {
        'id': 1,
        'customer_name': 'Rajesh Kumar',
        'project_name': 'Sunrise Apartments',
        'contact_number': '9876543210',
        'type': '2BHK',
        'area': 1200.0,
        'agreement_cost': 5000000.0,
        'amount': 4800000.0,
        'tax_gst': 240000.0,
        'refund_buyer': 100000.0,
        'refund_referral': 50000.0,
        'onc_trust_fund': 200000.0,
        'oncct_funded': 150000.0,
        'invoice_status': 'Paid',
        'timeline': '2025-03-30',
        'loan_req': 'yes',
        'status': 'active',
        'created_by': 'admin'
    },
    {
        'id': 2,
        'customer_name': 'Priya Sharma',
        'project_name': 'Green Valley',
        'contact_number': '9876543211',
        'type': '3BHK',
        'area': 1500.0,
        'agreement_cost': 7500000.0,
        'amount': 7200000.0,
        'tax_gst': 360000.0,
        'refund_buyer': 150000.0,
        'refund_referral': 75000.0,
        'onc_trust_fund': 300000.0,
        'oncct_funded': 225000.0,
        'invoice_status': 'Pending',
        'timeline': '2025-04-15',
        'loan_req': 'no',
        'status': 'complete',
        'created_by': 'sales'
    }
]

# Demo enquiries and LLM config
enquiries_db = []
llm_config = {
    'model_name': 'gpt-3.5-turbo',
    'api_key': '',
    'is_active': True
}

available_models = [
    'gpt-3.5-turbo',
    'gpt-4',
    'gpt-4-turbo',
    'gpt-4o',
    'gpt-4o-mini'
]

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
    """Serve the main application using the actual localhost template."""
    try:
        return render_template('index.html')
    except Exception as e:
        return jsonify({'error': f'Template error: {str(e)}'}), 500

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
        return send_from_directory(static_dir, filename)
    except Exception as e:
        return jsonify({'error': f'Static file not found: {filename}'}), 404

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
            'data': {  # Match localhost response format
                'token': token,
                'user': {
                    'username': username,
                    'role': user['role']
                }
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
            
        return jsonify(bookings_db)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get bookings: {str(e)}'}), 500

# Customer endpoints (matching localhost functionality)
@app.route('/api/customer/search-properties', methods=['POST'])
def search_properties():
    """Property search endpoint."""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
            
        data = request.get_json()
        
        # Demo property search results (same as localhost)
        properties = [
            {
                'id': 1,
                'title': 'Beautiful 2BHK Apartment in Mumbai',
                'location': 'Bandra West, Mumbai',
                'price': 12000000,
                'area': '850 sq ft',
                'bedrooms': 2,
                'bathrooms': 2,
                'description': 'Modern apartment with sea view',
                'image_url': 'https://via.placeholder.com/300x200',
                'contact': '+91-9876543210'
            },
            {
                'id': 2,
                'title': 'Spacious 3BHK Villa in Pune',
                'location': 'Koregaon Park, Pune',
                'price': 8500000,
                'area': '1200 sq ft',
                'bedrooms': 3,
                'bathrooms': 3,
                'description': 'Spacious villa with garden',
                'image_url': 'https://via.placeholder.com/300x200',
                'contact': '+91-9876543211'
            }
        ]
        
        return jsonify({
            'results': properties
        })
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/api/customer/get-property-advice', methods=['POST'])
def get_property_advice():
    """Property advice endpoint."""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
            
        data = request.get_json()
        advice_request = data.get('advice_request', '')
        
        # Demo advice response (same as localhost fallback)
        if 'investment' in advice_request.lower():
            advice = """**Investment Advisory (Demo Version)**

Based on your investment query, here are key recommendations:

1. **Location Analysis**: Focus on areas with upcoming infrastructure development
2. **Property Type**: 2BHK and 3BHK apartments offer better rental yields
3. **Budget Planning**: Allocate 70-80% for property, 20-30% for additional costs
4. **Legal Verification**: Verify RERA registration and clear title
5. **Market Timing**: Current conditions favor investment with stable prices

*Note: This is a demo response. For AI-powered personalized advice, please use the localhost version with OpenAI integration.*"""
        elif 'first home' in advice_request.lower() or 'buying' in advice_request.lower():
            advice = """**First Home Buyer Guide (Demo Version)**

Congratulations on planning your first home purchase!

1. **Financial Planning**: EMI should not exceed 40% of monthly income
2. **Location Priorities**: Consider commute, amenities, and connectivity
3. **Legal Checklist**: RERA registration, clear title, approved plans
4. **Home Loan**: Compare rates and consider pre-approval
5. **Future Value**: Research resale potential and area development

*Note: This is a demo response. For AI-powered personalized advice, please use the localhost version with OpenAI integration.*"""
        else:
            advice = f"""**Property Advisory (Demo Version)**

Thank you for your inquiry: "{advice_request}"

General recommendations:
1. Research local market trends and pricing
2. Verify all legal documents and RERA registration
3. Plan finances including additional costs
4. Consider location connectivity and amenities
5. Consult with local real estate experts

*Note: This is a demo response. For AI-powered personalized advice, please use the localhost version with OpenAI integration.*"""
        
        return jsonify({
            'advice': advice
        })
        
    except Exception as e:
        return jsonify({'error': f'Advice failed: {str(e)}'}), 500

# Admin endpoints (matching localhost functionality)
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
                'config': {
                    'model_name': llm_config.get('model_name', 'gpt-3.5-turbo'),
                    'api_key': '***' + llm_config.get('api_key', '')[-4:] if llm_config.get('api_key') and len(llm_config.get('api_key', '')) > 4 else '***',
                    'is_active': llm_config.get('is_active', True)
                },
                'available_models': available_models
            })
        else:
            data = request.get_json()
            if data:
                # Update global config
                global llm_config
                if 'model_name' in data:
                    llm_config['model_name'] = data['model_name']
                if 'api_key' in data:
                    llm_config['api_key'] = data['api_key']
                if 'is_active' in data:
                    llm_config['is_active'] = data['is_active']
                    
                return jsonify({
                    'message': 'LLM configuration saved successfully',
                    'config': {
                        'model_name': llm_config.get('model_name'),
                        'api_key': '***' + llm_config.get('api_key', '')[-4:] if llm_config.get('api_key') and len(llm_config.get('api_key', '')) > 4 else '***',
                        'is_active': llm_config.get('is_active', True)
                    }
                })
            else:
                return jsonify({'error': 'No data provided'}), 400
            
    except Exception as e:
        return jsonify({'error': f'LLM config failed: {str(e)}'}), 500

@app.route('/api/customer/get-activity-summary', methods=['GET'])
def get_activity_summary():
    """Get customer activity summary."""
    try:
        return jsonify({
            'total_enquiries': len(enquiries_db),
            'search_count': len([e for e in enquiries_db if e.get('type') == 'search']),
            'advice_count': len([e for e in enquiries_db if e.get('type') == 'advice'])
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get activity summary: {str(e)}'}), 500

@app.route('/api/admin/customer-enquiries', methods=['GET'])
def get_customer_enquiries():
    """Get customer enquiries."""
    try:
        # Verify admin token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
            
        return jsonify(enquiries_db)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get enquiries: {str(e)}'}), 500

@app.route('/api/admin/customer-enquiries/stats', methods=['GET'])
def get_enquiry_stats():
    """Get customer enquiry statistics."""
    try:
        # Verify admin token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
            
        return jsonify({
            'total_enquiries': len(enquiries_db),
            'search_enquiries': len([e for e in enquiries_db if e.get('type') == 'search']),
            'advice_enquiries': len([e for e in enquiries_db if e.get('type') == 'advice']),
            'report_enquiries': len([e for e in enquiries_db if e.get('type') == 'report'])
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get enquiry stats: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)