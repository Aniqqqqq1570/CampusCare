from app.extensions import db


class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    building = db.Column(db.String(100))
    floor = db.Column(db.String(30))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    reports = db.relationship('Report', back_populates='location')