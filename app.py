from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Room, Booking
from datetime import datetime
import os

app = Flask(__name__, template_folder='templates')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///roomtrack.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# secret key sederhana untuk session (ganti sebelum ujian/demo)
app.secret_key = os.environ.get('SECRET_KEY', 'this-should-be-changed')

db.init_app(app)

# helper function untuk cek login
def is_logged_in():
    return 'name' in session and 'nim' in session

@app.route('/', methods=['GET'])
def index():
    # halaman login jika belum login, langsung ke dashboard jika sudah
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    name = request.form.get('name', '').strip()
    nim = request.form.get('nim', '').strip()
    if not name or not nim:
        flash('Nama dan NIM harus diisi.', 'error')
        return redirect(url_for('login'))
    # simpan di session (login sederhana)
    session['name'] = name
    session['nim'] = nim
    flash(f'Selamat datang, {name}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('index'))
    rooms = Room.query.order_by(Room.name).all()
    return render_template('dashboard.html', rooms=rooms, user=session)

@app.route('/book/<int:room_id>', methods=['GET'])
def book_form(room_id):
    if not is_logged_in():
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('index'))
    room = Room.query.get_or_404(room_id)
    return render_template('booking.html', room=room, user=session)

@app.route('/book_submit', methods=['POST'])
def book_submit():
    if not is_logged_in():
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('index'))

    room_id = int(request.form.get('room_id'))
    reason = request.form.get('reason', '').strip()

    # input tambahan
    booking_date = request.form.get('booking_date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')

    room = Room.query.get_or_404(room_id)

    # konversi ke tipe Python
    date_obj = datetime.strptime(booking_date, "%Y-%m-%d").date()
    start_obj = datetime.strptime(start_time, "%H:%M").time()
    end_obj = datetime.strptime(end_time, "%H:%M").time()

    # validasi waktu
    if start_obj >= end_obj:
        flash('Jam mulai harus lebih kecil dari jam selesai.', 'error')
        return redirect(url_for('book_form', room_id=room_id))

    # cek bentrok jadwal
    conflict = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.booking_date == date_obj,
        Booking.start_time < end_obj,
        Booking.end_time > start_obj
    ).first()

    if conflict:
        flash('Ruangan bentrok dengan jadwal lain.', 'error')
        return redirect(url_for('dashboard'))

    # simpan booking
    booking = Booking(
        name=session['name'],
        nim=session['nim'],
        room_id=room.id,
        reason=reason,
        booking_date=date_obj,
        start_time=start_obj,
        end_time=end_obj,
        timestamp=datetime.now()
    )

    db.session.add(booking)
    db.session.commit()

    flash(f'Booking sukses: {room.name}', 'success')
    return redirect(url_for('dashboard'))

@app.route('/release/<int:room_id>', methods=['POST'])
def release(room_id):
    if not is_logged_in():
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('index'))

    room = Room.query.get_or_404(room_id)
    # hanya boleh release jika dia peminjam yang sama atau admin (sederhana: izinkan jika nim sama)
    if room.is_available:
        flash(f'{room.name} sudah kosong.', 'info')
        return redirect(url_for('dashboard'))

    if room.booked_by_nim != session.get('nim'):
        flash('Hanya peminjam yang melakukan booking yang dapat merilis ruangan ini.', 'error')
        return redirect(url_for('dashboard'))

    # release
    room.is_available = True
    room.booked_by_name = None
    room.booked_by_nim = None
    room.current_booking_id = None
    db.session.commit()
    flash(f'{room.name} berhasil di-release.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/history')
def history():
    if not is_logged_in():
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('index'))
    # menampilkan riwayat booking terbaru dulu (loop later di template)
    bookings = Booking.query.order_by(Booking.timestamp.desc()).all()
    return render_template('history.html', bookings=bookings, user=session)

# Run app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)