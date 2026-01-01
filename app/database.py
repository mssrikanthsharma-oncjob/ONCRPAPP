"""Database initialization and management utilities."""
from datetime import datetime, timedelta
from app import db
from app.models import User, Booking


def init_database():
    """Initialize database tables and create demo users and bookings."""
    # Create all tables
    db.create_all()
    
    # Always recreate demo data for production (since we use in-memory SQLite)
    # Check if demo users already exist
    admin_user = User.query.filter_by(username='admin').first()
    sales_user = User.query.filter_by(username='sales').first()
    
    # Create demo admin user if not exists
    if not admin_user:
        admin_user = User(
            username='admin',
            password='admin123',
            role='admin'
        )
        db.session.add(admin_user)
    
    # Create demo sales person if not exists
    if not sales_user:
        sales_user = User(
            username='sales',
            password='sales123',
            role='sales_person'
        )
        db.session.add(sales_user)
    
    # Commit users first to get their IDs
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating users: {e}")
        raise
    
    # Always create dummy bookings (important for in-memory database)
    if Booking.query.count() == 0:
        create_dummy_bookings()
    
    print("Database initialized successfully with demo users:")
    print("- Admin: username='admin', password='admin123'")
    print("- Sales: username='sales', password='sales123'")
    print(f"- {Booking.query.count()} booking records available")


def create_dummy_bookings():
    """Create 10 dummy booking records for demonstration."""
    dummy_bookings = [
        {
            'customer_name': 'Rajesh Kumar',
            'contact_number': '9876543210',
            'project_name': 'Sunrise Apartments',
            'type': '2BHK',
            'area': 1200.0,
            'agreement_cost': 5000000.0,
            'amount': 4800000.0,
            'tax_gst': 240000.0,
            'refund_buyer': 100000.0,
            'refund_referral': 50000.0,
            'onc_trust_fund': 200000.0,
            'oncct_funded': 150000.0,
            'invoice_status': 'Paid',
            'timeline': datetime.utcnow() + timedelta(days=30),
            'loan_req': 'yes',
            'status': 'active'
        },
        {
            'customer_name': 'Priya Sharma',
            'contact_number': '9876543211',
            'project_name': 'Green Valley',
            'type': '3BHK',
            'area': 1500.0,
            'agreement_cost': 7500000.0,
            'amount': 7200000.0,
            'tax_gst': 360000.0,
            'refund_buyer': 150000.0,
            'refund_referral': 75000.0,
            'onc_trust_fund': 300000.0,
            'oncct_funded': 225000.0,
            'invoice_status': 'Pending',
            'timeline': datetime.utcnow() + timedelta(days=45),
            'loan_req': 'no',
            'status': 'complete'
        },
        {
            'customer_name': 'Amit Patel',
            'contact_number': '9876543212',
            'project_name': 'Blue Heights',
            'type': '1BHK',
            'area': 800.0,
            'agreement_cost': 3500000.0,
            'amount': 3300000.0,
            'tax_gst': 165000.0,
            'refund_buyer': 70000.0,
            'refund_referral': 35000.0,
            'onc_trust_fund': 140000.0,
            'oncct_funded': 105000.0,
            'invoice_status': 'Paid',
            'timeline': datetime.utcnow() + timedelta(days=60),
            'loan_req': 'yes',
            'status': 'active'
        },
        {
            'customer_name': 'Sneha Reddy',
            'contact_number': '9876543213',
            'project_name': 'Golden Towers',
            'type': '4BHK',
            'area': 2200.0,
            'agreement_cost': 12000000.0,
            'amount': 11500000.0,
            'tax_gst': 575000.0,
            'refund_buyer': 240000.0,
            'refund_referral': 120000.0,
            'onc_trust_fund': 480000.0,
            'oncct_funded': 360000.0,
            'invoice_status': 'Paid',
            'timeline': datetime.utcnow() + timedelta(days=90),
            'loan_req': 'no',
            'status': 'active'
        },
        {
            'customer_name': 'Vikram Singh',
            'contact_number': '9876543214',
            'project_name': 'Silver Springs',
            'type': '2BHK',
            'area': 1100.0,
            'agreement_cost': 4800000.0,
            'amount': 4600000.0,
            'tax_gst': 230000.0,
            'refund_buyer': 96000.0,
            'refund_referral': 48000.0,
            'onc_trust_fund': 192000.0,
            'oncct_funded': 144000.0,
            'invoice_status': 'Overdue',
            'timeline': datetime.utcnow() - timedelta(days=15),
            'loan_req': 'yes',
            'status': 'cancelled'
        },
        {
            'customer_name': 'Meera Joshi',
            'contact_number': '9876543215',
            'project_name': 'Sunrise Apartments',
            'type': '3BHK',
            'area': 1600.0,
            'agreement_cost': 8000000.0,
            'amount': 7700000.0,
            'tax_gst': 385000.0,
            'refund_buyer': 160000.0,
            'refund_referral': 80000.0,
            'onc_trust_fund': 320000.0,
            'oncct_funded': 240000.0,
            'invoice_status': 'Paid',
            'timeline': datetime.utcnow() + timedelta(days=75),
            'loan_req': 'no',
            'status': 'complete'
        },
        {
            'customer_name': 'Arjun Gupta',
            'contact_number': '9876543216',
            'project_name': 'Ocean View',
            'type': '2BHK',
            'area': 1300.0,
            'agreement_cost': 6200000.0,
            'amount': 5900000.0,
            'tax_gst': 295000.0,
            'refund_buyer': 124000.0,
            'refund_referral': 62000.0,
            'onc_trust_fund': 248000.0,
            'oncct_funded': 186000.0,
            'invoice_status': 'Pending',
            'timeline': datetime.utcnow() + timedelta(days=120),
            'loan_req': 'yes',
            'status': 'active'
        },
        {
            'customer_name': 'Kavya Nair',
            'contact_number': '9876543217',
            'project_name': 'Green Valley',
            'type': '1BHK',
            'area': 750.0,
            'agreement_cost': 3200000.0,
            'amount': 3000000.0,
            'tax_gst': 150000.0,
            'refund_buyer': 64000.0,
            'refund_referral': 32000.0,
            'onc_trust_fund': 128000.0,
            'oncct_funded': 96000.0,
            'invoice_status': 'Paid',
            'timeline': datetime.utcnow() + timedelta(days=40),
            'loan_req': 'no',
            'status': 'complete'
        },
        {
            'customer_name': 'Rohit Agarwal',
            'contact_number': '9876543218',
            'project_name': 'Blue Heights',
            'type': '3BHK',
            'area': 1450.0,
            'agreement_cost': 7800000.0,
            'amount': 7500000.0,
            'tax_gst': 375000.0,
            'refund_buyer': 156000.0,
            'refund_referral': 78000.0,
            'onc_trust_fund': 312000.0,
            'oncct_funded': 234000.0,
            'invoice_status': 'Paid',
            'timeline': datetime.utcnow() + timedelta(days=100),
            'loan_req': 'yes',
            'status': 'active'
        },
        {
            'customer_name': 'Anita Desai',
            'contact_number': '9876543219',
            'project_name': 'Golden Towers',
            'type': '2BHK',
            'area': 1250.0,
            'agreement_cost': 5800000.0,
            'amount': 5500000.0,
            'tax_gst': 275000.0,
            'refund_buyer': 116000.0,
            'refund_referral': 58000.0,
            'onc_trust_fund': 232000.0,
            'oncct_funded': 174000.0,
            'invoice_status': 'Pending',
            'timeline': datetime.utcnow() + timedelta(days=80),
            'loan_req': 'no',
            'status': 'active'
        }
    ]
    
    # Get admin user for created_by field
    admin_user = User.query.filter_by(username='admin').first()
    
    for booking_data in dummy_bookings:
        booking = Booking(
            customer_name=booking_data['customer_name'],
            contact_number=booking_data['contact_number'],
            project_name=booking_data['project_name'],
            type=booking_data['type'],
            area=booking_data['area'],
            agreement_cost=booking_data['agreement_cost'],
            amount=booking_data['amount'],
            tax_gst=booking_data['tax_gst'],
            refund_buyer=booking_data['refund_buyer'],
            refund_referral=booking_data['refund_referral'],
            onc_trust_fund=booking_data['onc_trust_fund'],
            oncct_funded=booking_data['oncct_funded'],
            invoice_status=booking_data['invoice_status'],
            timeline=booking_data['timeline'],
            loan_req=booking_data['loan_req'],
            status=booking_data['status'],
            created_by=admin_user.id if admin_user else 1
        )
        db.session.add(booking)
    
    try:
        db.session.commit()
        print(f"Created {len(dummy_bookings)} dummy booking records")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating dummy bookings: {e}")
        raise


def reset_database():
    """Drop and recreate all database tables."""
    db.drop_all()
    init_database()


def create_user(username, password, role):
    """Create a new user with the specified credentials and role."""
    if User.query.filter_by(username=username).first():
        raise ValueError(f"User '{username}' already exists")
    
    if role not in ['admin', 'sales_person']:
        raise ValueError(f"Invalid role '{role}'. Must be 'admin' or 'sales_person'")
    
    user = User(username=username, password=password, role=role)
    db.session.add(user)
    db.session.commit()
    
    return user