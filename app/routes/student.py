
import os
from uuid import uuid4

from flask import Blueprint, jsonify, request, current_app, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.decorators import role_required
from app.extensions import db
from app.models.report import Report
from app.models.category import Category
from app.models.location import Location


student = Blueprint('student', __name__, url_prefix='/api/student')

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}


# MEMBACA DATA JSON ATAU FORM
def get_request_data():
    if request.is_json:
        return request.get_json(silent=True) or {}

    return request.form


# MENYIMPAN FOTO LAPORAN
def save_report_image(file):
    if not file or not file.filename:
        return None

    filename = secure_filename(file.filename)

    if '.' not in filename:
        raise ValueError('Format foto tidak valid')

    extension = filename.rsplit('.', 1)[-1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            'Format foto harus JPG, JPEG, PNG, atau WEBP'
        )

    new_filename = f'{uuid4().hex}.{extension}'

    upload_folder = os.path.join(
        current_app.static_folder,
        'uploads',
        'reports'
    )

    os.makedirs(upload_folder, exist_ok=True)

    file.save(os.path.join(upload_folder, new_filename))

    return f'uploads/reports/{new_filename}'


# MENGHAPUS FOTO LAPORAN
def delete_report_image(image_path):
    if not image_path:
        return

    upload_folder = os.path.realpath(
        os.path.join(
            current_app.static_folder,
            'uploads',
            'reports'
        )
    )

    file_path = os.path.realpath(
        os.path.join(
            current_app.static_folder,
            image_path
        )
    )

    if os.path.commonpath([upload_folder, file_path]) == upload_folder:
        if os.path.isfile(file_path):
            os.remove(file_path)


# MENGUBAH DATA LAPORAN MENJADI JSON
def report_to_dict(report):
    return {
        'id': report.id,
        'title': report.title,
        'description': report.description,
        'status': report.status,
        'image_path': url_for(
            'static',
            filename=report.image_path
        ) if report.image_path else None,
        'category': {
            'id': report.category.id,
            'name': report.category.name
        },
        'location': {
            'id': report.location.id,
            'name': report.location.name,
            'building': report.location.building,
            'floor': report.location.floor
        },
        'created_at': report.created_at.isoformat()
            if report.created_at else None,
        'updated_at': report.updated_at.isoformat()
            if report.updated_at else None
    }


# DASHBOARD MAHASISWA
@student.route('/dashboard')
@login_required
@role_required('mahasiswa')
def dashboard():
    return jsonify({
        'message': 'Selamat datang di dashboard mahasiswa',
        'user': current_user.full_name,
        'role': current_user.role
    })
# MENAMPILKAN KATEGORI AKTIF
@student.route('/categories', methods=['GET'])
@login_required
@role_required('mahasiswa')
def get_categories():
    categories = Category.query.filter_by(
        is_active=True
    ).order_by(Category.id.asc()).all()

    return jsonify({
        'message': 'Daftar kategori berhasil diambil',
        'data': [{
            'id': category.id,
            'name': category.name,
            'description': category.description
        } for category in categories]
    }), 200


# MENAMPILKAN LOKASI AKTIF
@student.route('/locations', methods=['GET'])
@login_required
@role_required('mahasiswa')
def get_locations():
    locations = Location.query.filter_by(
        is_active=True
    ).order_by(Location.id.asc()).all()

    return jsonify({
        'message': 'Daftar lokasi berhasil diambil',
        'data': [{
            'id': location.id,
            'name': location.name,
            'building': location.building,
            'floor': location.floor,
            'description': location.description
        } for location in locations]
    }), 200

# MENAMPILKAN SEMUA LAPORAN MILIK MAHASISWA
@student.route('/reports', methods=['GET'])
@login_required
@role_required('mahasiswa')
def get_reports():
    reports = Report.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Report.created_at.desc()
    ).all()

    return jsonify({
        'message': 'Daftar laporan berhasil diambil',
        'data': [
            report_to_dict(report) for report in reports
        ]
    }), 200


# MEMBUAT LAPORAN BARU
@student.route('/reports', methods=['POST'])
@login_required
@role_required('mahasiswa')
def create_report():
    data = get_request_data()

    title = data.get('title', '').strip()
    description = data.get('description', '').strip()

    if not title or not description:
        return jsonify({
            'message': 'Judul dan deskripsi wajib diisi'
        }), 400

    try:
        category_id = int(data.get('category_id'))
        location_id = int(data.get('location_id'))
    except (TypeError, ValueError):
        return jsonify({
            'message': 'Kategori dan lokasi harus berupa ID yang valid'
        }), 400

    category = Category.query.filter_by(
        id=category_id,
        is_active=True
    ).first()

    location = Location.query.filter_by(
        id=location_id,
        is_active=True
    ).first()

    if not category or not location:
        return jsonify({
            'message': 'Kategori atau lokasi tidak ditemukan atau tidak aktif'
        }), 404

    try:
        image_path = save_report_image(
            request.files.get('image')
        )
    except ValueError as error:
        return jsonify({
            'message': str(error)
        }), 400

    report = Report(
        title=title,
        description=description,
        image_path=image_path,
        user_id=current_user.id,
        category_id=category.id,
        location_id=location.id
    )

    try:
        db.session.add(report)
        db.session.commit()
    except Exception:
        db.session.rollback()
        delete_report_image(image_path)
        raise

    return jsonify({
        'message': 'Laporan berhasil dibuat',
        'data': report_to_dict(report)
    }), 201


# MENAMPILKAN DETAIL LAPORAN
@student.route('/reports/<int:report_id>', methods=['GET'])
@login_required
@role_required('mahasiswa')
def get_report(report_id):
    report = Report.query.filter_by(
        id=report_id,
        user_id=current_user.id
    ).first_or_404()

    return jsonify({
        'message': 'Detail laporan berhasil diambil',
        'data': report_to_dict(report)
    }), 200


# MENGUBAH LAPORAN
@student.route('/reports/<int:report_id>', methods=['PUT'])
@login_required
@role_required('mahasiswa')
def update_report(report_id):
    report = Report.query.filter_by(
        id=report_id,
        user_id=current_user.id
    ).first_or_404()

    if report.status != 'menunggu_verifikasi':
        return jsonify({
            'message': 'Laporan tidak dapat diubah karena sudah diproses'
        }), 403

    data = get_request_data()

    if 'title' in data:
        title = data['title']

        if not isinstance(title, str) or not title.strip():
            return jsonify({
                'message': 'Judul tidak boleh kosong'
            }), 400

        report.title = title.strip()

    if 'description' in data:
        description = data['description']

        if not isinstance(description, str) or not description.strip():
            return jsonify({
                'message': 'Deskripsi tidak boleh kosong'
            }), 400

        report.description = description.strip()

    if 'category_id' in data:
        try:
            category_id = int(data['category_id'])
        except (TypeError, ValueError):
            return jsonify({
                'message': 'ID kategori tidak valid'
            }), 400

        category = Category.query.filter_by(
            id=category_id,
            is_active=True
        ).first()

        if not category:
            return jsonify({
                'message': 'Kategori tidak ditemukan atau tidak aktif'
            }), 404

        report.category_id = category.id

    if 'location_id' in data:
        try:
            location_id = int(data['location_id'])
        except (TypeError, ValueError):
            return jsonify({
                'message': 'ID lokasi tidak valid'
            }), 400

        location = Location.query.filter_by(
            id=location_id,
            is_active=True
        ).first()

        if not location:
            return jsonify({
                'message': 'Lokasi tidak ditemukan atau tidak aktif'
            }), 404

        report.location_id = location.id

    uploaded_file = request.files.get('image')
    new_image_path = None

    if uploaded_file and uploaded_file.filename:
        try:
            new_image_path = save_report_image(uploaded_file)
        except ValueError as error:
            return jsonify({
                'message': str(error)
            }), 400

    old_image_path = report.image_path

    if new_image_path:
        report.image_path = new_image_path

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        delete_report_image(new_image_path)
        raise

    if new_image_path:
        delete_report_image(old_image_path)

    return jsonify({
        'message': 'Laporan berhasil diperbarui',
        'data': report_to_dict(report)
    }), 200


# MENGHAPUS LAPORAN
@student.route('/reports/<int:report_id>', methods=['DELETE'])
@login_required
@role_required('mahasiswa')
def delete_report(report_id):
    report = Report.query.filter_by(
        id=report_id,
        user_id=current_user.id
    ).first_or_404()

    if report.status != 'menunggu_verifikasi':
        return jsonify({
            'message': 'Laporan tidak dapat dihapus karena sudah diproses'
        }), 403

    image_path = report.image_path

    db.session.delete(report)
    db.session.commit()

    delete_report_image(image_path)

    return jsonify({
        'message': 'Laporan berhasil dihapus'
    }), 200
