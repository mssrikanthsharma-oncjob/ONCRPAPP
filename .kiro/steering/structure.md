# Project Structure & Architecture

## Directory Organization

```
ONCRP/
├── app/                          # Main Flask application package
│   ├── __init__.py              # App factory with blueprint registration
│   ├── config.py                # Environment-specific configurations
│   ├── database.py              # Database initialization and sample data
│   ├── analytics/               # Analytics module (admin-only features)
│   │   ├── analytics_service.py # Business logic for analytics
│   │   └── routes.py           # Analytics API endpoints
│   ├── auth/                    # Authentication module
│   │   ├── auth_service.py     # JWT token handling and user auth
│   │   └── routes.py           # Auth API endpoints (/login, /verify)
│   ├── booking/                 # Booking management module
│   │   └── routes.py           # Booking CRUD API endpoints
│   ├── models/                  # SQLAlchemy database models
│   │   ├── user.py             # User model with role-based auth
│   │   └── booking.py          # Booking model with validation
│   ├── static/                  # Frontend assets
│   │   ├── css/style.css       # Application styles
│   │   └── js/                 # JavaScript modules
│   │       ├── app.js          # Main application logic
│   │       ├── auth.js         # Authentication handling
│   │       ├── bookings.js     # Booking management UI
│   │       └── analytics.js    # Analytics dashboard
│   └── templates/
│       └── index.html          # Single-page application template
├── api/                         # Vercel serverless functions
│   └── index.py                # Production entry point
├── tests/                       # Test suite
│   ├── test_app.py             # Basic Flask app tests
│   ├── test_booking_api.py     # Booking API tests
│   ├── test_analytics_api.py   # Analytics API tests
│   └── test_booking_frontend_integration.py
├── instance/                    # SQLite database files (development)
├── .kiro/                      # Kiro IDE configuration
└── run.py                      # Development server entry point
```

## Architecture Patterns

### Modular Blueprint Architecture
- Each feature area (auth, booking, analytics) is a separate Flask blueprint
- Blueprints registered with URL prefixes: `/api/auth`, `/api/bookings`, `/api/analytics`
- Clear separation of concerns between modules

### Service Layer Pattern
- Business logic separated from route handlers
- `AuthService` handles JWT tokens and user authentication
- `AnalyticsService` processes booking data for dashboard
- Models contain validation and data transformation methods

### Model-View-Controller (MVC)
- **Models**: SQLAlchemy classes in `app/models/`
- **Views**: HTML templates and JavaScript frontend
- **Controllers**: Flask route handlers in blueprint modules

### Repository Pattern (Implicit)
- SQLAlchemy ORM provides data access abstraction
- Models include query methods and data validation
- Database operations centralized in model classes

## Naming Conventions

### Files and Directories
- Snake_case for Python files: `auth_service.py`, `booking_api.py`
- Lowercase for directories: `analytics/`, `models/`
- Descriptive names indicating purpose: `routes.py`, `models.py`

### Python Code
- Classes: PascalCase (`User`, `Booking`, `AuthService`)
- Functions/methods: snake_case (`create_booking`, `validate_data`)
- Constants: UPPER_SNAKE_CASE (`JWT_SECRET_KEY`)
- Database tables: lowercase plural (`users`, `bookings`)

### API Endpoints
- RESTful conventions: GET `/api/bookings`, POST `/api/bookings`
- Resource-based URLs: `/api/bookings/{id}`
- Action endpoints: `/api/auth/login`, `/api/analytics/export`

### Frontend
- JavaScript: camelCase for variables and functions
- CSS: kebab-case for classes (`.booking-form`, `.analytics-chart`)
- HTML: semantic element names and ARIA attributes

## Configuration Management

### Environment-Based Config
- `DevelopmentConfig`: File-based SQLite, debug enabled
- `ProductionConfig`: In-memory SQLite, debug disabled
- `TestingConfig`: In-memory SQLite, testing flags enabled

### Security Practices
- JWT secrets from environment variables
- Password hashing with Werkzeug
- CORS properly configured for allowed origins
- Input validation at model and API levels

## Database Design

### User Model
- Role-based authentication (`admin`, `sales_person`)
- Password hashing and verification methods
- Audit fields (created_at, last_login)

### Booking Model
- Comprehensive financial tracking (multiple amount fields)
- Status workflow management
- Foreign key relationship to User (created_by)
- Built-in validation methods

## Frontend Architecture

### Single Page Application (SPA)
- One HTML template with dynamic content loading
- JavaScript modules for different features
- Chart.js integration for analytics visualization
- Responsive CSS design

### State Management
- JWT token stored in localStorage
- User role determines UI visibility
- Form validation on client and server side