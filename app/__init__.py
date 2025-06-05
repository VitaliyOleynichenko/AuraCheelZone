from flask import Flask, session
from flask_admin import Admin
from config import Config
from app.database import db
from app.models import Menu  # Импортируем модель Menu для использования в контекстном процессоре
from app.filters import init_app as init_filters

# Инициализация админ-панели
admin = Admin(name='AuraCheelZone Admin', template_mode='bootstrap3')

def create_app():
    # Создание экземпляра приложения Flask
    app = Flask(__name__)
    # Загрузка конфигурации
    app.config.from_object(Config)
    # Инициализация базы данных
    db.init_app(app)
    # Инициализация админ-панели
    admin.init_app(app)

    # Создание таблиц в базе данных (если они еще не созданы)
    with app.app_context():
        db.create_all()

    # Регистрация маршрутов (роутов)
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    # Регистрация пользовательских фильтров
    init_filters(app)

    from app.models import Menu

    @app.context_processor
    def inject_models():
        return dict(Menu=Menu)

    # Регистрация контекстного процессора для шаблонов
    @app.context_processor
    def utility_processor():
        def sum_cart(cart):
            total = 0
            for item in cart:
                menu_item = Menu.query.get(item['item_id'])
                if menu_item:
                    total += item['quantity'] * menu_item.price
            return total
        return dict(sum_cart=sum_cart)

    return app
import logging
logging.basicConfig(level=logging.DEBUG)

