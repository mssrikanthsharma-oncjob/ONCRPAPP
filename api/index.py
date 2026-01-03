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

# Import OpenAI for LLM functionality
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

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

# In-memory storage (same as localhost for demo)
users_db = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'sales': {'password': 'sales123', 'role': 'sales_person'},
    'customer': {'password': 'customer123', 'role': 'customer'}
}

# Dummy booking records with future dates
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
        'timeline': '2025-03-15',
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
        'timeline': '2025-02-20',
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
        'timeline': '2025-04-10',
        'created_by': 'admin',
        'created_at': '2024-01-20T09:15:00'
    },
    {
        'id': 4,
        'customer_name': 'Sunita Reddy',
        'project': 'Skyline Heights',
        'contact': '+91 9876543213',
        'type': '4BHK',
        'agreement_cost': 3500000,
        'amount': 3500000,
        'tax': 350000,
        'refund': 0,
        'trust_fund': 150000,
        'status': 'active',
        'timeline': '2025-05-25',
        'created_by': 'sales',
        'created_at': '2024-01-25T11:45:00'
    },
    {
        'id': 5,
        'customer_name': 'Vikram Singh',
        'project': 'Royal Gardens',
        'contact': '+91 9876543214',
        'type': '2BHK',
        'agreement_cost': 1500000,
        'amount': 1500000,
        'tax': 150000,
        'refund': 0,
        'trust_fund': 75000,
        'status': 'active',
        'timeline': '2025-06-30',
        'created_by': 'admin',
        'created_at': '2024-02-01T16:20:00'
    },
    {
        'id': 6,
        'customer_name': 'Meera Joshi',
        'project': 'Paradise Villas',
        'contact': '+91 9876543215',
        'type': '3BHK',
        'agreement_cost': 2200000,
        'amount': 2200000,
        'tax': 220000,
        'refund': 50000,
        'trust_fund': 90000,
        'status': 'cancelled',
        'timeline': '2025-07-15',
        'created_by': 'sales',
        'created_at': '2024-02-05T09:30:00'
    },
    {
        'id': 7,
        'customer_name': 'Arjun Kapoor',
        'project': 'Metro Heights',
        'contact': '+91 9876543216',
        'type': '1BHK',
        'agreement_cost': 950000,
        'amount': 950000,
        'tax': 95000,
        'refund': 0,
        'trust_fund': 40000,
        'status': 'complete',
        'timeline': '2025-08-20',
        'created_by': 'admin',
        'created_at': '2024-02-10T14:15:00'
    },
    {
        'id': 8,
        'customer_name': 'Kavya Nair',
        'project': 'Coastal Towers',
        'contact': '+91 9876543217',
        'type': '2BHK',
        'agreement_cost': 1800000,
        'amount': 1800000,
        'tax': 180000,
        'refund': 0,
        'trust_fund': 80000,
        'status': 'active',
        'timeline': '2025-09-10',
        'created_by': 'sales',
        'created_at': '2024-02-15T12:00:00'
    }
]

enquiries_db = []
llm_config = {
    'model_name': 'gpt-3.5-turbo', 
    'api_key': '',
    'is_active': True
}

# Available LLM models
available_models = [
    'gpt-4',
    'gpt-4-turbo',
    'gpt-3.5-turbo',
    'gpt-3.5-turbo-16k',
    'claude-3-opus',
    'claude-3-sonnet',
    'claude-3-haiku'
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
    """Serve the main application."""
    try:
        return render_template('index.html')
    except Exception as e:
        # Fallback to inline HTML if template fails
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ONC REALTY PARTNERS - Property Advisory</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div id="app-container">
        <div id="login-container" class="container" style="display: flex;">
            <div class="header">
                <h1>ONC REALTY PARTNERS</h1>
                <p>Property Search & Advisory Platform</p>
            </div>
            <div class="form-container">
                <div id="error-message" class="error-message"></div>
                <div id="success-message" class="success-message"></div>
                <form id="login-form">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" required placeholder="Enter your username">
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required placeholder="Enter your password">
                    </div>
                    <button type="submit" id="login-btn" class="btn btn-primary">Login</button>
                </form>
                <div class="demo-credentials">
                    <h3>Demo Credentials</h3>
                    <p><strong>Admin:</strong> username: admin, password: admin123</p>
                    <p><strong>Sales:</strong> username: sales, password: sales123</p>
                    <p><strong>Customer:</strong> username: customer, password: customer123</p>
                </div>
            </div>
        </div>
        <div id="dashboard" class="dashboard" style="display: none;"></div>
        <div id="customer-portal" class="dashboard" style="display: none;"></div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="/static/js/auth.js"></script>
    <script src="/static/js/bookings.js"></script>
    <script src="/static/js/analytics.js"></script>
    <script src="/static/js/customer.js"></script>
    <script src="/static/js/admin.js"></script>
    <script src="/static/js/app.js"></script>
    <script>
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('user');
        document.addEventListener('DOMContentLoaded', function() {{
            window.bookingApp = new BookingApp();
        }});
    </script>
</body>
</html>
        """

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
        return jsonify({'error': f'Static file error: {str(e)}', 'file': filename, 'static_dir': static_dir}), 404

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
    """Property advice endpoint with OpenAI integration."""
    try:
        data = request.get_json()
        advice_request = data.get('advice_request', '')
        
        if not advice_request:
            return jsonify({'error': 'Advice request is required'}), 400
        
        # Get LLM-powered advice
        advice_text = get_property_advice_llm(advice_request)
        
        # Store enquiry
        enquiry = {
            'id': len(enquiries_db) + 1,
            'type': 'advice',
            'content': data,
            'advice_request': advice_request,
            'llm_response': advice_text,
            'timestamp': datetime.now().isoformat(),
            'email': data.get('email', 'anonymous')
        }
        enquiries_db.append(enquiry)
        
        return jsonify({
            'success': True,
            'advice': advice_text,
            'message': 'Property advice generated'
        })
        
    except Exception as e:
        return jsonify({'error': f'Advice failed: {str(e)}'}), 500

def get_property_advice_llm(advice_request):
    """Get property advice using OpenAI LLM (same as localhost)."""
    # Check if LLM is configured
    if not llm_config.get('api_key') or not llm_config.get('is_active'):
        return get_fallback_advice(advice_request)
    
    if not OPENAI_AVAILABLE:
        return get_fallback_advice(advice_request)
    
    try:
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=llm_config['api_key'])
        
        # Create system prompt
        system_prompt = """You are an expert real estate advisor for ONC REALTY PARTNERS, a premium property advisory firm in India. 

Your expertise includes:
- Indian real estate market trends and regulations
- Property investment strategies
- Legal compliance (RERA, stamp duty, registration)
- Location analysis and infrastructure development
- Home loan processes and financial planning
- Property valuation and market analysis

Guidelines for responses:
- Provide practical, actionable advice
- Consider Indian market conditions and regulations
- Include specific recommendations when possible
- Mention legal compliance requirements
- Be professional yet approachable
- Ask clarifying questions when needed
- Provide structured responses with clear sections

Always prioritize customer safety and legal compliance in your recommendations."""

        # Create user prompt
        user_prompt = f"""Property Advisory Request: {advice_request}

Please provide comprehensive property advice addressing the customer's query. Include relevant market insights, legal considerations, financial planning tips, and actionable next steps where applicable."""

        # Make API call to OpenAI
        response = client.chat.completions.create(
            model=llm_config.get('model_name', 'gpt-3.5-turbo'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        
        # Extract advice
        advice = response.choices[0].message.content.strip()
        
        # Add professional footer
        advice += "\n\n---\n*This advice is generated by ONC REALTY PARTNERS' AI advisory system. For personalized consultation, please contact our expert team.*"
        
        return advice
        
    except openai.AuthenticationError:
        return "Invalid OpenAI API key. Please contact administrator to verify the API key configuration."
    
    except openai.RateLimitError:
        return "OpenAI API rate limit exceeded. Please try again in a few minutes or contact administrator."
    
    except openai.APIError as e:
        return f"OpenAI API error: {str(e)}. Please try again or contact administrator."
    
    except Exception as e:
        return get_fallback_advice(advice_request)

def get_fallback_advice(advice_request):
    """Fallback advice when OpenAI is not available (same as localhost)."""
    if 'investment' in advice_request.lower():
        return """**Investment Advisory (Fallback Mode)**

Based on your investment query, here are key recommendations:

1. **Location Analysis**: Focus on areas with upcoming infrastructure development
2. **Property Type**: 2BHK and 3BHK apartments offer better rental yields
3. **Budget Planning**: Allocate 70-80% for property, 20-30% for additional costs
4. **Legal Verification**: Verify RERA registration and clear title
5. **Market Timing**: Current conditions favor investment with stable prices

*Note: This is a fallback response. For AI-powered personalized advice, please ensure OpenAI API is properly configured.*"""
    
    elif 'first home' in advice_request.lower() or 'buying' in advice_request.lower():
        return """**First Home Buyer Guide (Fallback Mode)**

Congratulations on planning your first home purchase!

1. **Financial Planning**: EMI should not exceed 40% of monthly income
2. **Location Priorities**: Consider commute, amenities, and connectivity
3. **Legal Checklist**: RERA registration, clear title, approved plans
4. **Home Loan**: Compare rates and consider pre-approval
5. **Future Value**: Research resale potential and area development

*Note: This is a fallback response. For AI-powered personalized advice, please ensure OpenAI API is properly configured.*"""
    
    else:
        return f"""**Property Advisory (Fallback Mode)**

Thank you for your inquiry: "{advice_request}"

General recommendations:
1. Research local market trends and pricing
2. Verify all legal documents and RERA registration
3. Plan finances including additional costs
4. Consider location connectivity and amenities
5. Consult with local real estate experts

*Note: This is a fallback response. For AI-powered personalized advice, please ensure OpenAI API is properly configured in the admin panel.*"""

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
@app.route('/api/admin/customer-enquiries', methods=['GET'])
def get_customer_enquiries():
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

@app.route('/api/admin/customer-enquiries/stats', methods=['GET'])
def get_enquiry_stats():
    """Get customer enquiry statistics."""
    try:
        # Verify admin token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
            
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload or payload['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
            
        # Calculate stats
        total_enquiries = len(enquiries_db)
        search_enquiries = len([e for e in enquiries_db if e['type'] == 'search'])
        advice_enquiries = len([e for e in enquiries_db if e['type'] == 'advice'])
        report_enquiries = len([e for e in enquiries_db if e['type'] == 'report'])
        
        return jsonify({
            'success': True,
            'stats': {
                'total_enquiries': total_enquiries,
                'search_enquiries': search_enquiries,
                'advice_enquiries': advice_enquiries,
                'report_enquiries': report_enquiries
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get enquiry stats: {str(e)}'}), 500

@app.route('/api/customer/get-activity-summary', methods=['GET'])
def get_activity_summary():
    """Get customer activity summary."""
    try:
        # This endpoint doesn't require authentication for demo purposes
        # In production, you might want to add customer authentication
        
        # Calculate summary from enquiries
        total_searches = len([e for e in enquiries_db if e['type'] == 'search'])
        total_advice = len([e for e in enquiries_db if e['type'] == 'advice'])
        total_reports = len([e for e in enquiries_db if e['type'] == 'report'])
        
        return jsonify({
            'success': True,
            'summary': {
                'total_searches': total_searches,
                'total_advice_requests': total_advice,
                'total_reports_generated': total_reports,
                'last_activity': enquiries_db[-1]['timestamp'] if enquiries_db else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get activity summary: {str(e)}'}), 500

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
                    'success': True,
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

if __name__ == '__main__':
    app.run(debug=True)