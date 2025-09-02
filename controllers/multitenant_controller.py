from flask import request, jsonify
from services.usuario_service import UsuarioService
from utils.permissions import require_empresa_or_admin_token

class MultiTenantController:
    def __init__(self):
        self.usuario_service = UsuarioService()
    
    @require_empresa_or_admin_token
    def create_usuario_for_empresa(self, empresa_id):
        """
        Endpoint: POST /empresas/<empresa_id>/usuarios
        Crea un usuario para una empresa específica
        """
        try:
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
    
    @require_empresa_or_admin_token
    def get_usuarios_by_empresa(self, empresa_id):
        """
        Endpoint: GET /empresas/<empresa_id>/usuarios
        Obtiene todos los usuarios de una empresa
        """
        try:
            result = self.usuario_service.get_usuarios_by_empresa(empresa_id)
            # print(f"los usuarios son: {result}")
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
    
    @require_empresa_or_admin_token
    def get_usuario_by_empresa(self, empresa_id, usuario_id):
        """
        Endpoint: GET /empresas/<empresa_id>/usuarios/<usuario_id>
        Obtiene un usuario específico de una empresa
        """
        try:
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
    
    @require_empresa_or_admin_token
    def update_usuario_by_empresa(self, empresa_id, usuario_id):
        """
        Endpoint: PUT /empresas/<empresa_id>/usuarios/<usuario_id>
        Actualiza un usuario específico de una empresa
        """
        try:
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
    
    @require_empresa_or_admin_token
    def delete_usuario_by_empresa(self, empresa_id, usuario_id):
        """
        Endpoint: DELETE /empresas/<empresa_id>/usuarios/<usuario_id>
        Elimina un usuario específico de una empresa
        """
        try:
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
    
    @require_empresa_or_admin_token
    def toggle_usuario_status(self, empresa_id, usuario_id):
        """
        Endpoint: PATCH /empresas/<empresa_id>/usuarios/<usuario_id>/toggle-status
        Activa o desactiva un usuario específico de una empresa
        """
        try:
            data = request.get_json() or {}
            activo = data.get('activo', True)
            
            result = self.usuario_service.toggle_usuario_status(usuario_id, empresa_id, activo)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result['message'],
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
    
    @require_empresa_or_admin_token
    def get_usuarios_by_empresa_including_inactive(self, empresa_id):
        """
        Endpoint: GET /empresas/<empresa_id>/usuarios/including-inactive
        Obtiene todos los usuarios de una empresa incluyendo inactivos
        """
        try:
            result = self.usuario_service.get_usuarios_by_empresa_including_inactive(empresa_id)
            # print(f"Los usuarios son: {result}")
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
