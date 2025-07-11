from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from middleware.security_middleware import SecurityMiddleware

security_middleware = SecurityMiddleware()

def secure_route(f):
    """
    Decorador que combina jwt_required con validación de seguridad avanzada
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        # Validar seguridad del token
        security_check = security_middleware.validate_request_security()
        if security_check:
            return security_check
        
        # Si pasa todas las validaciones, ejecutar la función
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """
    Decorador que requiere rol de administrador con validación de seguridad
    """
    @wraps(f)
    @secure_route
    def decorated_function(*args, **kwargs):
        from services.user_service import UserService
        user_service = UserService()
        
        user_id = get_jwt_identity()
        user_data = user_service.get_user_by_id(user_id)
        
        if not user_data or user_data.get('role') not in ['admin', 'super_admin']:
            return jsonify({'error': 'Acceso denegado - se requiere rol de administrador'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def super_admin_required(f):
    """
    Decorador que requiere rol de super administrador con validación de seguridad
    """
    @wraps(f)
    @secure_route
    def decorated_function(*args, **kwargs):
        from services.user_service import UserService
        user_service = UserService()
        
        user_id = get_jwt_identity()
        user_data = user_service.get_user_by_id(user_id)
        
        if not user_data or user_data.get('role') != 'super_admin':
            return jsonify({'error': 'Acceso denegado - se requiere rol de super administrador'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
