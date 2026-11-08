
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from app.decorators import role_required
from app.extensions import db
from app.models.report import Report
from app.models.response import Response
from app.models.activity_log import ActivityLog

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


# FORMAT DATA LAPORAN
def report_to_dict(report):
    return {
        'id': report.id,
        'title': report.title,
        'description': report.description,
        'status': report.status,
        'student': report.user.full_name,
        'category': report.category.name,
        'location': report.location.name,
        'building': report.location.building,
        'floor': report.location.floor,
        'created_at': report.created_at.isoformat()
            if report.created_at else None
    }


# MELIHAT SEMUA LAPORAN
@campus.route('/reports', methods=['GET'])
@login_required
@role_required('kampus')
def get_reports():
    reports = Report.query.order_by(
        Report.created_at.desc()
    ).all()

    return jsonify({
        'message': 'Daftar laporan berhasil diambil',
        'data': [report_to_dict(report) for report in reports]
    }), 200


# MELIHAT DETAIL LAPORAN
@campus.route('/reports/<int:report_id>', methods=['GET'])
@login_required
@role_required('kampus')
def get_report(report_id):
    report = Report.query.get_or_404(report_id)

    responses = []

    for response in report.responses:
        responses.append({
            'id': response.id,
            'message': response.message,
            'status_update': response.status_update,
            'user': response.user.full_name,
            'created_at': response.created_at.isoformat()
                if response.created_at else None
        })

    return jsonify({
        'message': 'Detail laporan berhasil diambil',
        'data': report_to_dict(report),
        'responses': responses
    }), 200


# MEMPERBARUI STATUS DAN MEMBERIKAN TANGGAPAN
@campus.route('/reports/<int:report_id>/status', methods=['PATCH'])
@login_required
@role_required('kampus')
def update_report_status(report_id):
    report = Report.query.get_or_404(report_id)

    data = request.get_json(silent=True) or {}

    new_status = data.get('status')
    message = data.get('message', '').strip()

    if not new_status or not message:
        return jsonify({
            'message': 'Status dan tanggapan wajib diisi'
        }), 400

    # Alur perubahan status
    allowed_transitions = {
        'menunggu_verifikasi': [
            'diverifikasi',
            'ditolak'
        ],
        'diverifikasi': [
            'sedang_diproses',
            'ditolak'
        ],
        'sedang_diproses': [
            'selesai'
        ]
    }

    allowed_statuses = allowed_transitions.get(
        report.status, []
    )

    if new_status not in allowed_statuses:
        return jsonify({
            'message': 'Perubahan status tidak diperbolehkan',
            'current_status': report.status,
            'requested_status': new_status
        }), 400

    old_status = report.status

    # Memperbarui status laporan
    report.status = new_status

    # Menyimpan tanggapan pihak kampus
    response = Response(
        message=message,
        report_id=report.id,
        user_id=current_user.id,
        status_update=new_status
    )

    # Mencatat aktivitas
    activity = ActivityLog(
        user_id=current_user.id,
        action='update_status_laporan',
        description=(
            f'Laporan #{report.id} berubah dari '
            f'{old_status} menjadi {new_status}. '
            f'Tanggapan: {message}'
        )
    )

    db.session.add(response)
    db.session.add(activity)
    db.session.commit()

    return jsonify({
        'message': 'Status laporan berhasil diperbarui',
        'data': {
            'report_id': report.id,
            'old_status': old_status,
            'new_status': report.status,
            'response': message
        }
    }), 200

