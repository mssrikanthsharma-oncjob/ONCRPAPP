# Product Overview

## ONC REALTY PARTNERS - Booking Management System

A comprehensive web-based booking management system for real estate transactions with role-based authentication, analytics dashboard, and comprehensive reporting capabilities.

### Core Features

- **Role-Based Authentication**: Admin and Sales person roles with JWT token authentication
- **Booking Management**: Complete CRUD operations for real estate bookings with advanced search and filtering
- **Analytics Dashboard**: Interactive charts, KPIs, and data export (Admin only)
- **Real Estate Focus**: Specialized for property transactions with Indian market data structure

### User Roles

- **Admin**: Full access including analytics dashboard, user management, and all booking operations
- **Sales Person**: Booking management only, no analytics access

### Demo Credentials

- Admin: `admin` / `admin123`
- Sales: `sales` / `sales123`

### Key Business Logic

- Bookings have multiple financial fields (agreement cost, amount, tax, refunds, trust funds)
- Status workflow: active → complete/cancelled
- Timeline-based booking management
- Property types: 1BHK, 2BHK, 3BHK, 4BHK, etc.
- Comprehensive audit trail with created_by tracking