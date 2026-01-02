"""Vercel-compatible Flask application entry point."""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import Flask app
    from app import create_app
    
    # Create app instance with production config
    app = create_app('production')
    
    # Override database configuration for serverless
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database with sample data
    with app.app_context():
        from app.database import init_db
        init_db()
        
except Exception as e:
    # Fallback minimal app for debugging
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return jsonify({
            'error': f'Import failed: {str(e)}', 
            'status': 'error',
            'message': 'Please check server logs for details'
        })
    
    @app.route('/api/health')
    def health():
        return jsonify({
            'error': f'Import failed: {str(e)}', 
            'status': 'error'
        })