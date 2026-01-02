"""Analytics API routes for booking system reporting."""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app import db
from app.analytics.analytics_service import AnalyticsService
from app.auth.auth_service import auth_required

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/dashboard', methods=['GET'])
@auth_required(['admin'])
def get_dashboard_data():
    """Get comprehensive dashboard data including KPIs and charts."""
    try:
        # Parse query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        filters = _parse_filters(request.args)
        
        # Parse dates
        start_dt, end_dt = _parse_date_range(start_date, end_date)
        
        # Get KPI summary
        kpis = AnalyticsService.get_kpi_summary(start_dt, end_dt, filters)
        
        # Get chart data
        monthly_trends = AnalyticsService.get_chart_data(
            'monthly_trends', start_dt, end_dt, filters
        )
        
        project_distribution = AnalyticsService.get_chart_data(
            'project_distribution', start_dt, end_dt, filters
        )
        
        property_types = AnalyticsService.get_chart_data(
            'property_types', start_dt, end_dt, filters
        )
        
        status_distribution = AnalyticsService.get_chart_data(
            'status_distribution', start_dt, end_dt, filters
        )
        
        revenue_trends = AnalyticsService.get_chart_data(
            'revenue_trends', start_dt, end_dt, filters
        )
        
        return jsonify({
            'kpis': kpis,
            'charts': {
                'monthly_trends': monthly_trends,
                'project_distribution': project_distribution,
                'property_types': property_types,
                'status_distribution': status_distribution,
                'revenue_trends': revenue_trends
            },
            'date_range': {
                'start_date': start_dt.isoformat() if start_dt else None,
                'end_date': end_dt.isoformat() if end_dt else None
            },
            'filters_applied': filters
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@analytics_bp.route('/kpis', methods=['GET'])
@auth_required(['admin'])
def get_kpis():
    """Get key performance indicators."""
    try:
        # Parse query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        filters = _parse_filters(request.args)
        
        # Parse dates
        start_dt, end_dt = _parse_date_range(start_date, end_date)
        
        # Get KPI data
        kpis = AnalyticsService.get_kpi_summary(start_dt, end_dt, filters)
        
        return jsonify({
            'kpis': kpis,
            'date_range': {
                'start_date': start_dt.isoformat() if start_dt else None,
                'end_date': end_dt.isoformat() if end_dt else None
            },
            'filters_applied': filters
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@analytics_bp.route('/trends', methods=['GET'])
@auth_required(['admin'])
def get_trends():
    """Get booking trends over time."""
    try:
        # Parse query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        filters = _parse_filters(request.args)
        trend_type = request.args.get('type', 'monthly')  # monthly, revenue
        
        # Parse dates
        start_dt, end_dt = _parse_date_range(start_date, end_date)
        
        # Get trend data based on type
        if trend_type == 'revenue':
            group_by = request.args.get('group_by', 'month')
            trends = AnalyticsService.get_revenue_trends(start_dt, end_dt, filters, group_by)
        else:  # default to monthly booking trends
            trends = AnalyticsService.get_monthly_trends(start_dt, end_dt, filters)
        
        return jsonify({
            'trends': trends,
            'trend_type': trend_type,
            'date_range': {
                'start_date': start_dt.isoformat() if start_dt else None,
                'end_date': end_dt.isoformat() if end_dt else None
            },
            'filters_applied': filters
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@analytics_bp.route('/projects', methods=['GET'])
@auth_required(['admin'])
def get_project_analytics():
    """Get project-wise booking analytics."""
    try:
        # Parse query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        filters = _parse_filters(request.args)
        
        # Parse dates
        start_dt, end_dt = _parse_date_range(start_date, end_date)
        
        # Get project distribution data
        projects = AnalyticsService.get_project_distribution(start_dt, end_dt, filters)
        
        return jsonify({
            'projects': projects,
            'date_range': {
                'start_date': start_dt.isoformat() if start_dt else None,
                'end_date': end_dt.isoformat() if end_dt else None
            },
            'filters_applied': filters
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@analytics_bp.route('/property-types', methods=['GET'])
@auth_required(['admin'])
def get_property_type_analytics():
    """Get property type analytics."""
    try:
        # Parse query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        filters = _parse_filters(request.args)
        
        # Parse dates
        start_dt, end_dt = _parse_date_range(start_date, end_date)
        
        # Get property type analysis
        property_types = AnalyticsService.get_property_type_analysis(start_dt, end_dt, filters)
        
        return jsonify({
            'property_types': property_types,
            'date_range': {
                'start_date': start_dt.isoformat() if start_dt else None,
                'end_date': end_dt.isoformat() if end_dt else None
            },
            'filters_applied': filters
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@analytics_bp.route('/charts/<chart_type>', methods=['GET'])
@auth_required(['admin'])
def get_chart_data(chart_type):
    """Get formatted data for specific chart types."""
    try:
        # Validate chart type
        valid_chart_types = ['monthly_trends', 'project_distribution', 'property_types', 'status_distribution', 'revenue_trends']
        if chart_type not in valid_chart_types:
            return jsonify({
                'error': f'Invalid chart type. Must be one of: {", ".join(valid_chart_types)}'
            }), 400
        
        # Parse query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        filters = _parse_filters(request.args)
        
        # Parse dates
        start_dt, end_dt = _parse_date_range(start_date, end_date)
        
        # Get chart data
        chart_data = AnalyticsService.get_chart_data(chart_type, start_dt, end_dt, filters)
        
        return jsonify({
            'chart_type': chart_type,
            'chart_data': chart_data,
            'date_range': {
                'start_date': start_dt.isoformat() if start_dt else None,
                'end_date': end_dt.isoformat() if end_dt else None
            },
            'filters_applied': filters
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@analytics_bp.route('/export', methods=['GET'])
@auth_required(['admin'])
def export_analytics_data():
    """Export analytics data in various formats."""
    try:
        # Parse query parameters
        data_type = request.args.get('type', 'kpis')  # kpis, trends, projects, types
        format_type = request.args.get('format', 'json')  # json, csv_data
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        filters = _parse_filters(request.args)
        
        # Validate parameters
        valid_data_types = ['kpis', 'trends', 'projects', 'types']
        if data_type not in valid_data_types:
            return jsonify({
                'error': f'Invalid data type. Must be one of: {", ".join(valid_data_types)}'
            }), 400
        
        valid_formats = ['json', 'csv']
        if format_type not in valid_formats:
            return jsonify({
                'error': f'Invalid format. Must be one of: {", ".join(valid_formats)}'
            }), 400
        
        # Parse dates
        start_dt, end_dt = _parse_date_range(start_date, end_date)
        
        # Export data
        export_data = AnalyticsService.export_data(
            data_type, start_dt, end_dt, filters, format_type
        )
        
        # Set appropriate content type
        if format_type == 'csv':
            response = jsonify(export_data)
            response.headers['Content-Type'] = 'application/json'
        else:
            response = jsonify(export_data)
        
        return response, 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@analytics_bp.route('/filters/options', methods=['GET'])
@auth_required(['admin'])
def get_filter_options():
    """Get available filter options for analytics."""
    try:
        from app.models.booking import Booking
        from sqlalchemy import distinct
        
        # Get distinct values for filter options
        projects = [row[0] for row in db.session.query(distinct(Booking.project_name)).all()]
        property_types = [row[0] for row in db.session.query(distinct(Booking.type)).all()]
        statuses = ['active', 'complete', 'cancelled']
        
        return jsonify({
            'filter_options': {
                'projects': sorted(projects),
                'property_types': sorted(property_types),
                'statuses': statuses,
                'date_ranges': {
                    'last_7_days': (datetime.utcnow() - timedelta(days=7)).isoformat(),
                    'last_30_days': (datetime.utcnow() - timedelta(days=30)).isoformat(),
                    'last_90_days': (datetime.utcnow() - timedelta(days=90)).isoformat(),
                    'last_year': (datetime.utcnow() - timedelta(days=365)).isoformat(),
                    'current_year': datetime(datetime.utcnow().year, 1, 1).isoformat()
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


def _parse_filters(args) -> dict:
    """Parse filter parameters from request arguments."""
    filters = {}
    
    # Status filter
    if args.get('status'):
        status_list = args.get('status').split(',')
        filters['status'] = [s.strip() for s in status_list if s.strip()]
    
    # Project filter
    if args.get('project_name'):
        filters['project_name'] = args.get('project_name').strip()
    
    # Property type filter
    if args.get('property_type'):
        filters['property_type'] = args.get('property_type').strip()
    
    # Customer name filter
    if args.get('customer_name'):
        filters['customer_name'] = args.get('customer_name').strip()
    
    # Amount range filters
    if args.get('min_amount'):
        try:
            filters['min_amount'] = float(args.get('min_amount'))
        except ValueError:
            pass
    
    if args.get('max_amount'):
        try:
            filters['max_amount'] = float(args.get('max_amount'))
        except ValueError:
            pass
    
    # Area range filters
    if args.get('min_area'):
        try:
            filters['min_area'] = float(args.get('min_area'))
        except ValueError:
            pass
    
    if args.get('max_area'):
        try:
            filters['max_area'] = float(args.get('max_area'))
        except ValueError:
            pass
    
    return filters


def _parse_date_range(start_date_str, end_date_str) -> tuple:
    """Parse start and end date strings into datetime objects."""
    start_dt = None
    end_dt = None
    
    if start_date_str:
        try:
            start_dt = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS).')
    
    if end_date_str:
        try:
            end_dt = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS).')
    
    # Validate date range
    if start_dt and end_dt and start_dt > end_dt:
        raise ValueError('start_date cannot be after end_date.')
    
    return start_dt, end_dt