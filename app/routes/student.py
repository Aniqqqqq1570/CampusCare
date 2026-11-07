from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.decorators import role_required

student = Blueprint('student', __name__, url_prefix='/api/student')


@student.route('/dashboard')
@login_required
@role_required('mahasiswa')
def dashboard():
    return jsonify({
        'message': 'Selamat datang di dashboard mahasiswa',
        'user': current_user.full_name,
        'role': current_user.role
    })