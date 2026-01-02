# ONC REALTY PARTNERS - Enhanced Property Management Application

A comprehensive web-based property management application for real estate transactions with role-based authentication, analytics dashboard, and comprehensive reporting capabilities. This is an enhanced version of the original booking management system.

## 🚀 Live Demo

**GitHub Repository**: https://github.com/mssrikanthsharma-oncjob/ONCRPAPP

## 📋 Features

### 🔐 Authentication & Authorization
- **Manual Login Required** - No auto-login, users must enter credentials
- **Role-Based Access Control** - Admin and Sales person roles
- **JWT Token Authentication** - Secure session management
- **Demo Credentials Available** - Easy testing with provided accounts

### 📊 Booking Management
- **Complete CRUD Operations** - Create, Read, Update, Delete bookings
- **Advanced Search & Filtering** - Find bookings by multiple criteria
- **Real-time Data Validation** - Comprehensive input validation
- **10 Pre-loaded Demo Records** - Realistic Indian customer data

### 📈 Analytics Dashboard (Admin Only)
- **Interactive Charts** - Trends, project distribution, revenue analysis
- **Key Performance Indicators** - Total bookings, revenue, completion rates
- **Date Range Filtering** - Custom analytics periods
- **Data Export** - Download reports in JSON format
- **Responsive Design** - Works on all screen sizes

### 🎨 User Interface
- **Modern Design** - Clean, professional interface
- **Responsive Layout** - Mobile and desktop friendly
- **Loading States** - Visual feedback for all operations
- **Error Handling** - User-friendly error messages

## 🛠 Technology Stack

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Database (development)
- **PyJWT** - JWT token handling
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **HTML5/CSS3** - Modern web standards
- **JavaScript (ES6+)** - Interactive functionality
- **Chart.js** - Data visualization
- **Responsive CSS** - Mobile-first design

### Testing
- **pytest** - Unit and integration testing
- **hypothesis** - Property-based testing framework
- **22 Test Cases** - Comprehensive test coverage

### Deployment
- **Vercel Ready** - Serverless deployment configuration
- **Docker Support** - Containerized deployment option
- **Environment Configuration** - Production-ready settings

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js (for Vercel CLI)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/mssrikanthsharma-oncjob/ONCRPAPP.git
   cd ONCRPAPP
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python run.py
   ```

4. **Access the application**
   - Open browser to `http://localhost:5001`
   - Use demo credentials to login

### Demo Credentials

#### Admin Access (Full Features)
- **Username**: `admin`
- **Password**: `admin123`
- **Permissions**: All features including analytics

#### Sales Access (Limited Features)
- **Username**: `sales`
- **Password**: `sales123`
- **Permissions**: Booking management only

## 📊 Sample Data

The system comes pre-loaded with 10 realistic booking records:

| Customer | Project | Type | Amount | Status |
|----------|---------|------|---------|--------|
| Rajesh Kumar | Sunrise Apartments | 2BHK | ₹48L | Active |
| Priya Sharma | Green Valley | 3BHK | ₹72L | Complete |
| Amit Patel | Blue Heights | 1BHK | ₹33L | Active |
| Sneha Reddy | Golden Towers | 4BHK | ₹1.15Cr | Active |
| Vikram Singh | Silver Springs | 2BHK | ₹46L | Cancelled |
| *...and 5 more records* | | | | |

## 🚀 Deployment

### Vercel Deployment

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

### Docker Deployment

1. **Build Docker image**
   ```bash
   docker build -t onc-realty-booking .
   ```

2. **Run container**
   ```bash
   docker run -p 5001:5001 onc-realty-booking
   ```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_booking_api.py -v
python -m pytest tests/test_analytics_api.py -v
python -m pytest tests/test_booking_frontend_integration.py -v
```

**Test Coverage**: 22 tests covering:
- Authentication and authorization
- Booking CRUD operations
- Analytics data processing
- Frontend integration
- Error handling

## 📁 Project Structure

```
ONCRPAPP/
├── app/                          # Main application package
│   ├── analytics/               # Analytics module
│   ├── auth/                    # Authentication module
│   ├── booking/                 # Booking management module
│   ├── models/                  # Database models
│   ├── static/                  # CSS, JS, images
│   └── templates/               # HTML templates
├── api/                         # Vercel serverless functions
├── tests/                       # Test suite
├── .kiro/specs/                 # Project specifications
├── requirements.txt             # Python dependencies
├── vercel.json                  # Vercel configuration
├── Dockerfile                   # Docker configuration
└── run.py                       # Application entry point
```

## 🔧 Configuration

### Environment Variables

For production deployment, set these environment variables:

```bash
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
DATABASE_URL=your-database-url-here  # Optional
FLASK_ENV=production
```

### Database Configuration

- **Development**: SQLite (file-based)
- **Production**: SQLite (in-memory) or external database
- **Testing**: SQLite (in-memory)

## 📈 Analytics Features

### Charts Available
1. **Booking Trends** - Monthly booking counts and revenue over time
2. **Project Distribution** - Pie chart of bookings by project
3. **Revenue by Property Type** - Bar chart of revenue by property type

### KPIs Displayed
- Total Bookings
- Total Revenue
- Completion Rate
- Active Bookings

### Export Options
- JSON format data export
- Filtered data export
- Date range specific exports

## 🛡 Security Features

- **JWT Authentication** - Secure token-based authentication
- **Role-Based Access** - Different permissions for different roles
- **Input Validation** - Comprehensive data validation
- **SQL Injection Prevention** - SQLAlchemy ORM protection
- **CORS Configuration** - Proper cross-origin settings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

**ONC REALTY PARTNERS Development Team**
- Full-stack web application
- Real estate booking management
- Analytics and reporting system

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation in the `/docs` folder

---

**Built with ❤️ for ONC REALTY PARTNERS**