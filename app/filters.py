# app/filters.py
from app.models import Menu

def sum_cart(cart):
    total = 0
    # Можно оптимизировать, если собрать все id и выполнить один запрос,
    # но для простоты здесь по одному
    for item in cart:
        menu_item = Menu.query.get(item['item_id'])
        if menu_item:
            total += item['quantity'] * menu_item.price
    return total

def init_app(app):
    app.jinja_env.filters['sum_cart'] = sum_cart
