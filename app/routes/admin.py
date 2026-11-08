
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy import func

from app.decorators import role_required
from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.models.location import Location
from app.models.report import Report
from app.models.activity_log import ActivityLog

admin = Blueprint('admin', __name__, url_prefix='/api/admin')


# ==========================================
# FUNGSI BANTU
# ==========================================

def log_activity(action, description):
    activity = ActivityLog(
        user_id=current_user.id,
        action=action,
        description=description
    )
    db.session.add(activity)


def report_to_dict(report):
    return {
        'id': report.id,
        'title': report.title,
        'description': report.description,
        'image_path': report.image_path,
        'status': report.status,
        'student': report.user.full_name,
        'category': report.category.name,
        'location': report.location.name,
        'building': report.location.building,
        'floor': report.location.floor,
        'created_at': report.created_at.isoformat()
            if report.created_at else None
    }


def user_to_dict(user):
    return {
        'id': user.id,
        'full_name': user.full_name,
        'nim': user.nim,
        'email': user.email,
        'role': user.role,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat()
            if user.created_at else None
    }


# ==========================================
# DASHBOARD DAN STATISTIK
# ==========================================

@admin.route('/dashboard', methods=['GET'])
@login_required
@role_required('admin')
def dashboard():
    total_users = User.query.count()
    total_students = User.query.filter_by(role='mahasiswa').count()
    total_campus = User.query.filter_by(role='kampus').count()
    total_reports = Report.query.count()

    status_counts = db.session.query(
        Report.status,
        func.count(Report.id)
    ).group_by(Report.status).all()

    reports_by_status = {
        status: total for status, total in status_counts
    }

    return jsonify({
        'message': 'Dashboard admin berhasil diambil',
        'data': {
            'total_users': total_users,
            'total_students': total_students,
            'total_campus': total_campus,
            'total_reports': total_reports,
            'reports_by_status': reports_by_status,
            'total_categories': Category.query.filter_by(
                is_active=True
            ).count(),
            'total_locations': Location.query.filter_by(
                is_active=True
            ).count()
        }
    }), 200


# ==========================================
# MANAJEMEN PENGGUNA
# ==========================================

@admin.route('/users', methods=['GET'])
@login_required
@role_required('admin')
def get_users():
    users = User.query.order_by(User.created_at.desc()).all()

    return jsonify({
        'message': 'Daftar pengguna berhasil diambil',
        'data': [user_to_dict(user) for user in users]
    }), 200


@admin.route('/users/<int:user_id>', methods=['GET'])
@login_required
@role_required('admin')
def get_user(user_id):
    user = User.query.get_or_404(user_id)

    return jsonify({
        'message': 'Detail pengguna berhasil diambil',
        'data': user_to_dict(user)
    }), 200


@admin.route('/users', methods=['POST'])
@login_required
@role_required('admin')
def create_user():
    data = request.get_json(silent=True) or {}

    full_name = data.get('full_name', '').strip()
    nim = data.get('nim') or None
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', 'mahasiswa')

    if not full_name or not email or not password:
        return jsonify({
            'message': 'Nama, email, dan password wajib diisi'
        }), 400

    if len(password) < 8:
        return jsonify({
            'message': 'Password minimal 8 karakter'
        }), 400

    if role not in ['mahasiswa', 'kampus', 'admin']:
        return jsonify({
            'message': 'Role tidak valid'
        }), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email sudah digunakan'}), 409

    if nim and User.query.filter_by(nim=nim).first():
        return jsonify({'message': 'NIM sudah digunakan'}), 409

    user = User(
        full_name=full_name,
        nim=nim,
        email=email,
        password_hash=generate_password_hash(password),
        role=role
    )

    db.session.add(user)
    log_activity('create_user', f'Membuat akun {email}')
    db.session.commit()

    return jsonify({
        'message': 'Pengguna berhasil ditambahkan',
        'data': user_to_dict(user)
    }), 201


@admin.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@role_required('admin')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json(silent=True) or {}

    full_name = data.get('full_name', user.full_name)
    email = data.get('email', user.email).strip().lower()
    nim = data.get('nim', user.nim) or None
    role = data.get('role', user.role)

    if not full_name or not email:
        return jsonify({
            'message': 'Nama dan email wajib diisi'
        }), 400

    if role not in ['mahasiswa', 'kampus', 'admin']:
        return jsonify({'message': 'Role tidak valid'}), 400

    email_owner = User.query.filter(
        User.email == email,
        User.id != user.id
    ).first()

    if email_owner:
        return jsonify({'message': 'Email sudah digunakan'}), 409

    if nim:
        nim_owner = User.query.filter(
            User.nim == nim,
            User.id != user.id
        ).first()

        if nim_owner:
            return jsonify({'message': 'NIM sudah digunakan'}), 409

    if user.id == current_user.id and role != 'admin':
        return jsonify({
            'message': 'Admin tidak dapat mengubah role akunnya sendiri'
        }), 400

    user.full_name = full_name
    user.email = email
    user.nim = nim
    user.role = role

    if data.get('password'):
        if len(data['password']) < 8:
            return jsonify({
                'message': 'Password minimal 8 karakter'
            }), 400

        user.password_hash = generate_password_hash(data['password'])

    log_activity('update_user', f'Memperbarui akun {email}')
    db.session.commit()

    return jsonify({
        'message': 'Pengguna berhasil diperbarui',
        'data': user_to_dict(user)
    }), 200


@admin.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@role_required('admin')
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        return jsonify({
            'message': 'Tidak dapat menonaktifkan akun sendiri'
        }), 400

    user.is_active = False

    log_activity(
        'deactivate_user',
        f'Menonaktifkan akun {user.email}'
    )
    db.session.commit()

    return jsonify({
        'message': 'Pengguna berhasil dinonaktifkan'
    }), 200


# ==========================================
# MANAJEMEN KATEGORI
# ==========================================

@admin.route('/categories', methods=['GET'])
@login_required
@role_required('admin')
def get_categories():
    categories = Category.query.order_by(Category.id.asc()).all()

    return jsonify({
        'message': 'Daftar kategori berhasil diambil',
        'data': [{
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'is_active': c.is_active
        } for c in categories]
    }), 200


@admin.route('/categories', methods=['POST'])
@login_required
@role_required('admin')
def create_category():
    data = request.get_json(silent=True) or {}

    name = data.get('name', '').strip()
    description = data.get('description', '').strip()

    if not name:
        return jsonify({'message': 'Nama kategori wajib diisi'}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({'message': 'Kategori sudah tersedia'}), 409

    category = Category(
        name=name,
        description=description,
        is_active=True
    )

    db.session.add(category)
    log_activity('create_category', f'Menambahkan kategori {name}')
    db.session.commit()

    return jsonify({
        'message': 'Kategori berhasil ditambahkan',
        'data': {
            'id': category.id,
            'name': category.name,
            'description': category.description
        }
    }), 201


@admin.route('/categories/<int:category_id>', methods=['PUT'])
@login_required
@role_required('admin')
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json(silent=True) or {}

    name = data.get('name', category.name).strip()

    if not name:
        return jsonify({'message': 'Nama kategori wajib diisi'}), 400

    existing = Category.query.filter(
        Category.name == name,
        Category.id != category.id
    ).first()

    if existing:
        return jsonify({'message': 'Nama kategori sudah digunakan'}), 409

    category.name = name
    category.description = data.get(
        'description', category.description
    )

    log_activity('update_category', f'Memperbarui kategori {name}')
    db.session.commit()

    return jsonify({
        'message': 'Kategori berhasil diperbarui'
    }), 200


@admin.route('/categories/<int:category_id>', methods=['DELETE'])
@login_required
@role_required('admin')
def deactivate_category(category_id):
    category = Category.query.get_or_404(category_id)
    category.is_active = False

    log_activity(
        'deactivate_category',
        f'Menonaktifkan kategori {category.name}'
    )
    db.session.commit()

    return jsonify({
        'message': 'Kategori berhasil dinonaktifkan'
    }), 200


# ==========================================
# MANAJEMEN LOKASI
# ==========================================

@admin.route('/locations', methods=['GET'])
@login_required
@role_required('admin')
def get_locations():
    locations = Location.query.order_by(Location.id.asc()).all()

    return jsonify({
        'message': 'Daftar lokasi berhasil diambil',
        'data': [{
            'id': loc.id,
            'name': loc.name,
            'building': loc.building,
            'floor': loc.floor,
            'description': loc.description,
            'is_active': loc.is_active
        } for loc in locations]
    }), 200


@admin.route('/locations', methods=['POST'])
@login_required
@role_required('admin')
def create_location():
    data = request.get_json(silent=True) or {}

    name = data.get('name', '').strip()

    if not name:
        return jsonify({'message': 'Nama lokasi wajib diisi'}), 400

    location = Location(
        name=name,
        building=data.get('building'),
        floor=data.get('floor'),
        description=data.get('description'),
        is_active=True
    )

    db.session.add(location)
    log_activity('create_location', f'Menambahkan lokasi {name}')
    db.session.commit()

    return jsonify({
        'message': 'Lokasi berhasil ditambahkan',
        'data': {
            'id': location.id,
            'name': location.name,
            'building': location.building,
            'floor': location.floor
        }
    }), 201


@admin.route('/locations/<int:location_id>', methods=['PUT'])
@login_required
@role_required('admin')
def update_location(location_id):
    location = Location.query.get_or_404(location_id)
    data = request.get_json(silent=True) or {}

    name = data.get('name', location.name).strip()

    if not name:
        return jsonify({'message': 'Nama lokasi wajib diisi'}), 400

    location.name = name
    location.building = data.get('building', location.building)
    location.floor = data.get('floor', location.floor)
    location.description = data.get(
        'description', location.description
    )

    log_activity('update_location', f'Memperbarui lokasi {name}')
    db.session.commit()

    return jsonify({
        'message': 'Lokasi berhasil diperbarui'
    }), 200


@admin.route('/locations/<int:location_id>', methods=['DELETE'])
@login_required
@role_required('admin')
def deactivate_location(location_id):
    location = Location.query.get_or_404(location_id)
    location.is_active = False

    log_activity(
        'deactivate_location',
        f'Menonaktifkan lokasi {location.name}'
    )
    db.session.commit()

    return jsonify({
        'message': 'Lokasi berhasil dinonaktifkan'
    }), 200


# ==========================================
# MANAJEMEN LAPORAN
# ==========================================

@admin.route('/reports', methods=['GET'])
@login_required
@role_required('admin')
def get_reports():
    query = Report.query

    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    reports = query.order_by(Report.created_at.desc()).all()

    return jsonify({
        'message': 'Daftar laporan berhasil diambil',
        'total': len(reports),
        'data': [report_to_dict(r) for r in reports]
    }), 200


@admin.route('/reports/<int:report_id>', methods=['GET'])
@login_required
@role_required('admin')
def get_report(report_id):
    report = Report.query.get_or_404(report_id)

    responses = [{
        'id': response.id,
        'message': response.message,
        'status_update': response.status_update,
        'user': response.user.full_name,
        'created_at': response.created_at.isoformat()
            if response.created_at else None
    } for response in report.responses]

    return jsonify({
        'message': 'Detail laporan berhasil diambil',
        'data': report_to_dict(report),
        'responses': responses
    }), 200


# ==========================================
# RIWAYAT AKTIVITAS
# ==========================================

@admin.route('/activity-logs', methods=['GET'])
@login_required
@role_required('admin')
def get_activity_logs():
    logs = ActivityLog.query.order_by(
        ActivityLog.created_at.desc()
    ).limit(100).all()

    return jsonify({
        'message': 'Riwayat aktivitas berhasil diambil',
        'data': [{
            'id': log.id,
            'user': log.user.full_name if log.user else 'Sistem',
            'action': log.action,
            'description': log.description,
            'created_at': log.created_at.isoformat()
                if log.created_at else None
        } for log in logs]
    }), 200
