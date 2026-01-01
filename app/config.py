"""Application configuration settings."""
import os
from datetime import timedelta


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings - Use in-memory SQLite for serverless
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # CORS settings - Add Vercel domains
    CORS_ORIGINS = [
        'http://localhost:3000', 
        'http://127.0.0.1:3000',
        'https://*.vercel.app',
        'https://vercel.app',
        'https://onc-realty-booking-system.vercel.app'
    ]
    
    # JSON settings
    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Use file-based SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///booking_system.db'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Use in-memory SQLite for Vercel serverless
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}