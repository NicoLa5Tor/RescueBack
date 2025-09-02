from flask import request
from flask_restx import Resource
from core.swagger_config import (
    admin_ns,
    success_response_model,
    error_response_model
)
from controllers.admin_controller import AdminController

admin_controller = AdminController()

@admin_ns.route('/activity')
class AdminActivityAPI(Resource):
    @admin_ns.response(200, 'Actividad de empresas', success_response_model)
    @admin_ns.response(401, 'No autorizado', error_response_model)
    @admin_ns.doc(security='Bearer', description='''
    Obtiene la actividad registrada de todas las empresas.
    
    **Requiere permisos:**
    - Token de administrador o super_admin
    
    **Funcionalidad:**
    - Logs de actividad de todas las empresas
    - Métricas de uso del sistema
    - Datos para dashboards administrativos
    ''')
    def get(self):
        """Obtener actividad de todas las empresas"""
        try:
            response = admin_controller.get_activity()
            if hasattr(response, 'get_json'):
                return response.get_json(), response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

@admin_ns.route('/activity-admin')  
class AdminActivityAdminAPI(Resource):
    @admin_ns.response(200, 'Actividad empresas (admin)', success_response_model)
    @admin_ns.response(401, 'No autorizado', error_response_model)
    @admin_ns.doc(security='Bearer', description='''
    Actividad de empresas específica para administradores.
    
    **Requiere permisos:**
    - Token de administrador únicamente
    ''')
    def get(self):
        """Actividad empresas para admin"""
        try:
            response = admin_controller.get_activity_admin()
            if hasattr(response, 'get_json'):
                return response.get_json(), response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

@admin_ns.route('/distribution')
class AdminDistributionAPI(Resource):
    @admin_ns.response(200, 'Distribución de empresas', success_response_model)
    @admin_ns.response(401, 'No autorizado', error_response_model)
    @admin_ns.doc(security='Bearer', description='''
    Obtiene la distribución geográfica de empresas.
    
    **Requiere permisos:**
    - Token de admin o super_admin
    ''')
    def get(self):
        """Distribución geográfica de empresas"""
        try:
            response = admin_controller.get_distribution()
            if hasattr(response, 'get_json'):
                return response.get_json(), response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500