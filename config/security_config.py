import os

class SecurityConfig:
    # Detectar si estamos en desarrollo o producción
    IS_DEVELOPMENT = os.environ.get('FLASK_ENV') == 'development'
    
    # Configuración de cookies
    COOKIE_SECURE = not IS_DEVELOPMENT  # False en desarrollo, True en producción
    COOKIE_SAMESITE = 'Lax' if IS_DEVELOPMENT else 'Strict'
    
    # Configuración de JWT
    JWT_IN_COOKIE = True  # Usar cookies para JWT
    JWT_MINIMAL_PAYLOAD = not IS_DEVELOPMENT  # JWT mínimo en producción
    
    # Headers de seguridad adicionales para producción
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    @classmethod
    def get_cookie_config(cls):
        """Retorna configuración de cookies según el entorno"""
        return {
            'httponly': True,
            'secure': cls.COOKIE_SECURE,
            'samesite': cls.COOKIE_SAMESITE,
            'domain': None,
            'path': '/'
        }
