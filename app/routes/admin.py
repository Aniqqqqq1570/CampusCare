from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.decorators import role_required

admin = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    return jsonify({
        'message': 'Selamat datang di dashboard admin',
        'user': current_user.full_name,
        'role': current_user.role
    })