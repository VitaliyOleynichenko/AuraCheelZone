# app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.models import Reservation, Table
from app.database import db

def reset_reservations():
    now = datetime.now()
    # Если сейчас 4:00 (можно добавить проверку минут для большей точности)
    if now.hour == 4:
        # Сбросить все бронирования на текущую дату
        reservations = Reservation.query.filter(Reservation.reservation_time.cast(db.Date) == datetime.today().date()).all()
        for r in reservations:
            r.status = False
        # Сбросить статус всех столов
        tables = Table.query.all()
        for table in tables:
            table.status = 'Свободен'
        db.session.commit()
        print("Все бронирования сброшены в 4:00 утра.")

scheduler = BackgroundScheduler()
scheduler.add_job(func=reset_reservations, trigger="interval", hours=1)
scheduler.start()
