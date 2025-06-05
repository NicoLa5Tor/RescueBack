from flask import request, jsonify
from functools import wraps
from services.empresa_service import EmpresaService
from services.auth_service import AuthService
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

class EmpresaController:
    def __init__(self):
        self.empresa_service = EmpresaService()
    
    @admin_required
    def create_empresa(self):
        """Endpoint para crear una empresa (solo super admin)"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'errors': ['No se enviaron datos']
                }), 400
            
            # Obtener el ID del super admin del token JWT
            super_admin_id = request.current_user['user_id']
            
            result = self.empresa_service.create_empresa(data, super_admin_id)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result.get('message', 'Empresa creada correctamente'),
                    'data': result['data']
                }), 201
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500
    
    def get_empresa(self, empresa_id):
        """Endpoint para obtener una empresa por ID"""
        try:
            result = self.empresa_service.get_empresa_by_id(empresa_id)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'data': result['data']
                }), 200
            else:
                return jsonify(result), 404
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500
    
    def get_all_empresas(self):
        """Endpoint para obtener todas las empresas"""
        try:
            # Verificar si se quieren incluir empresas inactivas (solo super admin)
            include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
            
            if include_inactive:
                # Verificar autenticación de super admin si se solicitan inactivas
                auth_header = request.headers.get('Authorization')
                if auth_header and auth_header.startswith('Bearer '):
                    auth_service = AuthService()
                    token = auth_header[7:]
                    verification = auth_service.verify_token(token)
                    if not (verification['valid'] and verification['tipo'] == 'admin'):
                        include_inactive = False
                else:
                    include_inactive = False
            
            result = self.empresa_service.get_all_empresas(include_inactive)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'data': result['data'],
                    'count': result['count']
                }), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500
    
    @admin_required
    def get_my_empresas(self):
        """Endpoint para obtener empresas creadas por el super admin autenticado"""
        try:
            super_admin_id = request.current_user['user_id']
            result = self.empresa_service.get_empresas_by_creador(super_admin_id)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'data': result['data'],
                    'count': result['count']
                }), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500
    
    @admin_required
    def update_empresa(self, empresa_id):
        """Endpoint para actualizar una empresa (solo el creador)"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'errors': ['No se enviaron datos']
                }), 400
            
            super_admin_id = request.current_user['user_id']
            result = self.empresa_service.update_empresa(empresa_id, data, super_admin_id)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result.get('message', 'Empresa actualizada correctamente'),
                    'data': result['data']
                }), 200
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500
    
    @admin_required
    def delete_empresa(self, empresa_id):
        """Endpoint para eliminar una empresa (solo el creador)"""
        try:
            super_admin_id = request.current_user['user_id']
            result = self.empresa_service.delete_empresa(empresa_id, super_admin_id)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result['message']
                }), 200
            else:
                return jsonify(result), 404
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500
    
    def search_empresas_by_ubicacion(self):
        """Endpoint para buscar empresas por ubicación"""
        try:
            ubicacion = request.args.get('ubicacion')
            
            if not ubicacion:
                return jsonify({
                    'success': False,
                    'errors': ['El parámetro ubicacion es obligatorio']
                }), 400
            
            result = self.empresa_service.search_empresas_by_ubicacion(ubicacion)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'data': result['data'],
                    'count': result['count']
                }), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500
    
    @admin_required
    def get_empresa_stats(self):
        """Endpoint para obtener estadísticas de empresas (solo super admin)"""
        try:
            result = self.empresa_service.get_empresa_stats()
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'data': result['data']
                }), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500