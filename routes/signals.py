"""Traffic signal management routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.signal import Signal

signals_bp = Blueprint('signals', __name__, url_prefix='/signals')


@signals_bp.route('/')
@login_required
def index():
    """List all traffic signals."""
    status = request.args.get('status', '')
    signals = Signal.get_all(status=status if status else None)
    return render_template('signals.html', signals=signals, status=status)


@signals_bp.route('/add', methods=['POST'])
@login_required
def add():
    """Add a new traffic signal."""
    try:
        Signal.create(
            signal_code=request.form['signal_code'].strip().upper(),
            location=request.form['location'].strip(),
            intersection=request.form.get('intersection', '').strip() or None,
            status=request.form.get('status', 'active'),
            signal_type=request.form.get('signal_type', 'standard'),
            installed_date=request.form.get('installed_date') or None
        )
        flash('Traffic signal added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding signal: {str(e)}', 'error')
    return redirect(url_for('signals.index'))


@signals_bp.route('/edit/<int:signal_id>', methods=['POST'])
@login_required
def edit(signal_id):
    """Edit a traffic signal."""
    try:
        Signal.update(
            signal_id=signal_id,
            signal_code=request.form['signal_code'].strip().upper(),
            location=request.form['location'].strip(),
            intersection=request.form.get('intersection', '').strip() or None,
            status=request.form.get('status', 'active'),
            signal_type=request.form.get('signal_type', 'standard'),
            installed_date=request.form.get('installed_date') or None,
            last_maintenance=request.form.get('last_maintenance') or None
        )
        flash('Traffic signal updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating signal: {str(e)}', 'error')
    return redirect(url_for('signals.index'))


@signals_bp.route('/delete/<int:signal_id>', methods=['POST'])
@login_required
def delete(signal_id):
    """Delete a traffic signal."""
    try:
        Signal.delete(signal_id)
        flash('Traffic signal deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting signal: {str(e)}', 'error')
    return redirect(url_for('signals.index'))


@signals_bp.route('/status/<int:signal_id>', methods=['POST'])
@login_required  
def update_status(signal_id):
    """Quick update signal status."""
    try:
        Signal.update_status(signal_id, request.form['status'])
        flash('Signal status updated!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('signals.index'))
