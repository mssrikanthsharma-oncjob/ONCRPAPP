from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return {'message': 'Hello from Vercel!', 'status': 'working'}

@app.route('/health')
def health():
    return {'status': 'healthy', 'message': 'Test API is working'}

# For Vercel
def handler(event, context):
    return app