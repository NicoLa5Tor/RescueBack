from flask import request, jsonify, g
from functools import wraps
from services.empresa_service import EmpresaService

def require_super_admin(f):
    """Decorador para verificar que el usuario sea super admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Aquí deberías implementar tu lógica de autenticación
        # Por ahora, asumimos que el super_admin_id viene en los headers
        super_admin_id = request.headers.get('X-Super-Admin-ID')
        
        if not super_admin_id:
            return jsonify({
                'success': False,
                'errors': ['Se requiere autenticación de super admin']
            }), 401
        
        # Guardar el ID del super admin en el contexto de la request
        g.super_admin_id = super_admin_id
        return f(*args, **kwargs)
    
    return decorated_function

class EmpresaController:
    def __init__(self):
        self.empresa_service = EmpresaService()
    
    @require_super_admin
    def create_empresa(self):
        """Endpoint para crear una empresa (solo super admin)"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'errors': ['No se enviaron datos']
                }), 400
            
            # Obtener el ID del super admin del contexto
            super_admin_id = g.super_admin_id
            
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
                super_admin_id = request.headers.get('X-Super-Admin-ID')
                if not super_admin_id:
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
    
    @require_super_admin
    def get_my_empresas(self):
        """Endpoint para obtener empresas creadas por el super admin autenticado"""
        try:
            super_admin_id = g.super_admin_id
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
    
    @require_super_admin
    def update_empresa(self, empresa_id):
        """Endpoint para actualizar una empresa (solo el creador)"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'errors': ['No se enviaron datos']
                }), 400
            
            super_admin_id = g.super_admin_id
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
    
    @require_super_admin
    def delete_empresa(self, empresa_id):
        """Endpoint para eliminar una empresa (solo el creador)"""
        try:
            super_admin_id = g.super_admin_id
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
    
    @require_super_admin
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