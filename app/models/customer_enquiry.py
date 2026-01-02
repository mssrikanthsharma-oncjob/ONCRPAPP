"""Customer enquiry model for tracking property searches and advice requests."""
from datetime import datetime
from app import db


class CustomerEnquiry(db.Model):
    """Model for tracking customer property enquiries."""
    
    __tablename__ = 'customer_enquiries'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    enquiry_type = db.Column(db.Enum('search', 'advice', name='enquiry_types'), nullable=False)
    search_criteria = db.Column(db.Text, nullable=True)  # JSON string of search filters
    advice_request = db.Column(db.Text, nullable=True)   # Customer's advice requirements
    llm_response = db.Column(db.Text, nullable=True)     # LLM generated advice
    report_generated = db.Column(db.Boolean, default=False, nullable=False)
    report_content = db.Column(db.Text, nullable=True)   # Generated report content
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    customer = db.relationship('User', backref='enquiries')
    
    def to_dict(self):
        """Convert enquiry to dictionary."""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_username': self.customer.username if self.customer else None,
            'email': self.email,
            'enquiry_type': self.enquiry_type,
            'search_criteria': self.search_criteria,
            'advice_request': self.advice_request,
            'llm_response': self.llm_response,
            'report_generated': self.report_generated,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        """String representation of enquiry."""
        return f'<CustomerEnquiry {self.id} ({self.enquiry_type})>'