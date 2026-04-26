"""Vehicle management routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.vehicle import Vehicle
from models.owner import Owner

vehicles_bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')


@vehicles_bp.route('/')
@login_required
def index():
    """List all vehicles."""
    search = request.args.get('search', '')
    vehicle_type = request.args.get('type', '')
    vehicles = Vehicle.get_all(search=search if search else None, vehicle_type=vehicle_type if vehicle_type else None)
    owners = Owner.get_all()
    return render_template('vehicles.html', vehicles=vehicles, owners=owners, search=search, vehicle_type=vehicle_type)


@vehicles_bp.route('/add', methods=['POST'])
@login_required
def add():
    """Add a new vehicle."""
    try:
        Vehicle.create(
            registration_number=request.form['registration_number'].strip().upper(),
            vehicle_type=request.form['vehicle_type'],
            make=request.form.get('make', '').strip(),
            model=request.form.get('model', '').strip(),
            color=request.form.get('color', '').strip(),
            year=int(request.form['year']) if request.form.get('year') else None,
            owner_id=int(request.form['owner_id']) if request.form.get('owner_id') else None
        )
        flash('Vehicle added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding vehicle: {str(e)}', 'error')
    return redirect(url_for('vehicles.index'))


@vehicles_bp.route('/edit/<int:vehicle_id>', methods=['POST'])
@login_required
def edit(vehicle_id):
    """Edit a vehicle."""
    try:
        Vehicle.update(
            vehicle_id=vehicle_id,
            registration_number=request.form['registration_number'].strip().upper(),
            vehicle_type=request.form['vehicle_type'],
            make=request.form.get('make', '').strip(),
            model=request.form.get('model', '').strip(),
            color=request.form.get('color', '').strip(),
            year=int(request.form['year']) if request.form.get('year') else None,
            owner_id=int(request.form['owner_id']) if request.form.get('owner_id') else None
        )
        flash('Vehicle updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating vehicle: {str(e)}', 'error')
    return redirect(url_for('vehicles.index'))


@vehicles_bp.route('/delete/<int:vehicle_id>', methods=['POST'])
@login_required
def delete(vehicle_id):
    """Delete a vehicle."""
    try:
        Vehicle.delete(vehicle_id)
        flash('Vehicle deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting vehicle: {str(e)}', 'error')
    return redirect(url_for('vehicles.index'))
