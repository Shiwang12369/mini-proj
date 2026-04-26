"""Challan (Fine/Ticket) management routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.challan import Challan
from models.vehicle import Vehicle
from models.violation import Violation
from models.signal import Signal

challans_bp = Blueprint('challans', __name__, url_prefix='/challans')


@challans_bp.route('/')
@login_required
def index():
    """List all challans."""
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    challans = Challan.get_all(
        status=status if status else None,
        search=search if search else None,
        date_from=date_from if date_from else None,
        date_to=date_to if date_to else None
    )
    vehicles = Vehicle.get_all()
    violations = Violation.get_active()
    signals = Signal.get_all('active')
    
    return render_template('challans.html', challans=challans, vehicles=vehicles, 
                         violations=violations, signals=signals,
                         search=search, status=status, date_from=date_from, date_to=date_to)


@challans_bp.route('/add', methods=['POST'])
@login_required
def add():
    """Generate a new challan."""
    try:
        violation = Violation.get_by_id(int(request.form['violation_id']))
        fine_amount = violation['fine_amount'] if violation else float(request.form.get('fine_amount', 0))
        
        challan_id = Challan.create(
            vehicle_id=int(request.form['vehicle_id']),
            violation_id=int(request.form['violation_id']),
            issued_by=current_user.id,
            fine_amount=fine_amount,
            location=request.form.get('location', '').strip() or None,
            signal_id=int(request.form['signal_id']) if request.form.get('signal_id') else None,
            description=request.form.get('description', '').strip() or None,
            remarks=request.form.get('remarks', '').strip() or None
        )
        flash(f'Challan generated successfully!', 'success')
    except Exception as e:
        flash(f'Error generating challan: {str(e)}', 'error')
    return redirect(url_for('challans.index'))


@challans_bp.route('/status/<int:challan_id>', methods=['POST'])
@login_required
def update_status(challan_id):
    """Update challan status."""
    try:
        new_status = request.form['status']
        Challan.update_status(challan_id, new_status)
        flash(f'Challan status updated to {new_status}!', 'success')
    except Exception as e:
        flash(f'Error updating status: {str(e)}', 'error')
    return redirect(url_for('challans.index'))


@challans_bp.route('/view/<int:challan_id>')
@login_required
def view(challan_id):
    """View challan details (for printing)."""
    challan = Challan.get_by_id(challan_id)
    if not challan:
        flash('Challan not found.', 'error')
        return redirect(url_for('challans.index'))
    return render_template('challan_view.html', challan=challan)
