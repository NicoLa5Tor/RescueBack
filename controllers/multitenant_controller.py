from flask import request, jsonify
from services.usuario_service import UsuarioService
from controllers.auth_controller import token_required

class MultiTenantController:
    def __init__(self):
        self.usuario_service = UsuarioService()
    
    @token_required
    def create_usuario_for_empresa(self, empresa_id):
        """
        Endpoint: POST /empresas/<empresa_id>/usuarios
        Crea un usuario para una empresa específica
        """
        try:
            # Verificar que sea una empresa o admin
            current_user = request.current_user
            
            # Si es una empresa, solo puede crear usuarios para sí misma
            if current_user['tipo'] == 'empresa':
                if current_user['empresa_id'] != empresa_id:
                    return jsonify({
                        'success': False,
                        'errors': ['No puedes crear usuarios para otra empresa']
                    }), 403
            # Si es admin, puede crear para cualquier empresa
            elif current_user['tipo'] != 'admin':
                return jsonify({
                    'success': False,
                    'errors': ['Se requieren permisos de empresa o administrador']
                }), 403
            
            # Obtener datos del request
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'errors': ['No se enviaron datos']
                }), 400
            
            # Llamar al servicio para crear el usuario
            result = self.usuario_service.create_usuario_for_empresa(empresa_id, data)
            
            # Retornar respuesta según el resultado
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result.get('message', 'Usuario creado correctamente'),
                    'data': result['data']
                }), result['status_code']
            else:
                return jsonify({
                    'success': False,
                    'errors': result['errors']
                }), result['status_code']
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500
    
    @token_required
    def get_usuarios_by_empresa(self, empresa_id):
        """
        Endpoint: GET /empresas/<empresa_id>/usuarios
        Obtiene todos los usuarios de una empresa
        """
        try:
            # Verificar permisos
            current_user = request.current_user
            
            if current_user['tipo'] == 'empresa':
                if current_user['empresa_id'] != empresa_id:
                    return jsonify({
                        'success': False,
                        'errors': ['No puedes ver usuarios de otra empresa']
                    }), 403
            elif current_user['tipo'] != 'admin':
                return jsonify({
                    'success': False,
                    'errors': ['Se requieren permisos de empresa o administrador']
                }), 403
            
            result = self.usuario_service.get_usuarios_by_empresa(empresa_id)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'data': result['data'],
                    'count': result['count'],
                    'empresa': result['empresa']
                }), result['status_code']
            else:
                return jsonify({
                    'success': False,
                    'errors': result['errors']
                }), result['status_code']
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500
    
    @token_required
    def get_usuario_by_empresa(self, empresa_id, usuario_id):
        """
        Endpoint: GET /empresas/<empresa_id>/usuarios/<usuario_id>
        Obtiene un usuario específico de una empresa
        """
        try:
            # Verificar permisos
            current_user = request.current_user
            
            if current_user['tipo'] == 'empresa':
                if current_user['empresa_id'] != empresa_id:
                    return jsonify({
                        'success': False,
                        'errors': ['No puedes ver usuarios de otra empresa']
                    }), 403
            elif current_user['tipo'] != 'admin':
                return jsonify({
                    'success': False,
                    'errors': ['Se requieren permisos de empresa o administrador']
                }), 403
            
            result = self.usuario_service.get_usuario_by_id_and_empresa(usuario_id, empresa_id)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'data': result['data']
                }), result['status_code']
            else:
                return jsonify({
                    'success': False,
                    'errors': result['errors']
                }), result['status_code']
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500
    
    @token_required
    def update_usuario_by_empresa(self, empresa_id, usuario_id):
        """
        Endpoint: PUT /empresas/<empresa_id>/usuarios/<usuario_id>
        Actualiza un usuario específico de una empresa
        """
        try:
            # Verificar permisos
            current_user = request.current_user
            
            if current_user['tipo'] == 'empresa':
                if current_user['empresa_id'] != empresa_id:
                    return jsonify({
                        'success': False,
                        'errors': ['No puedes modificar usuarios de otra empresa']
                    }), 403
            elif current_user['tipo'] != 'admin':
                return jsonify({
                    'success': False,
                    'errors': ['Se requieren permisos de empresa o administrador']
                }), 403
            
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'errors': ['No se enviaron datos']
                }), 400
            
            result = self.usuario_service.update_usuario_for_empresa(usuario_id, empresa_id, data)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result.get('message', 'Usuario actualizado correctamente'),
                    'data': result['data']
                }), result['status_code']
            else:
                return jsonify({
                    'success': False,
                    'errors': result['errors']
                }), result['status_code']
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500
    
    @token_required
    def delete_usuario_by_empresa(self, empresa_id, usuario_id):
        """
        Endpoint: DELETE /empresas/<empresa_id>/usuarios/<usuario_id>
        Elimina un usuario específico de una empresa
        """
        try:
            # Verificar permisos
            current_user = request.current_user
            
            if current_user['tipo'] == 'empresa':
                if current_user['empresa_id'] != empresa_id:
                    return jsonify({
                        'success': False,
                        'errors': ['No puedes eliminar usuarios de otra empresa']
                    }), 403
            elif current_user['tipo'] != 'admin':
                return jsonify({
                    'success': False,
                    'errors': ['Se requieren permisos de empresa o administrador']
                }), 403
            
            result = self.usuario_service.delete_usuario_for_empresa(usuario_id, empresa_id)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result['message']
                }), result['status_code']
            else:
                return jsonify({
                    'success': False,
                    'errors': result['errors']
                }), result['status_code']
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500