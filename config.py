import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv('MONGO_URI')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'rescue')
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    PORT = int(os.getenv('PORT', 5000))
    
    # Validar variables de entorno críticas
    @classmethod
    def validate_config(cls):
        required_vars = ['MONGO_URI', 'SECRET_KEY', 'JWT_SECRET_KEY']
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var, None):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Variables de entorno faltantes: {', '.join(missing_vars)}. Verifica tu archivo .env")
    
    # Configuración de cookies JWT
    JWT_TOKEN_LOCATION = ['cookies', 'headers']  # Permitir tanto cookies como headers
    JWT_COOKIE_SECURE = False  # False en desarrollo local (HTTP)
    JWT_COOKIE_HTTPONLY = True  # HttpOnly para seguridad
    JWT_COOKIE_SAMESITE = 'None'  # None para desarrollo local cross-origin
    JWT_COOKIE_CSRF_PROTECT = False  # Desactivamos CSRF protection por simplicidad
    JWT_ACCESS_COOKIE_NAME = 'auth_token'  # Nombre de la cookie
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 horas
