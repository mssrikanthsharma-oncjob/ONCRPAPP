"""Vercel serverless function entry point for full Flask app."""
import os
import sys

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import the full Flask application
from app import create_app

# Create the Flask application in production mode
app = create_app('production')

# Export for Vercel (this is the entry point Vercel will use)
def handler(request, context):
    return app

# Also make the app available directly
application = app