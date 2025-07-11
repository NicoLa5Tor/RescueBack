import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'rescue')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    
    # Configuración de cookies JWT
    JWT_TOKEN_LOCATION = ['cookies', 'headers']  # Permitir tanto cookies como headers
    JWT_COOKIE_SECURE = False  # False en desarrollo local (HTTP)
    JWT_COOKIE_HTTPONLY = True  # HttpOnly para seguridad
    JWT_COOKIE_SAMESITE = 'None'  # None para desarrollo local cross-origin
    JWT_COOKIE_CSRF_PROTECT = False  # Desactivamos CSRF protection por simplicidad
    JWT_ACCESS_COOKIE_NAME = 'auth_token'  # Nombre de la cookie
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 horas
