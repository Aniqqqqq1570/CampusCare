from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models.user import User

auth = Blueprint('auth', __name__)


# LANDING PAGE
@auth.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    return render_template('landing.html')


# REGISTER
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        nim = request.form.get('nim', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not full_name or not nim or not email or not password:
            flash('Semua kolom wajib diisi.', 'danger')
            return redirect(url_for('auth.register'))

        if len(password) < 8:
            flash('Password minimal 8 karakter.', 'danger')
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter(
            (User.email == email) | (User.nim == nim)
        ).first()

        if existing_user:
            flash('Email atau NIM sudah terdaftar.', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            full_name=full_name,
            nim=nim,
            email=email,
            password_hash=generate_password_hash(password),
            role='mahasiswa'
        )

        db.session.add(user)
        db.session.commit()

        flash('Pendaftaran berhasil. Silakan login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# LOGIN
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and user.is_active and check_password_hash(
            user.password_hash, password
        ):
            login_user(user)
            flash('Login berhasil.', 'success')

            # Arahkan pengguna berdasarkan role
            if user.role == 'admin':
                return redirect(url_for('pages.admin_dashboard'))

            elif user.role == 'kampus':
                return redirect(url_for('pages.campus_dashboard'))

            else:
                return redirect(url_for('pages.student_dashboard'))

        flash('Email atau password salah.', 'danger')

    return render_template('auth/login.html')


# DASHBOARD REDIRECT
@auth.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('pages.admin_dashboard'))

    elif current_user.role == 'kampus':
        return redirect(url_for('pages.campus_dashboard'))

    else:
        return redirect(url_for('pages.student_dashboard'))


# LOGOUT
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Kamu berhasil logout.', 'success')
    return redirect(url_for('auth.login'))
