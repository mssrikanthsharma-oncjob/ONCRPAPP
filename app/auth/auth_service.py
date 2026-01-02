"""Authentication service with JWT token management."""
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify
from app.models import User
from app import db


class AuthService:
    """Service class for handling authentication operations."""
    
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate user with username and password."""
        if not username or not password:
            return None, "Username and password are required"
        
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if not user or not user.check_password(password):
            return None, "Invalid username or password"
        
        # Update last login timestamp
        user.update_last_login()
        
        return user, None
    
    @staticmethod
    def generate_token(user):
        """Generate JWT token for authenticated user."""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
        return token
    
    @staticmethod
    def verify_token(token):
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Check if user still exists and is active
            user = User.query.filter_by(
                id=payload['user_id'],
                is_active=True
            ).first()
            
            if not user:
                return None, "User not found or inactive"
            
            return payload, None
            
        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"
    
    @staticmethod
    def login(username, password):
        """Complete login process with token generation."""
        user, error = AuthService.authenticate_user(username, password)
        
        if error:
            return None, error
        
        token = AuthService.generate_token(user)
        
        return {
            'token': token,
            'user': user.to_dict(),
            'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()
        }, None


def token_required(f):
    """Decorator to require valid JWT token for protected routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload, error = AuthService.verify_token(token)
        
        if error:
            return jsonify({'error': error}), 401
        
        # Add user info to request context
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """Decorator to require admin role for protected routes."""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated


def auth_required(allowed_roles=None):
    """Decorator to require specific roles for protected routes."""
    if allowed_roles is None:
        allowed_roles = ['admin', 'sales_person', 'customer']
    
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            user_role = request.current_user['role']
            
            if user_role not in allowed_roles:
                return jsonify({'error': f'Access denied. Required roles: {allowed_roles}'}), 403
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator