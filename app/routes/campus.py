from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.decorators import role_required

campus = Blueprint('campus', __name__, url_prefix='/api/campus')


@campus.route('/dashboard')
@login_required
@role_required('kampus')
def dashboard():
    return jsonify({
        'message': 'Selamat datang di dashboard pihak kampus',
        'user': current_user.full_name,
        'role': current_user.role
    })