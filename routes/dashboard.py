"""Dashboard routes with analytics."""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from models.vehicle import Vehicle
from models.challan import Challan
from models.signal import Signal
from models.owner import Owner
from models.violation import Violation

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard with statistics."""
    # Update overdue challans
    Challan.update_overdue()
    
    stats = {
        'total_vehicles': Vehicle.get_count(),
        'total_owners': Owner.get_count(),
        'total_challans': Challan.get_count(),
        'pending_challans': Challan.get_count('pending'),
        'overdue_challans': Challan.get_count('overdue'),
        'paid_challans': Challan.get_count('paid'),
        'total_revenue': Challan.get_total_revenue(),
        'pending_amount': Challan.get_pending_amount(),
        'active_signals': Signal.get_count('active'),
        'total_signals': Signal.get_count(),
        'total_violations': Violation.get_count(),
    }
    
    recent_challans = Challan.get_recent(8)
    vehicle_types = Vehicle.get_type_stats()
    
    return render_template('dashboard.html', stats=stats, recent_challans=recent_challans, vehicle_types=vehicle_types)


@dashboard_bp.route('/api/chart-data')
@login_required
def chart_data():
    """API endpoint for chart data."""
    monthly_stats = Challan.get_monthly_stats(6)
    violation_dist = Challan.get_violation_distribution()
    status_dist = Challan.get_status_distribution()
    vehicle_types = Vehicle.get_type_stats()
    
    return jsonify({
        'monthly': [{
            'month': s['month'],
            'total': s['total_challans'],
            'revenue': float(s['revenue']) if s['revenue'] else 0,
            'fines': float(s['total_fines']) if s['total_fines'] else 0
        } for s in monthly_stats] if monthly_stats else [],
        'violations': [{
            'label': v['description'],
            'count': v['count'],
            'severity': v['severity']
        } for v in violation_dist] if violation_dist else [],
        'status': [{
            'label': s['status'],
            'count': s['count']
        } for s in status_dist] if status_dist else [],
        'vehicle_types': [{
            'label': v['vehicle_type'],
            'count': v['count']
        } for v in vehicle_types] if vehicle_types else []
    })
