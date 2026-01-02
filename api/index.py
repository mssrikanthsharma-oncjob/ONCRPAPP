"""Vercel-compatible Flask application entry point."""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import Flask app
    from app import create_app
    
    # Create app instance
    app = create_app('production')
    
    # Test route for debugging
    @app.route('/test')
    def test():
        return {'status': 'working', 'message': 'Vercel deployment successful'}
        
except Exception as e:
    # Fallback minimal app for debugging
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return jsonify({'error': f'Import failed: {str(e)}', 'status': 'error'})
    
    @app.route('/api/health')
    def health():
        return jsonify({'error': f'Import failed: {str(e)}', 'status': 'error'})