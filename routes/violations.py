"""Violation management routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.violation import Violation

violations_bp = Blueprint('violations', __name__, url_prefix='/violations')


@violations_bp.route('/')
@login_required
def index():
    """List all violation types."""
    severity = request.args.get('severity', '')
    violations = Violation.get_all(severity=severity if severity else None)
    return render_template('violations.html', violations=violations, severity=severity)


@violations_bp.route('/add', methods=['POST'])
@login_required
def add():
    """Add a new violation type."""
    try:
        Violation.create(
            violation_code=request.form['violation_code'].strip().upper(),
            description=request.form['description'].strip(),
            fine_amount=float(request.form['fine_amount']),
            severity=request.form['severity'],
            points=int(request.form.get('points', 0))
        )
        flash('Violation type added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding violation: {str(e)}', 'error')
    return redirect(url_for('violations.index'))


@violations_bp.route('/edit/<int:violation_id>', methods=['POST'])
@login_required
def edit(violation_id):
    """Edit a violation type."""
    try:
        Violation.update(
            violation_id=violation_id,
            violation_code=request.form['violation_code'].strip().upper(),
            description=request.form['description'].strip(),
            fine_amount=float(request.form['fine_amount']),
            severity=request.form['severity'],
            points=int(request.form.get('points', 0))
        )
        flash('Violation type updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating violation: {str(e)}', 'error')
    return redirect(url_for('violations.index'))


@violations_bp.route('/toggle/<int:violation_id>', methods=['POST'])
@login_required
def toggle(violation_id):
    """Toggle violation active status."""
    try:
        Violation.toggle_active(violation_id)
        flash('Violation status updated!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('violations.index'))
