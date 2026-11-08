from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.decorators import role_required
from app.models.user import User
from app.models.report import Report
from app.models.category import Category
from app.models.location import Location

pages = Blueprint('pages', __name__)

def status_count(query, status):
    return query.filter(Report.status == status).count()

@pages.route('/mahasiswa/dashboard')
@login_required
@role_required('mahasiswa')
def student_dashboard():
    query = Report.query.filter_by(user_id=current_user.id)
    reports = query.order_by(Report.created_at.desc()).limit(8).all()
    stats = [
        {'label': 'Total laporan', 'value': query.count(), 'icon': '▤', 'tone': 'lime'},
        {'label': 'Menunggu verifikasi', 'value': status_count(query, 'menunggu_verifikasi'), 'icon': '◷', 'tone': 'amber'},
        {'label': 'Sedang diproses', 'value': status_count(query, 'sedang_diproses'), 'icon': '↻', 'tone': 'teal'},
        {'label': 'Selesai', 'value': status_count(query, 'selesai'), 'icon': '✓', 'tone': 'green'}]
    return render_template('dashboard.html', page_title='Dashboard Mahasiswa', page_subtitle='Pantau laporan fasilitas yang kamu kirimkan.', role_label='Mahasiswa', stats=stats, reports=reports, dashboard_type='student')

@pages.route('/kampus/dashboard')
@login_required
@role_required('kampus')
def campus_dashboard():
    query = Report.query
    reports = query.order_by(Report.created_at.desc()).limit(10).all()
    stats = [
        {'label': 'Total laporan', 'value': query.count(), 'icon': '▤', 'tone': 'lime'},
        {'label': 'Menunggu verifikasi', 'value': status_count(query, 'menunggu_verifikasi'), 'icon': '◷', 'tone': 'amber'},
        {'label': 'Sedang diproses', 'value': status_count(query, 'sedang_diproses'), 'icon': '↻', 'tone': 'teal'},
        {'label': 'Selesai ditangani', 'value': status_count(query, 'selesai'), 'icon': '✓', 'tone': 'green'}]
    return render_template('dashboard.html', page_title='Dashboard Kampus', page_subtitle='Tinjau laporan dan pantau proses penanganan fasilitas.', role_label='Petugas Kampus', stats=stats, reports=reports, dashboard_type='campus')

@pages.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    query = Report.query
    reports = query.order_by(Report.created_at.desc()).limit(10).all()
    stats = [
        {'label': 'Total pengguna', 'value': User.query.count(), 'icon': '♙', 'tone': 'lime'},
        {'label': 'Mahasiswa', 'value': User.query.filter_by(role='mahasiswa').count(), 'icon': '♧', 'tone': 'teal'},
        {'label': 'Petugas kampus', 'value': User.query.filter_by(role='kampus').count(), 'icon': '⌂', 'tone': 'amber'},
        {'label': 'Total laporan', 'value': query.count(), 'icon': '▤', 'tone': 'green'}]
    overview = [
        {'label': 'Kategori aktif', 'value': Category.query.filter_by(is_active=True).count()},
        {'label': 'Lokasi aktif', 'value': Location.query.filter_by(is_active=True).count()}]
    return render_template('dashboard.html', page_title='Dashboard Admin', page_subtitle='Ringkasan pengguna dan aktivitas pelaporan CampusCare.', role_label='Administrator', stats=stats, reports=reports, overview=overview, dashboard_type='admin')


from flask import request, redirect, url_for, flash
from app.extensions import db
from app.models.response import Response as ReportResponse
from app.models.activity_log import ActivityLog
from app.routes.student import save_report_image, delete_report_image


@pages.route('/mahasiswa/laporan/buat', methods=['GET', 'POST'])
@login_required
@role_required('mahasiswa')
def student_create_report():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        try:
            category = Category.query.filter_by(id=int(request.form.get('category_id')), is_active=True).first()
            location = Location.query.filter_by(id=int(request.form.get('location_id')), is_active=True).first()
        except (TypeError, ValueError):
            category = location = None
        if not title or not description or not category or not location:
            flash('Lengkapi semua data laporan dengan benar.', 'danger')
            return redirect(url_for('pages.student_create_report'))
        try:
            image_path = save_report_image(request.files.get('image'))
        except ValueError as error:
            flash(str(error), 'danger')
            return redirect(url_for('pages.student_create_report'))
        report = Report(title=title, description=description, image_path=image_path,
            user_id=current_user.id, category_id=category.id, location_id=location.id)
        db.session.add(report)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            delete_report_image(image_path)
            raise
        flash('Laporan berhasil dikirim.', 'success')
        return redirect(url_for('pages.student_report_detail', report_id=report.id))
    return render_template('workspace.html', page_title='Buat Laporan',
        page_subtitle='Ceritakan kerusakan fasilitas kampus yang kamu temukan.',
        role_label='Mahasiswa', workspace='create_report',
        categories=Category.query.filter_by(is_active=True).order_by(Category.name).all(),
        locations=Location.query.filter_by(is_active=True).order_by(Location.name).all())


@pages.route('/mahasiswa/laporan')
@login_required
@role_required('mahasiswa')
def student_reports():
    reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).all()
    return render_template('workspace.html', page_title='Riwayat Laporan',
        page_subtitle='Semua laporan fasilitas yang pernah kamu kirim.',
        role_label='Mahasiswa', workspace='student_reports', reports=reports)


@pages.route('/mahasiswa/laporan/<int:report_id>')
@login_required
@role_required('mahasiswa')
def student_report_detail(report_id):
    report = Report.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    return render_template('workspace.html', page_title='Detail Laporan',
        page_subtitle='Informasi dan perkembangan laporan fasilitas.',
        role_label='Mahasiswa', workspace='report_detail',
        report=report, responses=report.responses)


@pages.route('/kampus/laporan')
@login_required
@role_required('kampus')
def campus_reports():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('workspace.html', page_title='Laporan Masuk',
        page_subtitle='Periksa laporan dan tindak lanjuti kerusakan fasilitas.',
        role_label='Petugas Kampus', workspace='campus_reports', reports=reports)


@pages.route('/kampus/laporan/<int:report_id>', methods=['GET', 'POST'])
@login_required
@role_required('kampus')
def campus_report_detail(report_id):
    report = Report.query.get_or_404(report_id)
    transitions = {
        'menunggu_verifikasi': ['diverifikasi', 'ditolak'],
        'diverifikasi': ['sedang_diproses', 'ditolak'],
        'sedang_diproses': ['selesai']
    }
    if request.method == 'POST':
        new_status = request.form.get('status')
        message = request.form.get('message', '').strip()
        if new_status not in transitions.get(report.status, []) or not message:
            flash('Pilih status lanjutan dan isi tanggapan.', 'danger')
            return redirect(url_for('pages.campus_report_detail', report_id=report.id))
        old_status = report.status
        report.status = new_status
        db.session.add(ReportResponse(message=message, report_id=report.id,
            user_id=current_user.id, status_update=new_status))
        db.session.add(ActivityLog(user_id=current_user.id,
            action='update_status_laporan',
            description=f'Laporan #{report.id} berubah dari {old_status} menjadi {new_status}. Tanggapan: {message}'))
        db.session.commit()
        flash('Status laporan berhasil diperbarui.', 'success')
        return redirect(url_for('pages.campus_report_detail', report_id=report.id))
    return render_template('workspace.html', page_title='Detail Laporan',
        page_subtitle='Tinjau informasi dan perbarui status penanganan.',
        role_label='Petugas Kampus', workspace='campus_report_detail',
        report=report, responses=report.responses,
        allowed_statuses=transitions.get(report.status, []))
