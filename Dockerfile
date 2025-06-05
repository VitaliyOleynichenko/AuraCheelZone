# Используем официальный образ Python
FROM python:3.10-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Указываем порт, который будет слушать Gunicorn
EXPOSE 8000

# Запускаем Gunicorn как WSGI-сервер
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:create_app()"]