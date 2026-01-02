"""Admin routes for LLM configuration and customer enquiry management."""
from flask import Blueprint, request, jsonify
from app import db
from app.models import LLMConfig, CustomerEnquiry, User
from app.auth.auth_service import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/llm-config', methods=['GET'])
@admin_required
def get_llm_config():
    """Get current LLM configuration."""
    try:
        config = LLMConfig.get_active_config()
        
        if not config:
            return jsonify({
                'config': None,
                'available_models': [
                    'gpt-3.5-turbo',
                    'gpt-4',
                    'gpt-4-turbo',
                    'gpt-4o',
                    'gpt-4o-mini'
                ]
            }), 200
        
        return jsonify({
            'config': config.to_dict(),
            'available_models': [
                'gpt-3.5-turbo',
                'gpt-4',
                'gpt-4-turbo',
                'gpt-4o',
                'gpt-4o-mini'
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/llm-config', methods=['POST'])
@admin_required
def save_llm_config():
    """Save or update LLM configuration."""
    try:
        data = request.get_json()
        model_name = data.get('model_name')
        api_key = data.get('api_key')
        
        if not model_name or not api_key:
            return jsonify({'error': 'Model name and API key are required'}), 400
        
        # Deactivate existing configs
        existing_configs = LLMConfig.query.filter_by(is_active=True).all()
        for config in existing_configs:
            config.is_active = False
        
        # Create new config
        new_config = LLMConfig(
            model_name=model_name,
            api_key=api_key,
            is_active=True
        )
        
        db.session.add(new_config)
        db.session.commit()
        
        return jsonify({
            'message': 'LLM configuration saved successfully',
            'config': new_config.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/customer-enquiries', methods=['GET'])
@admin_required
def get_customer_enquiries():
    """Get all customer enquiries for admin dashboard."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        enquiry_type = request.args.get('type')
        
        query = CustomerEnquiry.query
        
        if enquiry_type:
            query = query.filter_by(enquiry_type=enquiry_type)
        
        enquiries = query.order_by(CustomerEnquiry.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        enquiry_data = []
        for enquiry in enquiries.items:
            data = enquiry.to_dict()
            # Add customer username
            if enquiry.customer:
                data['customer_username'] = enquiry.customer.username
            enquiry_data.append(data)
        
        return jsonify({
            'enquiries': enquiry_data,
            'pagination': {
                'page': enquiries.page,
                'pages': enquiries.pages,
                'per_page': enquiries.per_page,
                'total': enquiries.total,
                'has_next': enquiries.has_next,
                'has_prev': enquiries.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/customer-enquiries/<int:enquiry_id>', methods=['GET'])
@admin_required
def get_enquiry_details(enquiry_id):
    """Get detailed information about a specific enquiry."""
    try:
        enquiry = CustomerEnquiry.query.get(enquiry_id)
        
        if not enquiry:
            return jsonify({'error': 'Enquiry not found'}), 404
        
        data = enquiry.to_dict()
        
        # Add full report content if available
        if enquiry.report_content:
            data['full_report'] = enquiry.report_content
        
        return jsonify({'enquiry': data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/customer-enquiries/stats', methods=['GET'])
@admin_required
def get_enquiry_stats():
    """Get customer enquiry statistics."""
    try:
        total_enquiries = CustomerEnquiry.query.count()
        search_enquiries = CustomerEnquiry.query.filter_by(enquiry_type='search').count()
        advice_enquiries = CustomerEnquiry.query.filter_by(enquiry_type='advice').count()
        reports_generated = CustomerEnquiry.query.filter_by(report_generated=True).count()
        
        # Get unique customers
        unique_customers = db.session.query(CustomerEnquiry.customer_id).distinct().count()
        
        return jsonify({
            'stats': {
                'total_enquiries': total_enquiries,
                'search_enquiries': search_enquiries,
                'advice_enquiries': advice_enquiries,
                'reports_generated': reports_generated,
                'unique_customers': unique_customers
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/customers', methods=['GET'])
@admin_required
def get_customers():
    """Get all customers for admin dashboard."""
    try:
        customers = User.query.filter_by(role='customer').order_by(User.created_at.desc()).all()
        
        customer_data = []
        for customer in customers:
            data = customer.to_dict()
            # Add enquiry count
            enquiry_count = CustomerEnquiry.query.filter_by(customer_id=customer.id).count()
            data['enquiry_count'] = enquiry_count
            customer_data.append(data)
        
        return jsonify({'customers': customer_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500