from flask import Flask, request, jsonify
import os
import sys

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import and create the Flask app
from app import create_app

app = create_app('production')

# This is the entry point for Vercel
def handler(event, context):
    return app

# Also export the app directly
application = app