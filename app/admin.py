# app/admin.py
from flask_admin.contrib.sqla import ModelView
from app.admin import admin, db
from app.models import Menu, Employee, Customer, Table, Order, OrderItem

class CustomModelView(ModelView):
    page_size = 50
    can_export = True

admin.add_view(CustomModelView(Menu, db.session, name='Меню'))
admin.add_view(CustomModelView(Employee, db.session, name='Сотрудники'))
admin.add_view(CustomModelView(Customer, db.session, name='Клиенты'))
admin.add_view(CustomModelView(Table, db.session, name='Столики'))
admin.add_view(CustomModelView(Order, db.session, name='Заказы'))
admin.add_view(CustomModelView(OrderItem, db.session, name='Позиции заказов'))