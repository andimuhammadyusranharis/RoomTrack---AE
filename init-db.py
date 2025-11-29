from app import app, db
from models import Room

with app.app_context():
    db.create_all()
    # cek jika rooms sudah ada, jangan duplikat
    existing = {r.name for r in Room.query.all()}
    rooms_to_create = ['AE101','AE102','AE103','AE104','AE105','AE106','AE107', 'C2-P1', 'Ruangan Rektor']
    for rname in rooms_to_create:
        if rname not in existing:
            r = Room(name=rname)
            db.session.add(r)
    db.session.commit()
    print("Database diinisialisasi dan ruangan ditambahkan, jalankan py app.py.")
