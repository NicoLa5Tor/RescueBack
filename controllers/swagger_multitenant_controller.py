from flask import request
from flask_restx import Resource
from core.swagger_config import (
    multitenant_ns,
    multitenant_user_model,
    multitenant_user_response_model,
    success_response_model,
    error_response_model
)
from controllers.multitenant_controller import MultiTenantController

multitenant_controller = MultiTenantController()

@multitenant_ns.route('/empresas/<string:empresa_id>/usuarios')
class MultitenantUsersAPI(Resource):
    @multitenant_ns.expect(multitenant_user_model)
    @multitenant_ns.response(201, 'Usuario creado', multitenant_user_response_model)
    @multitenant_ns.response(400, 'Datos inválidos', error_response_model)
    @multitenant_ns.doc(description='''
    Crear usuario para una empresa específica.
    
    **Campos obligatorios:**
    - nombre: Nombre del usuario
    - cedula: Número de cédula único
    - rol: Rol del usuario (operador, supervisor)
    
    **Nota:**
    - Estos usuarios no pueden iniciar sesión en la API
    - Son para uso interno de la empresa
    ''')
    def post(self, empresa_id):
        """Crear usuario para empresa"""
        try:
            response = multitenant_controller.create_usuario_for_empresa(empresa_id)
            if hasattr(response, 'get_json'):
                return response.get_json(), response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

    @multitenant_ns.response(200, 'Usuarios de empresa', [multitenant_user_response_model])
    @multitenant_ns.response(404, 'Empresa no encontrada', error_response_model)
    @multitenant_ns.doc(description='Listar usuarios de una empresa')
    def get(self, empresa_id):
        """Obtener usuarios de empresa"""
        try:
            response = multitenant_controller.get_usuarios_by_empresa(empresa_id)
            if hasattr(response, 'get_json'):
                return response.get_json(), response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

@multitenant_ns.route('/empresas/<string:empresa_id>/usuarios/<string:usuario_id>')
class MultitenantUserDetailAPI(Resource):
    @multitenant_ns.response(200, 'Usuario encontrado', multitenant_user_response_model)
    @multitenant_ns.response(404, 'Usuario no encontrado', error_response_model)
    @multitenant_ns.doc(description='Obtener usuario específico de empresa')
    def get(self, empresa_id, usuario_id):
        """Obtener usuario de empresa"""
        try:
            response = multitenant_controller.get_usuario_by_empresa(empresa_id, usuario_id)
            if hasattr(response, 'get_json'):
                return response.get_json(), response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

    @multitenant_ns.expect(multitenant_user_model)
    @multitenant_ns.response(200, 'Usuario actualizado', multitenant_user_response_model)
    @multitenant_ns.response(404, 'Usuario no encontrado', error_response_model)
    @multitenant_ns.doc(description='Actualizar usuario de empresa')
    def put(self, empresa_id, usuario_id):
        """Actualizar usuario de empresa"""
        try:
            response = multitenant_controller.update_usuario_by_empresa(empresa_id, usuario_id)
            if hasattr(response, 'get_json'):
                return response.get_json(), response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

    @multitenant_ns.response(200, 'Usuario eliminado', success_response_model)
    @multitenant_ns.response(404, 'Usuario no encontrado', error_response_model)
    @multitenant_ns.doc(description='Eliminar usuario de empresa')
    def delete(self, empresa_id, usuario_id):
        """Eliminar usuario de empresa"""
        try:
            response = multitenant_controller.delete_usuario_by_empresa(empresa_id, usuario_id)
            if hasattr(response, 'get_json'):
                return response.get_json(), response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500