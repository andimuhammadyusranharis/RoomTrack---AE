from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time

db = SQLAlchemy()

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    booked_by_name = db.Column(db.String(120), nullable=True)
    booked_by_nim = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<Room {self.name}>'


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)

    # Data user
    name = db.Column(db.String(120), nullable=False)
    nim = db.Column(db.String(50), nullable=False)

    # Data ruangan
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)

    # Jadwal booking
    booking_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    # Lainnya
    reason = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False)

    room = db.relationship('Room', backref=db.backref('bookings', lazy=True))

    def __repr__(self):
        return f'<Booking {self.id} {self.name}>'
