"""Main Flask application for Vercel deployment."""
import os
import sys
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app, origins=['*'])

# Simple User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='sales_person')

# Simple Booking model
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    project_name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    area = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize database
with app.app_context():
    db.create_all()
    
    # Create demo users if they don't exist
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin123', role='admin')
        sales = User(username='sales', password='sales123', role='sales_person')
        db.session.add(admin)
        db.session.add(sales)
        
        # Create demo bookings
        bookings = [
            Booking(customer_name='Rajesh Kumar', contact_number='9876543210', 
                   project_name='Sunrise Apartments', type='2BHK', area=1200, amount=4800000),
            Booking(customer_name='Priya Sharma', contact_number='9876543211', 
                   project_name='Green Valley', type='3BHK', area=1500, amount=7200000),
            Booking(customer_name='Amit Patel', contact_number='9876543212', 
                   project_name='Blue Heights', type='1BHK', area=800, amount=3300000),
        ]
        
        for booking in bookings:
            db.session.add(booking)
        
        db.session.commit()

# Routes
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ONC REALTY PARTNERS - Booking System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
            button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0056b3; }
            .demo-creds { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; font-size: 12px; }
            .error { color: red; margin-top: 10px; }
            .success { color: green; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>ONC REALTY PARTNERS</h1>
                <p>Booking Management System</p>
            </div>
            
            <form id="loginForm">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <button type="submit">Login</button>
            </form>
            
            <div class="demo-creds">
                <h3>Demo Credentials</h3>
                <p><strong>Admin:</strong> username: admin, password: admin123</p>
                <p><strong>Sales:</strong> username: sales, password: sales123</p>
            </div>
            
            <div id="message"></div>
        </div>
        
        <script>
            document.getElementById('loginForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                const messageDiv = document.getElementById('message');
                
                try {
                    const response = await fetch('/api/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, password })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        messageDiv.innerHTML = '<div class="success">Login successful! Redirecting to dashboard...</div>';
                        setTimeout(() => {
                            window.location.href = '/dashboard';
                        }, 1000);
                    } else {
                        messageDiv.innerHTML = '<div class="error">' + data.error + '</div>';
                    }
                } catch (error) {
                    messageDiv.innerHTML = '<div class="error">Login failed. Please try again.</div>';
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username, password=password).first()
    
    if user:
        return jsonify({
            'success': True,
            'user': {'username': user.username, 'role': user.role}
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/dashboard')
def dashboard():
    bookings = Booking.query.all()
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ONC REALTY PARTNERS - Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #007bff; color: white; padding: 20px; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .stats {{ display: flex; gap: 20px; margin-bottom: 20px; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>ONC REALTY PARTNERS Dashboard</h1>
            <p>Booking Management System</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Total Bookings</h3>
                <h2>{len(bookings)}</h2>
            </div>
            <div class="stat-card">
                <h3>Total Revenue</h3>
                <h2>₹{sum(b.amount for b in bookings):,.0f}</h2>
            </div>
            <div class="stat-card">
                <h3>Active Bookings</h3>
                <h2>{len([b for b in bookings if b.status == 'active'])}</h2>
            </div>
        </div>
        
        <h2>Recent Bookings</h2>
        <table>
            <thead>
                <tr>
                    <th>Customer Name</th>
                    <th>Project</th>
                    <th>Type</th>
                    <th>Area (sq ft)</th>
                    <th>Amount</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {"".join([f'''
                <tr>
                    <td>{booking.customer_name}</td>
                    <td>{booking.project_name}</td>
                    <td>{booking.type}</td>
                    <td>{booking.area:,.0f}</td>
                    <td>₹{booking.amount:,.0f}</td>
                    <td>{booking.status}</td>
                </tr>
                ''' for booking in bookings])}
            </tbody>
        </table>
        
        <p style="margin-top: 30px;">
            <a href="/" style="color: #007bff;">← Back to Login</a>
        </p>
    </body>
    </html>
    '''

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'ONC REALTY PARTNERS Booking System is running',
        'bookings_count': Booking.query.count(),
        'users_count': User.query.count()
    })

if __name__ == '__main__':
    app.run(debug=True)