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
