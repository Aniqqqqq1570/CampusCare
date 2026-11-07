from datetime import datetime
from app.extensions import db


class Response(db.Model):
    __tablename__ = 'responses'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)

    report_id = db.Column(
        db.Integer,
        db.ForeignKey('reports.id'),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    status_update = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    report = db.relationship('Report', back_populates='responses')
    user = db.relationship('User', back_populates='responses')