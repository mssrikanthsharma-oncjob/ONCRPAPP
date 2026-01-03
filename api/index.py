"""Simplified Vercel-compatible Flask application."""
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

# Configuration
app.config['SECRET_KEY'] = 'dev-secret-key-2024'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-2024'

# Enable CORS
CORS(app, origins=['https://oncrp.vercel.app', 'http://localhost:5001'])

# Simple in-memory storage for demo
users_db = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'sales': {'password': 'sales123', 'role': 'sales_person'},
    'customer': {'password': 'customer123', 'role': 'customer'}
}

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
        # Fallback HTML if template fails
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ONC REALTY PARTNERS - Property Advisory</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #2c3e50; margin-bottom: 10px; }}
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
        .form-group input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
        .btn {{ background: #3498db; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        .btn:hover {{ background: #2980b9; }}
        .demo-credentials {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin-top: 20px; }}
        .demo-credentials h3 {{ margin-top: 0; color: #2c3e50; }}
        .error-message {{ color: #e74c3c; margin-bottom: 15px; display: none; }}
        .success-message {{ color: #27ae60; margin-bottom: 15px; display: none; }}
        .dashboard {{ display: none; }}
        .dashboard.active {{ display: block; }}
        .nav-tabs {{ display: flex; margin-bottom: 20px; border-bottom: 2px solid #ecf0f1; }}
        .nav-tab {{ padding: 10px 20px; cursor: pointer; border: none; background: none; font-size: 16px; }}
        .nav-tab.active {{ background: #3498db; color: white; }}
        .tab-content {{ padding: 20px 0; }}
        .form-group textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; min-height: 100px; }}
        .advice-result {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin-top: 20px; white-space: pre-wrap; }}
    </style>
</head>
<body>
    <div class="container">
        <div id="login-container">
            <div class="header">
                <h1>ONC REALTY PARTNERS</h1>
                <p>Property Search & Advisory Platform</p>
            </div>
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
                <button type="submit" class="btn">Login</button>
            </form>
            <div class="demo-credentials">
                <h3>Demo Credentials</h3>
                <p><strong>Admin:</strong> username: admin, password: admin123</p>
                <p><strong>Sales:</strong> username: sales, password: sales123</p>
                <p><strong>Customer:</strong> username: customer, password: customer123</p>
            </div>
        </div>
        
        <div id="dashboard" class="dashboard">
            <div class="header">
                <h1>ONC REALTY PARTNERS</h1>
                <p>Welcome, <span id="user-name"></span>!</p>
                <button class="btn" onclick="logout()">Logout</button>
            </div>
            
            <div id="customer-portal" style="display: none;">
                <div class="nav-tabs">
                    <button class="nav-tab active" onclick="showTab('search')">Search Property</button>
                    <button class="nav-tab" onclick="showTab('advice')">Advise Property</button>
                    <button class="nav-tab" onclick="showTab('report')">Generate Report</button>
                </div>
                
                <div id="search-tab" class="tab-content">
                    <h3>Property Search</h3>
                    <form id="search-form">
                        <div class="form-group">
                            <label>Location</label>
                            <input type="text" id="search-location" placeholder="Enter location">
                        </div>
                        <div class="form-group">
                            <label>Property Type</label>
                            <select id="search-type">
                                <option value="">Any</option>
                                <option value="1BHK">1BHK</option>
                                <option value="2BHK">2BHK</option>
                                <option value="3BHK">3BHK</option>
                            </select>
                        </div>
                        <button type="submit" class="btn">Search Properties</button>
                    </form>
                    <div id="search-results"></div>
                </div>
                
                <div id="advice-tab" class="tab-content" style="display: none;">
                    <h3>Property Advisory</h3>
                    <form id="advice-form">
                        <div class="form-group">
                            <label>Your Property Question</label>
                            <textarea id="advice-request" placeholder="Ask your property-related question..."></textarea>
                        </div>
                        <button type="submit" class="btn">Get Advice</button>
                    </form>
                    <div id="advice-results"></div>
                </div>
                
                <div id="report-tab" class="tab-content" style="display: none;">
                    <h3>Generate Report</h3>
                    <p>This is a demo version. For full report generation with PDF export, please use the localhost version.</p>
                    <button class="btn" onclick="alert('Demo: Report generation feature available in localhost version')">Generate Demo Report</button>
                </div>
            </div>
            
            <div id="admin-portal" style="display: none;">
                <h3>Admin Dashboard</h3>
                <p>This is a demo version. For full admin functionality, please use the localhost version.</p>
            </div>
            
            <div id="sales-portal" style="display: none;">
                <h3>Sales Dashboard</h3>
                <p>This is a demo version. For full sales functionality, please use the localhost version.</p>
            </div>
        </div>
    </div>
    
    <script>
        let currentUser = null;
        
        // Check if already logged in
        window.addEventListener('load', function() {{
            const token = localStorage.getItem('jwt_token');
            const user = localStorage.getItem('user');
            if (token && user) {{
                currentUser = JSON.parse(user);
                showDashboard();
            }}
        }});
        
        document.getElementById('login-form').addEventListener('submit', async function(e) {{
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorDiv = document.getElementById('error-message');
            const successDiv = document.getElementById('success-message');
            
            try {{
                const response = await fetch('/api/auth/login', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ username, password }})
                }});
                
                const data = await response.json();
                
                if (response.ok) {{
                    successDiv.textContent = 'Login successful!';
                    successDiv.style.display = 'block';
                    errorDiv.style.display = 'none';
                    localStorage.setItem('jwt_token', data.token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    currentUser = data.user;
                    setTimeout(showDashboard, 1000);
                }} else {{
                    errorDiv.textContent = data.error || 'Login failed';
                    errorDiv.style.display = 'block';
                    successDiv.style.display = 'none';
                }}
            }} catch (error) {{
                errorDiv.textContent = 'Network error. Please try again.';
                errorDiv.style.display = 'block';
                successDiv.style.display = 'none';
            }}
        }});
        
        function showDashboard() {{
            document.getElementById('login-container').style.display = 'none';
            document.getElementById('dashboard').style.display = 'block';
            document.getElementById('user-name').textContent = currentUser.username;
            
            // Show appropriate portal based on role
            if (currentUser.role === 'customer') {{
                document.getElementById('customer-portal').style.display = 'block';
            }} else if (currentUser.role === 'admin') {{
                document.getElementById('admin-portal').style.display = 'block';
            }} else if (currentUser.role === 'sales_person') {{
                document.getElementById('sales-portal').style.display = 'block';
            }}
        }}
        
        function logout() {{
            localStorage.clear();
            location.reload();
        }}
        
        function showTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
            document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName + '-tab').style.display = 'block';
            event.target.classList.add('active');
        }}
        
        // Property search
        document.getElementById('search-form').addEventListener('submit', async function(e) {{
            e.preventDefault();
            const location = document.getElementById('search-location').value;
            const type = document.getElementById('search-type').value;
            
            try {{
                const response = await fetch('/api/customer/search-property', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ location, property_type: type }})
                }});
                
                const data = await response.json();
                const resultsDiv = document.getElementById('search-results');
                
                if (data.success) {{
                    resultsDiv.innerHTML = '<h4>Search Results:</h4>' + 
                        data.properties.map(p => `<div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
                            <h5>${{p.title}}</h5>
                            <p><strong>Price:</strong> ${{p.price}}</p>
                            <p><strong>Location:</strong> ${{p.location}}</p>
                        </div>`).join('');
                }} else {{
                    resultsDiv.innerHTML = '<p style="color: red;">Search failed. Please try again.</p>';
                }}
            }} catch (error) {{
                document.getElementById('search-results').innerHTML = '<p style="color: red;">Network error. Please try again.</p>';
            }}
        }});
        
        // Property advice
        document.getElementById('advice-form').addEventListener('submit', async function(e) {{
            e.preventDefault();
            const request = document.getElementById('advice-request').value;
            
            if (!request.trim()) {{
                alert('Please enter your question');
                return;
            }}
            
            try {{
                const response = await fetch('/api/customer/advise-property', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ advice_request: request }})
                }});
                
                const data = await response.json();
                const resultsDiv = document.getElementById('advice-results');
                
                if (data.success) {{
                    resultsDiv.innerHTML = '<div class="advice-result"><h4>Property Advice:</h4>' + data.advice + '</div>';
                }} else {{
                    resultsDiv.innerHTML = '<p style="color: red;">Advice request failed. Please try again.</p>';
                }}
            }} catch (error) {{
                document.getElementById('advice-results').innerHTML = '<p style="color: red;">Network error. Please try again.</p>';
            }}
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
        return jsonify({'error': f'Static file not found: {filename}'}), 404

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

# Simple demo endpoints
@app.route('/api/customer/search-property', methods=['POST'])
def search_property():
    """Demo property search."""
    return jsonify({
        'success': True,
        'properties': [
            {'id': 1, 'title': '2BHK Apartment in Mumbai', 'price': '₹1.2 Cr', 'location': 'Bandra West'},
            {'id': 2, 'title': '3BHK Villa in Pune', 'price': '₹85 Lakh', 'location': 'Koregaon Park'},
            {'id': 3, 'title': '1BHK Studio in Delhi', 'price': '₹75 Lakh', 'location': 'Connaught Place'}
        ],
        'message': 'Demo property search results'
    })

@app.route('/api/customer/advise-property', methods=['POST'])
def advise_property():
    """Demo property advice."""
    data = request.get_json()
    advice_request = data.get('advice_request', '')
    
    # Simple demo advice based on keywords
    if 'investment' in advice_request.lower():
        advice = """**Investment Advisory (Demo Version)**

Based on your investment query, here are key recommendations:

1. **Location Analysis**: Focus on areas with upcoming infrastructure development
2. **Property Type**: 2BHK and 3BHK apartments offer better rental yields
3. **Budget Planning**: Allocate 70-80% for property, 20-30% for additional costs
4. **Legal Verification**: Verify RERA registration and clear title
5. **Market Timing**: Current conditions favor investment with stable prices

*Note: This is a demo response. For AI-powered personalized advice with OpenAI integration, please use the localhost version.*"""
    elif 'first home' in advice_request.lower() or 'buying' in advice_request.lower():
        advice = """**First Home Buyer Guide (Demo Version)**

Congratulations on planning your first home purchase!

1. **Financial Planning**: EMI should not exceed 40% of monthly income
2. **Location Priorities**: Consider commute, amenities, and connectivity
3. **Legal Checklist**: RERA registration, clear title, approved plans
4. **Home Loan**: Compare rates and consider pre-approval
5. **Future Value**: Research resale potential and area development

*Note: This is a demo response. For AI-powered personalized advice with OpenAI integration, please use the localhost version.*"""
    else:
        advice = f"""**Property Advisory (Demo Version)**

Thank you for your inquiry: "{advice_request}"

General recommendations:
1. Research local market trends and pricing
2. Verify all legal documents and RERA registration
3. Plan finances including additional costs
4. Consider location connectivity and amenities
5. Consult with local real estate experts

*Note: This is a demo response. For AI-powered personalized advice with OpenAI integration, please use the localhost version.*"""
    
    return jsonify({
        'success': True,
        'advice': advice,
        'message': 'Demo advice generated'
    })

if __name__ == '__main__':
    app.run(debug=True)