"""LLM configuration model for admin settings."""
from datetime import datetime
from app import db


class LLMConfig(db.Model):
    """Model for storing LLM configuration settings."""
    
    __tablename__ = 'llm_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False, default='gpt-3.5-turbo')
    api_key = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert config to dictionary (excluding sensitive data)."""
        return {
            'id': self.id,
            'model_name': self.model_name,
            'api_key': '***' + self.api_key[-4:] if self.api_key and len(self.api_key) > 4 else '***',
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_dict_full(self):
        """Convert config to dictionary with full API key (for internal use)."""
        return {
            'id': self.id,
            'model_name': self.model_name,
            'api_key': self.api_key,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_active_config():
        """Get the active LLM configuration."""
        return LLMConfig.query.filter_by(is_active=True).first()
    
    def __repr__(self):
        """String representation of LLM config."""
        return f'<LLMConfig {self.model_name}>'