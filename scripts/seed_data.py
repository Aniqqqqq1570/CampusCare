
import sys
import os

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

from app import create_app
from app.extensions import db
from app.models.category import Category
from app.models.location import Location

app = create_app()

with app.app_context():

    # Data kategori
    categories = [
        Category(
            name='Kerusakan Elektronik',
            description='Kerusakan perangkat elektronik kampus'
        ),
        Category(
            name='Kerusakan Bangunan',
            description='Kerusakan fasilitas fisik bangunan'
        ),
        Category(
            name='Kerusakan Furniture',
            description='Kerusakan meja, kursi, dan perabot'
        ),
        Category(
            name='Kebersihan',
            description='Masalah kebersihan lingkungan kampus'
        ),
        Category(
            name='Fasilitas Umum',
            description='Kerusakan fasilitas umum kampus'
        )
    ]

    # Data lokasi
    locations = [
        Location(name='Ruang Kelas', building='Gedung A', floor='1'),
        Location(name='Laboratorium', building='Gedung B', floor='2'),
        Location(name='Perpustakaan', building='Gedung C', floor='1'),
        Location(name='Toilet', building='Gedung A', floor='1'),
        Location(name='Area Parkir', building='Area Kampus')
    ]

    for category in categories:
        if not Category.query.filter_by(name=category.name).first():
            db.session.add(category)

    for location in locations:
        if not Location.query.filter_by(
            name=location.name,
            building=location.building
        ).first():
            db.session.add(location)

    db.session.commit()

    print('Data kategori dan lokasi berhasil ditambahkan!')
