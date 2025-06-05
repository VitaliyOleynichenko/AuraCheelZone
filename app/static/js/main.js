document.addEventListener('DOMContentLoaded', function() {
  console.log("main.js loaded and DOMContentLoaded fired");

  /* ===== ФУНКЦИИ ДЛЯ РАБОТЫ С КОРЗИНОЙ ===== */
  const renderCart = async () => {
    const cartListEl = document.getElementById('cart-list');
    const cartTotalEl = document.getElementById('cart-total');
    if (!cartListEl) {
      console.warn("renderCart: Элемент #cart-list не найден на странице");
      return;
    }
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');
    try {
      const response = await fetch('/api/menu');
      let menu = await response.json();
      cartListEl.innerHTML = '';
      let total = 0;
      if (cart.length === 0) {
        cartListEl.innerHTML = '<p>Ваша корзина пуста.</p>';
        if (cartTotalEl) cartTotalEl.textContent = '';
        return;
      }
      const ul = document.createElement('ul');
      cart.forEach(item => {
        const menuItem = menu.find(m => String(m.id) === String(item.item_id));
        if (!menuItem) return;
        const li = document.createElement('li');
        li.innerHTML = `
          <strong>${menuItem.name}</strong>
          <span class="price">${menuItem.price} ₽</span>
          <input type="number" class="quantity-input" data-id="${item.item_id}" value="${item.quantity}" min="1">
          <button type="button" class="remove-item" data-id="${item.item_id}">Удалить</button>
        `;
        ul.appendChild(li);
        total += menuItem.price * item.quantity;
      });
      cartListEl.appendChild(ul);
      if (cartTotalEl) {
        cartTotalEl.textContent = `Итоговая сумма: ${total.toFixed(2)} ₽`;
      }
    } catch (error) {
      console.error("renderCart: Ошибка получения меню:", error);
    }
  };

  function showToast(message) {
    const toast = document.createElement("div");
    toast.className = "toast-notification";
    toast.innerText = message;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.classList.add("fade-out");
      setTimeout(() => {
        toast.remove();
      }, 500);
    }, 3000);
  }

  /* ===== ФУНКЦИИ ДЛЯ ОФОРМЛЕНИЯ ЗАКАЗА ===== */
  const initPlaceOrder = () => {
    const orderForm = document.getElementById('order-form');
    if (!orderForm) return;
    orderForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      let cart = JSON.parse(localStorage.getItem('cart') || '[]');
      if (cart.length === 0) {
        showToast('Ваша корзина пуста.');
        return;
      }
      const phoneEl = document.getElementById('phone');
      const deliveryCheckbox = document.getElementById('delivery-checkbox');
      const addressEl = document.getElementById('address');
      const phone = phoneEl ? phoneEl.value.trim() : '';
      const isDelivery = deliveryCheckbox ? deliveryCheckbox.checked : false;
      const address = addressEl ? addressEl.value.trim() : '';
      if (!phone) {
        showToast('Введите номер телефона.');
        return;
      }
      if (isDelivery && !address) {
        showToast('Введите адрес доставки.');
        return;
      }
      try {
        const response = await fetch('/place_order', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            cart: cart,
            phone: phone,
            delivery: isDelivery,
            address: isDelivery ? address : ''
          })
        });
        const result = await response.json();
        if (result.success) {
          localStorage.removeItem('cart');
          showOrderSuccessModal(result);
        } else {
          showToast('Ошибка: ' + result.message);
        }
      } catch (error) {
        console.error("initPlaceOrder: Ошибка оформления заказа:", error);
        showToast("Произошла ошибка при оформлении заказа.");
      }
    });
  };

  if (document.getElementById('order-form')) {
    initPlaceOrder();
  }
  if (document.getElementById('cart-list')) {
    renderCart();
  }
  console.debug("main.js: Инициализация завершена. Текущая корзина:", localStorage.getItem('cart'));

  /* ===== ОБРАБОТКА СОБЫТИЙ ДЛЯ КОРЗИНЫ ===== */
  // Делегирование событий для добавления в корзину, удаления и изменения количества
  document.body.addEventListener('click', function(e) {
    // Добавление в корзину
    if (e.target && e.target.classList.contains('add-to-cart')) {
      const button = e.target;
      const itemId = button.getAttribute('data-id');
      const quantityControl = button.closest('.quantity-control');
      const quantityInput = quantityControl ? quantityControl.querySelector('.quantity-input') : null;
      const quantity = quantityInput ? parseInt(quantityInput.value, 10) : 1;
      if (!itemId || quantity <= 0) return;
      let cart = JSON.parse(localStorage.getItem('cart') || '[]');
      let existingItem = cart.find(item => String(item.item_id) === String(itemId));
      if (existingItem) {
        existingItem.quantity += quantity;
      } else {
        cart.push({ item_id: itemId, quantity: quantity });
      }
      localStorage.setItem('cart', JSON.stringify(cart));
      showToast("Товар добавлен в корзину!");
      console.debug("Добавлен в корзину:", cart);
      if (document.getElementById('cart-list')) renderCart();
    }
    // Удаление из корзины
    if (e.target && e.target.classList.contains('remove-item')) {
      const itemId = e.target.getAttribute('data-id');
      let cart = JSON.parse(localStorage.getItem('cart') || '[]');
      cart = cart.filter(item => String(item.item_id) !== String(itemId));
      localStorage.setItem('cart', JSON.stringify(cart));
      showToast("Товар удалён из корзины!");
      if (document.getElementById('cart-list')) renderCart();
    }
  });

  document.body.addEventListener('change', function(e) {
    if (e.target && e.target.classList.contains('quantity-input')) {
      const itemId = e.target.getAttribute('data-id');
      const newQuantity = parseInt(e.target.value, 10);
      let cart = JSON.parse(localStorage.getItem('cart') || '[]');
      let item = cart.find(i => String(i.item_id) === String(itemId));
      if (item) {
        item.quantity = newQuantity;
        localStorage.setItem('cart', JSON.stringify(cart));
        if (document.getElementById('cart-list')) renderCart();
      }
    }
  });

  /* ===== ФУНКЦИИ ДЛЯ БРОНИРОВАНИЯ СТОЛОВ ===== */
  const bookingModal = document.getElementById('customBookingModal');
  const bookingForm = document.getElementById('bookingForm');
  const selectedTableInput = document.getElementById('selectedTableNumber');
  const availableTables = document.querySelectorAll('.restaurant-map .table.available');

  availableTables.forEach(function(table) {
    table.addEventListener('click', function() {
      const tableNumber = this.getAttribute('data-table-number');
      if (tableNumber) {
        selectedTableInput.value = tableNumber;
        availableTables.forEach(t => t.style.border = '');
        this.style.border = '2px solid var(--accent-orange)';
        // Показываем кастомное модальное окно
        bookingModal.classList.add('active');
      }
    });
  });

  // Обработчик закрытия модального окна
  const modalClose = document.getElementById('modalClose');
  if (modalClose) {
    modalClose.addEventListener('click', function() {
      bookingModal.classList.remove('active');
    });
  }

  // Обработка отправки формы бронирования
  if (bookingForm) {
    bookingForm.addEventListener('submit', function(event) {
      event.preventDefault();
      const tableNumber = selectedTableInput.value;
      const customerName = document.getElementById('customerName').value.trim();
      const customerPhone = document.getElementById('customerPhone').value.trim();
      if (!tableNumber) {
        alert("Пожалуйста, выберите свободный стол.");
        return;
      }
      const payload = {
        table_number: tableNumber,
        customer_name: customerName,
        customer_phone: customerPhone
      };
      fetch('/api/reserve-table/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })
      .then(response => {
        if (!response.ok) {
          throw new Error("Ошибка сети: " + response.status);
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          showBookingSuccessModal(tableNumber);
          bookingModal.classList.remove('active');
          const tableDiv = document.getElementById('table-' + tableNumber);
          if (tableDiv) {
            tableDiv.classList.remove('available');
            tableDiv.classList.add('booked');
            tableDiv.innerHTML = `${tableNumber}<br>Занят`;
            tableDiv.style.border = '';
            tableDiv.onclick = null;
          }
        } else {
          alert('Ошибка бронирования: ' + data.message);
        }
      })
      .catch(error => {
        console.error('Ошибка при бронировании стола:', error);
        alert('Произошла ошибка при бронировании стола.');
      });
    });
  }

  // Функция для показа модального окна с успешным бронированием (исчезает через 3 секунды)
  function showBookingSuccessModal(tableNumber) {
    const successModal = document.createElement("div");
    successModal.classList.add("booking-success-modal");
    successModal.innerHTML = `
      <div class="modal-content">
        <h2>Столик №${tableNumber} успешно забронирован!</h2>
      </div>
    `;
    document.body.appendChild(successModal);
    setTimeout(() => {
      successModal.classList.add("fade-out");
      setTimeout(() => {
        successModal.remove();
      }, 500);
    }, 3000);
  }

  /* ===== ФУНКЦИИ ДЛЯ ОФОРМЛЕНИЯ ЗАКАЗА (ТО, ЧТО УЖЕ РАБОТАЕТ) ===== */
  // Здесь можно оставить существующий код для работы с корзиной
});

function showOrderSuccessModal(orderData) {
  const modal = document.createElement("div");
  modal.classList.add("order-success-modal");
  modal.innerHTML = `
    <div class="modal-content">
      <h2>Заказ успешно принят!</h2>
      <p>Номер заказа: <strong>${orderData.order_id}</strong></p>
      <p>Способ получения: <strong>${orderData.delivery ? 'Доставка' : 'Самовывоз'}</strong></p>
      ${orderData.delivery ? `<p>Адрес доставки: <strong>${orderData.address}</strong></p>` : ""}
      <p>Сумма заказа: <strong>${orderData.total_amount.toFixed(2)} ₽</strong></p>
      <button class="modal-close-btn">Закрыть</button>
    </div>
  `;
  document.body.appendChild(modal);
  modal.querySelector(".modal-close-btn").addEventListener("click", function() {
    modal.remove();
    window.location.href = "/";
  });
}
