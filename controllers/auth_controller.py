from flask import request, jsonify
from functools import wraps
from services.auth_service import AuthService

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()
    
    def login(self):
        """
        Endpoint: POST /auth/login
        Autentica usuarios (administradores o empresas) y retorna JWT
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'access': False,
                    'message': 'No se enviaron datos',
                    'errors': ['Se requieren credenciales']
                }), 400
            
            email_or_usuario = data.get('email') or data.get('usuario')
            password = data.get('password')
            
            if not email_or_usuario or not password:
                return jsonify({
                    'success': False,
                    'access': False,
                    'message': 'Credenciales incompletas',
                    'errors': ['Se requieren email/usuario y contraseña']
                }), 400
            
            # Intentar autenticar
            result = self.auth_service.login(email_or_usuario, password)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'access': True,
                    'message': result['message'],
                    'token': result['token'],
                    'user': result['user']
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'access': False,
                    'message': result.get('message', 'Error de autenticación'),
                    'errors': result.get('errors', ['Credenciales inválidas'])
                }), 401
                
        except Exception as e:
            return jsonify({
                'success': False,
                'access': False,
                'message': 'Error interno del servidor',
                'errors': [str(e)]
            }), 500
    
    def verify_token(self):
        """
        Endpoint: POST /auth/verify
        Verifica si un token JWT es válido
        """
        try:
            print("entra")
            data = request.get_json()
            print("verifica")
            token = data.get('token') if data else None
            
            if not token:
                # Intentar obtener token del header Authorization
                auth_header = request.headers.get('Authorization')
                if auth_header and auth_header.startswith('Bearer '):
                    token = auth_header[7:]  # Remover "Bearer "
            
            if not token:
                return jsonify({
                    'valid': False,
                    'message': 'Token no proporcionado'
                }), 400
            
            verification = self.auth_service.verify_token(token)
            
            if verification['valid']:
                return jsonify({
                    'valid': True,
                    'user_id': verification['user_id'],
                    'rol': verification['rol'],
                    'tipo': verification['tipo'],
                    'permisos': verification['permisos']
                }), 200
            else:
                return jsonify({
                    'valid': False,
                    'message': verification.get('error', 'Token inválido')
                }), 401
                
        except Exception as e:
            return jsonify({
                'valid': False,
                'message': 'Error verificando token',
                'error': str(e)
            }), 500
    
    def refresh_token(self):
        """
        Endpoint: POST /auth/refresh
        Renueva un token JWT válido
        """
        try:
            data = request.get_json()
            token = data.get('token') if data else None
            
            if not token:
                auth_header = request.headers.get('Authorization')
                if auth_header and auth_header.startswith('Bearer '):
                    token = auth_header[7:]
            
            if not token:
                return jsonify({
                    'success': False,
                    'message': 'Token no proporcionado'
                }), 400
            
            result = self.auth_service.refresh_token(token)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'token': result['token'],
                    'message': result['message']
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': result['message'],
                    'errors': result.get('errors', [])
                }), 401
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Error renovando token',
                'errors': [str(e)]
            }), 500

# ========== DECORADORES PARA PROTEGER ENDPOINTS ==========

def token_required(f):
    """Decorador que requiere un token JWT válido"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Obtener token del header Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token de acceso requerido',
                'errors': ['Se requiere autenticación']
            }), 401
        
        # Verificar token
        auth_service = AuthService()
        verification = auth_service.verify_token(token)
        
        if not verification['valid']:
            return jsonify({
                'success': False,
                'message': 'Token inválido',
                'errors': [verification.get('error', 'Token inválido')]
            }), 401
        
        # Agregar información del usuario al contexto
        request.current_user = verification['payload']
        request.user_permissions = verification['permisos']
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """Decorador que requiere permisos de administrador"""
    @wraps(f)
    @token_required
    def decorated_function(*args, **kwargs):
        if request.current_user['tipo'] != 'admin':
            return jsonify({
                'success': False,
                'message': 'Se requieren permisos de administrador',
                'errors': ['Acceso denegado']
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def empresa_required(f):
    """Decorador que requiere ser una empresa autenticada"""
    @wraps(f)
    @token_required
    def decorated_function(*args, **kwargs):
        if request.current_user['tipo'] != 'empresa':
            return jsonify({
                'success': False,
                'message': 'Se requiere ser una empresa autenticada',
                'errors': ['Acceso denegado']
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def permission_required(permission):
    """Decorador que requiere un permiso específico"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated_function(*args, **kwargs):
            auth_service = AuthService()
            if not auth_service.check_permission(request.current_user, permission):
                return jsonify({
                    'success': False,
                    'message': f'Se requiere el permiso: {permission}',
                    'errors': ['Permisos insuficientes']
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator