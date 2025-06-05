from app.database import db
from datetime import datetime

class Menu(db.Model):
    __tablename__ = 'menu'
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(255))  # Поле для хранения имени файла изображения
    category = db.Column(db.String(255), nullable=True)  # Новое поле для категории

class Employee(db.Model):
    __tablename__ = 'employees'
    employee_id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(255))
    name = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(255))

class Table(db.Model):
    __tablename__ = 'tables'
    table_id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    status = db.Column(db.String(50), default='Свободен')  # "Свободен" или "Занят"

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False)
    delivery = db.Column(db.Boolean, default=False)  # True – доставка, False – самовывоз/за столик
    address = db.Column(db.String(255))  # Заполняется, если доставка = True
    table_id = db.Column(db.Integer, db.ForeignKey('tables.table_id'), nullable=True)
    order_date = db.Column(db.DateTime, server_default=db.func.now())
    total_amount = db.Column(db.Numeric(10, 2))
    table = db.relationship('Table', backref='orders')
    items = db.relationship('OrderItem', backref='order')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'))
    item_id = db.Column(db.Integer, db.ForeignKey('menu.item_id'))
    quantity = db.Column(db.Integer, default=1)
    subtotal = db.Column(db.Numeric(10, 2))
    menu_item = db.relationship('Menu', backref='order_items')

# Новая модель для бронирования столов
class Reservation(db.Model):
    __tablename__ = 'reservations'
    reservation_id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.table_id'), nullable=False)
    customer_name = db.Column(db.String(255), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    reservation_time = db.Column(db.DateTime, default=datetime.today)  # Всегда на текущую дату
    status = db.Column(db.Boolean, default=True)  # True – забронирован, False – свободен

    table = db.relationship('Table', backref='reservations')
