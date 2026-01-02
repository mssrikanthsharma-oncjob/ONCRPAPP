"""Minimal Flask app for Vercel debugging."""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        'status': 'success',
        'message': 'ONC REALTY PARTNERS - Property Advisory Platform',
        'version': '1.0.0'
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'Application is running on Vercel'
    })

if __name__ == '__main__':
    app.run(debug=True)