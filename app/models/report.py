from datetime import datetime
from app.extensions import db


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255))

    status = db.Column(
        db.String(30),
        nullable=False,
        default='menunggu_verifikasi'
    )

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = db.relationship('User', back_populates='reports')
    category = db.relationship('Category', back_populates='reports')
    location = db.relationship('Location', back_populates='reports')
    responses = db.relationship(
        'Response',
        back_populates='report',
        cascade='all, delete-orphan'
    )