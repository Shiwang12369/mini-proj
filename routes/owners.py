"""Owner management routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.owner import Owner

owners_bp = Blueprint('owners', __name__, url_prefix='/owners')


@owners_bp.route('/')
@login_required
def index():
    """List all owners."""
    search = request.args.get('search', '')
    owners = Owner.get_all(search=search if search else None)
    return render_template('owners.html', owners=owners, search=search)


@owners_bp.route('/add', methods=['POST'])
@login_required
def add():
    """Add a new owner."""
    try:
        Owner.create(
            name=request.form['name'].strip(),
            phone=request.form['phone'].strip(),
            email=request.form.get('email', '').strip() or None,
            address=request.form.get('address', '').strip() or None,
            license_number=request.form.get('license_number', '').strip() or None,
            date_of_birth=request.form.get('date_of_birth') or None
        )
        flash('Owner added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding owner: {str(e)}', 'error')
    return redirect(url_for('owners.index'))


@owners_bp.route('/edit/<int:owner_id>', methods=['POST'])
@login_required
def edit(owner_id):
    """Edit an owner."""
    try:
        Owner.update(
            owner_id=owner_id,
            name=request.form['name'].strip(),
            phone=request.form['phone'].strip(),
            email=request.form.get('email', '').strip() or None,
            address=request.form.get('address', '').strip() or None,
            license_number=request.form.get('license_number', '').strip() or None,
            date_of_birth=request.form.get('date_of_birth') or None
        )
        flash('Owner updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating owner: {str(e)}', 'error')
    return redirect(url_for('owners.index'))


@owners_bp.route('/delete/<int:owner_id>', methods=['POST'])
@login_required
def delete(owner_id):
    """Delete an owner."""
    try:
        Owner.delete(owner_id)
        flash('Owner deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting owner: {str(e)}', 'error')
    return redirect(url_for('owners.index'))


@owners_bp.route('/<int:owner_id>/vehicles')
@login_required
def vehicles(owner_id):
    """Get vehicles for an owner (JSON)."""
    from flask import jsonify
    vehicles = Owner.get_vehicles(owner_id)
    return jsonify(vehicles if vehicles else [])
