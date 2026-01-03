"""Simple Vercel-compatible Flask application."""
import os
import sys
import jwt
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'dev-secret-key-2024'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-2024'

# Enable CORS
CORS(app, origins=['https://oncrp.vercel.app', 'http://localhost:5001'])

# Simple in-memory storage
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
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ONC REALTY PARTNERS - Property Advisory</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 500px; margin: 50px auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #2c3e50; margin-bottom: 10px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #2c3e50; }
        .form-group input { width: 100%; padding: 12px; border: 2px solid #ecf0f1; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
        .btn { background: linear-gradient(135deg, #3498db, #2980b9); color: white; padding: 12px 30px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; width: 100%; }
        .demo-credentials { background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 25px; }
        .error-message, .success-message { padding: 12px; border-radius: 8px; margin-bottom: 20px; display: none; }
        .error-message { background: #fee; color: #c0392b; }
        .success-message { background: #efe; color: #27ae60; }
        .dashboard { display: none; }
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
                    <input type="text" id="username" required placeholder="Enter your username">
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" required placeholder="Enter your password">
                </div>
                <button type="submit" class="btn">Login</button>
            </form>
            
            <div class="demo-credentials">
                <h3>Demo Credentials</h3>
                <p><strong>Admin:</strong> admin / admin123</p>
                <p><strong>Sales:</strong> sales / sales123</p>
                <p><strong>Customer:</strong> customer / customer123</p>
            </div>
        </div>
        
        <div id="dashboard" class="dashboard">
            <div class="header">
                <h1>Welcome to ONC REALTY PARTNERS</h1>
                <p>You are logged in as: <span id="user-info"></span></p>
                <button class="btn" onclick="logout()">Logout</button>
            </div>
            <div style="margin-top: 30px; text-align: center;">
                <p>This is a demo version of the Property Advisory Platform.</p>
                <p>For full functionality including property search, AI-powered advice, and PDF reports, please use the localhost version at http://127.0.0.1:5001</p>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('login-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorDiv = document.getElementById('error-message');
            const successDiv = document.getElementById('success-message');
            
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    successDiv.textContent = 'Login successful!';
                    successDiv.style.display = 'block';
                    errorDiv.style.display = 'none';
                    
                    const token = data.data ? data.data.token : data.token;
                    const user = data.data ? data.data.user : data.user;
                    
                    localStorage.setItem('jwt_token', token);
                    localStorage.setItem('user', JSON.stringify(user));
                    
                    document.getElementById('user-info').textContent = user.username + ' (' + user.role + ')';
                    document.getElementById('login-container').style.display = 'none';
                    document.getElementById('dashboard').style.display = 'block';
                } else {
                    errorDiv.textContent = data.error || 'Login failed';
                    errorDiv.style.display = 'block';
                    successDiv.style.display = 'none';
                }
            } catch (error) {
                errorDiv.textContent = 'Network error. Please try again.';
                errorDiv.style.display = 'block';
                successDiv.style.display = 'none';
            }
        });
        
        function logout() {
            localStorage.clear();
            location.reload();
        }
        
        // Check if already logged in
        window.addEventListener('load', function() {
            const token = localStorage.getItem('jwt_token');
            const user = localStorage.getItem('user');
            if (token && user) {
                const userData = JSON.parse(user);
                document.getElementById('user-info').textContent = userData.username + ' (' + userData.role + ')';
                document.getElementById('login-container').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
            }
        });
    </script>
</body>
</html>'''

@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'ONC REALTY PARTNERS Property Advisory Platform',
        'version': '2.0.0',
        'environment': 'production'
    })

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
            'data': {
                'token': token,
                'user': {
                    'username': username,
                    'role': user['role']
                }
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)