"""Vercel-compatible Flask application with static file serving."""
import os
import sys
from flask import Flask, jsonify, render_template, send_from_directory

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, 
           template_folder='../app/templates',
           static_folder='../app/static')

# Basic configuration
app.config['SECRET_KEY'] = 'vercel-deployment-key'

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

# Basic API endpoints for demo
@app.route('/api/demo/login', methods=['POST'])
def demo_login():
    """Demo login endpoint."""
    return jsonify({
        'message': 'Demo login - Full functionality available in local development',
        'demo_credentials': {
            'admin': 'admin/admin123',
            'sales': 'sales/sales123', 
            'customer': 'customer/customer123'
        },
        'note': 'This is a simplified version for Vercel deployment'
    })

if __name__ == '__main__':
    app.run(debug=True)