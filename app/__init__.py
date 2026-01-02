"""Main application factory."""
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from app.config import config

# Initialize extensions
db = SQLAlchemy()


def create_app(config_name='default'):
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Configure JSON handling
    app.config['JSON_SORT_KEYS'] = False
    app.json.ensure_ascii = False
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.booking.routes import booking_bp
    from app.analytics.routes import analytics_bp
    from app.customer.routes import customer_bp
    from app.admin.routes import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(booking_bp, url_prefix='/api/bookings')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(customer_bp, url_prefix='/api/customer')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Additional blueprints will be added in later tasks
    # Analytics blueprint is now registered above
    
    # Create database tables
    with app.app_context():
        from app.database import init_database
        init_database()
    
    @app.route('/api/health')
    def health_check():
        """Health check endpoint."""
        return {'status': 'healthy', 'message': 'ONC REALTY PARTNERS Booking System is running'}
    
    @app.route('/')
    def index():
        """Serve the main frontend application."""
        from flask import render_template
        return render_template('index.html')
    
    return app