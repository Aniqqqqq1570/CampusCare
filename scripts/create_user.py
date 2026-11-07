import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from getpass import getpass

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models.user import User


app = create_app()


def create_user():
    print("\n=== BUAT AKUN CAMPUSCARE ===")
    print("1. Admin")
    print("2. Pihak Kampus")

    pilihan = input("Pilih role (1/2): ").strip()

    if pilihan == "1":
        role = "admin"
    elif pilihan == "2":
        role = "kampus"
    else:
        print("Pilihan tidak valid.")
        return

    full_name = input("Nama lengkap: ").strip()
    nim = input("NIM (kosongkan jika tidak ada): ").strip() or None
    email = input("Email: ").strip().lower()
    password = getpass("Password: ")

    if not full_name or not email or not password:
        print("Nama, email, dan password wajib diisi.")
        return

    if len(password) < 8:
        print("Password minimal 8 karakter.")
        return

    with app.app_context():
        existing_user = User.query.filter(
            (User.email == email) |
            ((User.nim == nim) if nim else False)
        ).first()

        if existing_user:
            print("Email atau NIM sudah digunakan.")
            return

        user = User(
            full_name=full_name,
            nim=nim,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )

        db.session.add(user)
        db.session.commit()

        print("\nAkun berhasil dibuat!")
        print("Nama:", full_name)
        print("Email:", email)
        print("Role:", role)


if __name__ == "__main__":
    create_user()
