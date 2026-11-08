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
    reports = query.order_by(Report.created_at.desc()).all()
    latest_report = query.filter(Report.status.in_(['menunggu_verifikasi', 'diverifikasi', 'sedang_diproses'])).order_by(Report.updated_at.desc()).first() or query.order_by(Report.created_at.desc()).first()
    from app.models.response import Response as ReportResponse
    notification_count = ReportResponse.query.join(Report).filter(Report.user_id == current_user.id, ReportResponse.user_id != current_user.id).count()
    total = query.count()
    stats = [
        {'label': 'Total laporan saya', 'value': total, 'icon': 'assignment', 'tone': 'verified'},
        {'label': 'Menunggu verifikasi', 'value': status_count(query, 'menunggu_verifikasi'), 'icon': 'schedule', 'tone': 'waiting'},
        {'label': 'Sedang ditangani', 'value': status_count(query, 'sedang_diproses'), 'icon': 'engineering', 'tone': 'process'},
        {'label': 'Selesai & ditutup', 'value': status_count(query, 'selesai'), 'icon': 'task_alt', 'tone': 'done'}]
    return render_template('dashboard.html', page_title='Dashboard Mahasiswa',
        page_subtitle='Pantau perkembangan perbaikan sarana prasarana kampus.',
        role_label='Mahasiswa', stats=stats, reports=reports,
        latest_report=latest_report, notification_count=notification_count, dashboard_type='student')

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


from werkzeug.security import generate_password_hash


@pages.route('/admin/pengguna', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_users():
    if request.method == 'POST':
        name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'mahasiswa')
        nim = request.form.get('nim', '').strip() or None
        study_program = request.form.get('study_program', '').strip() or None
        faculty = request.form.get('faculty', '').strip() or None
        if not name or not email or len(password) < 8 or role not in ['mahasiswa', 'kampus', 'admin'] or (role == 'mahasiswa' and (not study_program or not faculty)):
            flash('Periksa kembali data pengguna. Password minimal 8 karakter.', 'danger')
            return redirect(url_for('pages.admin_users'))
        if User.query.filter_by(email=email).first() or (nim and User.query.filter_by(nim=nim).first()):
            flash('Email atau NIM sudah digunakan.', 'danger')
            return redirect(url_for('pages.admin_users'))
        user = User(full_name=name, nim=nim, study_program=study_program, faculty=faculty,
            email=email, password_hash=generate_password_hash(password), role=role)
        db.session.add(user)
        db.session.add(ActivityLog(user_id=current_user.id, action='create_user',
            description=f'Membuat akun {email}'))
        db.session.commit()
        flash('Pengguna berhasil ditambahkan.', 'success')
        return redirect(url_for('pages.admin_users'))
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('workspace.html', page_title='Manajemen Pengguna',
        page_subtitle='Kelola akun mahasiswa, petugas kampus, dan administrator.',
        role_label='Administrator', workspace='admin_users', users=users)


@pages.route('/admin/pengguna/<int:user_id>/nonaktifkan', methods=['POST'])
@login_required
@role_required('admin')
def admin_deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Kamu tidak dapat menonaktifkan akun sendiri.', 'danger')
    else:
        user.is_active = False
        db.session.add(ActivityLog(user_id=current_user.id, action='deactivate_user',
            description=f'Menonaktifkan akun {user.email}'))
        db.session.commit()
        flash('Akun pengguna dinonaktifkan.', 'success')
    return redirect(url_for('pages.admin_users'))


@pages.route('/admin/kategori', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_categories():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if not name:
            flash('Nama kategori wajib diisi.', 'danger')
        elif Category.query.filter_by(name=name).first():
            flash('Kategori sudah tersedia.', 'danger')
        else:
            db.session.add(Category(name=name, description=description, is_active=True))
            db.session.add(ActivityLog(user_id=current_user.id, action='create_category',
                description=f'Menambahkan kategori {name}'))
            db.session.commit()
            flash('Kategori berhasil ditambahkan.', 'success')
        return redirect(url_for('pages.admin_categories'))
    categories = Category.query.order_by(Category.id.asc()).all()
    return render_template('workspace.html', page_title='Manajemen Kategori',
        page_subtitle='Atur jenis kerusakan fasilitas yang dapat dipilih mahasiswa.',
        role_label='Administrator', workspace='admin_categories', categories=categories)


@pages.route('/admin/lokasi', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_locations():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        building = request.form.get('building', '').strip()
        floor = request.form.get('floor', '').strip()
        description = request.form.get('description', '').strip()
        if not name:
            flash('Nama lokasi wajib diisi.', 'danger')
        else:
            db.session.add(Location(name=name, building=building, floor=floor,
                description=description, is_active=True))
            db.session.add(ActivityLog(user_id=current_user.id, action='create_location',
                description=f'Menambahkan lokasi {name}'))
            db.session.commit()
            flash('Lokasi berhasil ditambahkan.', 'success')
        return redirect(url_for('pages.admin_locations'))
    locations = Location.query.order_by(Location.id.asc()).all()
    return render_template('workspace.html', page_title='Manajemen Lokasi',
        page_subtitle='Kelola gedung dan lokasi fasilitas kampus.',
        role_label='Administrator', workspace='admin_locations', locations=locations)


@pages.route('/admin/aktivitas')
@login_required
@role_required('admin')
def admin_activity():
    from app.models.activity_log import ActivityLog
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(100).all()
    return render_template('workspace.html', page_title='Riwayat Aktivitas',
        page_subtitle='Catatan aktivitas pengelolaan sistem CampusCare.',
        role_label='Administrator', workspace='admin_activity', logs=logs)

 
@pages.route('/laporan-publik')
@login_required
def public_reports():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('workspace.html', page_title='Laporan Publik',
        page_subtitle='Lihat laporan fasilitas kampus yang dibagikan di CampusCare.',
        role_label='Mahasiswa', workspace='public_reports', reports=reports)


@pages.route('/tentang')
@login_required
def about_campuscare():
    return render_template('workspace.html', page_title='Tentang CampusCare',
        page_subtitle='Sistem pelaporan dan pemantauan sarana prasarana kampus.',
        role_label='Mahasiswa', workspace='about_campuscare')


@pages.route('/mahasiswa/notifikasi')
@login_required
@role_required('mahasiswa')
def student_notifications():
    from app.models.response import Response as ReportResponse
    notifications = ReportResponse.query.join(Report).filter(
        Report.user_id == current_user.id,
        ReportResponse.user_id != current_user.id
    ).order_by(ReportResponse.created_at.desc()).all()
    return render_template('workspace.html', page_title='Notifikasi',
        page_subtitle='Tanggapan terbaru dari petugas untuk laporan Anda.',
        role_label='Mahasiswa', workspace='student_notifications',
        notifications=notifications)
