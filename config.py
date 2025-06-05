import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'ваш_секретный_ключ_для_разработки')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/auracheelzone')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # Настройки для сессии
    SESSION_COOKIE_SECURE = False  # Для разработки можно False, для продакшна True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'