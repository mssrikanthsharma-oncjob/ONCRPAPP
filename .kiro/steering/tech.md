# Technology Stack & Build System

## Backend Stack

- **Flask 3.1.2**: Python web framework with blueprints for modular architecture
- **SQLAlchemy 2.0.45**: Database ORM with declarative models
- **SQLite**: Database (file-based for dev, in-memory for production/serverless)
- **PyJWT 2.10.1**: JWT token authentication
- **Flask-CORS 6.0.2**: Cross-origin resource sharing
- **Werkzeug 3.1.3**: WSGI utilities and password hashing

## Frontend Stack

- **HTML5/CSS3**: Modern web standards with responsive design
- **Vanilla JavaScript (ES6+)**: No framework dependencies
- **Chart.js**: Data visualization for analytics dashboard
- **Fetch API**: HTTP client for API communication

## Testing Framework

- **pytest 9.0.2**: Unit and integration testing
- **hypothesis 6.148.8**: Property-based testing
- **22 comprehensive test cases** covering API endpoints and business logic

## Development Tools

- **python-dotenv**: Environment variable management
- **Docker**: Containerization support
- **Vercel**: Serverless deployment platform

## Common Commands

### Local Development
```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
python run.py
# Server runs on http://localhost:5001
```

### Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_booking_api.py -v
python -m pytest tests/test_analytics_api.py -v
python -m pytest tests/test_app.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Docker Deployment
```bash
# Build image
docker build -t onc-realty-booking .

# Run container
docker run -p 5001:5001 onc-realty-booking

# Docker Compose (with PostgreSQL)
docker-compose up -d
```

### Vercel Deployment
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy to production
vercel --prod

# Deploy preview
vercel
```

## Configuration Notes

- **Development**: Uses file-based SQLite (`booking_system.db`)
- **Production**: Uses in-memory SQLite for serverless compatibility
- **Testing**: Uses in-memory SQLite for isolation
- **CORS**: Configured for localhost and Vercel domains
- **JWT**: 24-hour token expiration
- **Port**: Default 5001 (configurable via environment)