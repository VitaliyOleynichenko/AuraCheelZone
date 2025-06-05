import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.models import Menu, Employee, Table, Order, OrderItem, Reservation
from app.database import db
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    logger.debug("Рендер главной страницы")
    return render_template('index.html')

@bp.route('/menu')
def menu():
    logger.debug("Получаем список блюд для меню")
    menu_items = Menu.query.all()
    logger.debug("Найдено блюд: %s", len(menu_items))
    # Группировка блюд по категории; если категория не задана, используем "Без категории"
    categories_dict = {}
    for dish in menu_items:
        cat = dish.category if dish.category else "Без категории"
        if cat not in categories_dict:
            categories_dict[cat] = []
        categories_dict[cat].append(dish)
    categories = [{'name': cat, 'dishes': dishes} for cat, dishes in categories_dict.items()]
    logger.debug("Сформировано %s категорий", len(categories))
    return render_template('menu.html', categories=categories)

@bp.route('/about')
def about():
    logger.debug("Рендер страницы 'О нас'")
    return render_template('about.html')

@bp.route('/booking')
def booking():
    logger.debug("Получаем список столиков для бронирования")
    tables = Table.query.all()
    logger.debug("Найдено столиков: %s", len(tables))
    return render_template('booking.html', tables=tables)

@bp.route('/cart')
def cart():
    cart = session.get('cart', [])
    logger.debug("Отображение корзины. Содержимое session['cart']: %s", cart)
    return render_template('cart.html')

@bp.route('/promotions')
def promotions():
    logger.debug("Рендер страницы акций")
    return render_template('promotions.html')

@bp.route('/api/tables')
def get_tables():
    logger.debug("API: Получение списка столиков")
    tables = Table.query.all()
    table_list = []
    for table in tables:
        table_data = {
            'table_id': table.table_id,
            'number': table.number,
            'status': table.status  # Ожидается: "Свободен" или "Занят"
        }
        table_list.append(table_data)
    logger.debug("Отправляем %s столиков", len(table_list))
    return jsonify(table_list)

@bp.route('/api/reserve-table/', methods=['POST'])
def reserve_table():
    try:
        data = request.get_json()
        logger.debug("Получены данные бронирования: %s", data)
        table_number = int(data.get('table_number'))
        customer_name = data.get('customer_name')
        customer_phone = data.get('customer_phone')

        # Находим стол по его номеру
        table = Table.query.filter_by(number=table_number).first()
        if not table:
            logger.error("Стол с номером %s не найден", table_number)
            return jsonify({'success': False, 'message': 'Стол не найден'}), 404

        if table.status == 'Занят':
            logger.debug("Стол с номером %s уже забронирован", table_number)
            return jsonify({'success': False, 'message': 'Стол уже забронирован'}), 400

        # Создаем бронирование на сегодняшний день
        reservation = Reservation(
            table_id=table.table_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            reservation_time=datetime.today(),
            status=True
        )
        db.session.add(reservation)
        table.status = 'Занят'
        db.session.commit()
        logger.debug("Бронирование создано для стола с номером %s", table_number)
        return jsonify({'success': True, 'message': 'Стол забронирован!', 'table_number': table_number})
    except Exception as e:
        db.session.rollback()
        logger.error("Ошибка бронирования: %s", e, exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/menu')
def get_menu():
    logger.debug("API: Получение меню")
    menu_items = Menu.query.all()
    menu_list = []
    for item in menu_items:
        menu_data = {
            'id': item.item_id,
            'name': item.name,
            'description': item.description,
            'price': float(item.price),
            'image_url': item.image_url,
            'category': item.category
        }
        menu_list.append(menu_data)
    logger.debug("Отправляем меню с %s позиций", len(menu_list))
    return jsonify(menu_list)

@bp.route('/api/add_to_cart', methods=['POST'])
def add_to_cart():
    logger.debug("API: Добавление блюда в корзину (START)")
    data = request.get_json()
    logger.debug("API: Получены данные JSON: %s", data)
    try:
        item_id = int(data.get('item_id'))
        quantity = int(data.get('quantity'))
    except Exception as e:
        logger.error("API: Ошибка при разборе данных для add_to_cart: %s", e, exc_info=True)
        return jsonify({'success': False, 'message': 'Неверные данные'}), 400

    menu_item = Menu.query.get(item_id)
    if not menu_item:
        logger.error("API: Блюдо с id %s не найдено", item_id)
        return jsonify({'success': False, 'message': 'Блюдо не найдено'}), 404

    cart = session.get('cart', [])
    logger.debug("API: Текущая корзина перед обновлением: %s", cart)
    existing_item = next((item for item in cart if item['item_id'] == item_id), None)
    if existing_item:
        existing_item['quantity'] += quantity
        logger.debug("API: Увеличено количество для блюда id %s до %s", item_id, existing_item['quantity'])
    else:
        cart.append({'item_id': item_id, 'quantity': quantity})
        logger.debug("API: Добавлено новое блюдо в корзину: id %s, quantity %s", item_id, quantity)
    session['cart'] = cart
    logger.debug("API: Обновлённая корзина: %s", cart)
    logger.debug("API: Добавление блюда в корзину (END)")
    return jsonify({'success': True, 'message': 'Блюдо добавлено в корзину'})

@bp.route('/api/sync_cart', methods=['POST'])
def sync_cart():
    data = request.get_json()
    logger.debug("API: Синхронизация корзины. Полученные данные: %s", data)
    cart = data.get('cart', [])
    session['cart'] = cart
    logger.debug("API: Синхронизированная корзина в сессии: %s", cart)
    return jsonify({'success': True, 'message': 'Корзина синхронизирована'})

@bp.route('/api/debug_cart', methods=['GET'])
def debug_cart():
    current_cart = session.get('cart', [])
    logger.debug("DEBUG: Текущее содержимое session['cart']: %s", current_cart)
    return jsonify(current_cart)

@bp.route('/place_order', methods=['POST'])
def place_order():
    logger.debug("Обработка оформления заказа")
    try:
        if request.is_json:
            data = request.get_json()
            cart = data.get('cart', [])
            phone = data.get('phone')
            delivery = data.get('delivery')
            address = data.get('address', '')
        else:
            cart = session.get('cart', [])
            phone = request.form.get('phone')
            delivery = request.form.get('delivery_option') == 'delivery'
            address = request.form.get('address', '')
        logger.debug("place_order: Корзина для заказа: %s", cart)
        total_amount = 0
        for item in cart:
            menu_item = Menu.query.get(item['item_id'])
            if not menu_item:
                logger.warning("place_order: Блюдо с id %s не найдено при расчёте суммы", item['item_id'])
                continue
            total_amount += menu_item.price * item['quantity']
        logger.debug("place_order: Итоговая сумма заказа: %s", total_amount)
        new_order = Order(
            phone=phone,
            delivery=delivery,
            address=address if delivery else None,
            table_id=None,
            total_amount=total_amount
        )
        db.session.add(new_order)
        db.session.flush()
        for item in cart:
            menu_item = Menu.query.get(item['item_id'])
            if not menu_item:
                logger.warning("place_order: Блюдо с id %s не найдено при добавлении в заказ", item['item_id'])
                continue
            order_item = OrderItem(
                order_id=new_order.order_id,
                item_id=item['item_id'],
                quantity=item['quantity'],
                subtotal=menu_item.price * item['quantity']
            )
            db.session.add(order_item)
            logger.debug("place_order: Добавлена позиция в заказ: блюдо id %s, quantity %s", item['item_id'], item['quantity'])
        db.session.commit()
        session['cart'] = []
        logger.debug("place_order: Заказ оформлен успешно и корзина очищена")
        return jsonify({
            'success': True,
            'message': 'Заказ оформлен!',
            'order_id': new_order.order_id,
            'delivery': new_order.delivery,
            'address': new_order.address,
            'total_amount': float(new_order.total_amount)
        })
    except Exception as e:
        db.session.rollback()
        logger.error("place_order: Ошибка оформления заказа: %s", e, exc_info=True)
        if request.is_json:
            return jsonify({'success': False, 'message': str(e)}), 500
        else:
            flash(f'Ошибка оформления заказа: {e}')
            return redirect(url_for('routes.cart'))
