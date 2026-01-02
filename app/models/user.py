"""User model for authentication and authorization."""
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """User model with role-based authentication."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'sales_person', 'customer', name='user_roles'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    is_email_verified = db.Column(db.Boolean, default=False, nullable=False)
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def __init__(self, username, password, role, email=None):
        """Initialize user with hashed password."""
        self.username = username
        self.set_password(password)
        self.role = role
        self.email = email
    
    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def generate_otp(self):
        """Generate and set OTP for email verification."""
        import random
        self.otp_code = str(random.randint(100000, 999999))
        self.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()
        return self.otp_code
    
    def verify_otp(self, otp_code):
        """Verify OTP code and mark email as verified."""
        if not self.otp_code or not self.otp_expires_at:
            return False
        
        if datetime.utcnow() > self.otp_expires_at:
            return False
        
        if self.otp_code == otp_code:
            self.is_email_verified = True
            self.otp_code = None
            self.otp_expires_at = None
            db.session.commit()
            return True
        
        return False
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)."""
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'email': self.email,
            'is_email_verified': self.is_email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        """String representation of user."""
        return f'<User {self.username} ({self.role})>'