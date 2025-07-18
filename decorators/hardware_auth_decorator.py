from functools import wraps
from flask import jsonify, request
from services.hardware_auth_service import HardwareAuthService


def require_hardware_token(f):
    """
    Decorador que requiere un token válido de autenticación de hardware.
    Solo permite el acceso a endpoints si el token es de hardware válido.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Obtener token de la cabecera Authorization o cookies
            token = None
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
            elif 'token' in request.cookies:
                token = request.cookies.get('token')
            
            if not token:
                return jsonify({
                    'success': False,
                    'error': 'Token de autenticación requerido',
                    'message': 'Se requiere token de hardware válido para acceder a este endpoint'
                }), 401
            
            # Verificar el token usando el servicio de autenticación de hardware
            hardware_auth_service = HardwareAuthService()
            verification_result = hardware_auth_service.verify_token(token)
            
            if not verification_result['success']:
                return jsonify({
                    'success': False,
                    'error': 'Token de hardware inválido',
                    'message': verification_result.get('message', 'Token de hardware no válido')
                }), 401
            
            # Token válido - continuar con la función original
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': f'Error verificando token de hardware: {str(e)}'
            }), 500
    
    return decorated_function
