from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from appCalcu.models import db, User

user_bp = Blueprint('user', __name__, template_folder='templates')

@user_bp.route('/user/dashboard')
@login_required
def user_dashboard():
    if not isinstance(current_user, User):
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    return render_template('user_dashboard.html')