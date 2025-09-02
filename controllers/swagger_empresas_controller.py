from flask import request
from flask_restx import Resource
from core.swagger_config import (
    empresas_ns,
    empresa_model,
    empresa_response_model,
    success_response_model,
    error_response_model
)
from controllers.empresa_controller import EmpresaController

# Instancia del controlador original
empresa_controller = EmpresaController()

@empresas_ns.route('/')
class EmpresasAPI(Resource):
    @empresas_ns.expect(empresa_model)
    @empresas_ns.response(201, 'Empresa creada exitosamente', empresa_response_model)
    @empresas_ns.response(400, 'Datos inválidos', error_response_model)
    @empresas_ns.response(401, 'No autorizado', error_response_model)
    @empresas_ns.doc(security='Bearer', description='''
    Crea una nueva empresa en el sistema.
    
    **Requiere permisos:**
    - Token de super_admin
    
    **Funcionalidad:**
    - Crea empresa con credenciales de login
    - Genera usuario empresa con rol 'empresa'
    - Valida unicidad de username y email
    - Hashea la contraseña automáticamente
    
    **Campos obligatorios:**
    - nombre: Nombre de la empresa
    - username: Usuario único para login
    - email: Email único de la empresa  
    - password: Contraseña para autenticación
    
    **Campos opcionales:**
    - descripcion: Descripción de la empresa
    - ubicacion: Ubicación geográfica
    - sedes: Array con nombres de sedes
    ''')
    def post(self):
        """Crear una nueva empresa"""
        try:
            # Extraer datos del request
            response = empresa_controller.create_empresa()
            
            # Convertir respuesta Flask a datos para Flask-RESTX
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

    @empresas_ns.response(200, 'Lista de empresas', [empresa_response_model])
    @empresas_ns.response(401, 'No autorizado', error_response_model)
    @empresas_ns.doc(security='Bearer', description='''
    Obtiene todas las empresas del sistema.
    
    **Requiere permisos:**
    - Token de super_admin o admin
    
    **Respuesta:**
    - Lista completa de empresas con sus datos
    - Excluye información sensible como contraseñas
    - Incluye estado activo/inactivo de cada empresa
    ''')
    def get(self):
        """Obtener todas las empresas"""
        try:
            response = empresa_controller.get_empresas()
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

@empresas_ns.route('/<string:empresa_id>')
class EmpresaAPI(Resource):
    @empresas_ns.response(200, 'Empresa encontrada', empresa_response_model)
    @empresas_ns.response(404, 'Empresa no encontrada', error_response_model)
    @empresas_ns.response(401, 'No autorizado', error_response_model)
    @empresas_ns.doc(security='Bearer', description='''
    Obtiene una empresa específica por su ID.
    
    **Requiere permisos:**
    - Token de super_admin, admin, o la propia empresa
    
    **Validaciones:**
    - El ID debe existir en el sistema
    - El usuario debe tener permisos para ver esta empresa
    ''')
    def get(self, empresa_id):
        """Obtener empresa por ID"""
        try:
            response = empresa_controller.get_empresa(empresa_id)
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

    @empresas_ns.expect(empresa_model)
    @empresas_ns.response(200, 'Empresa actualizada', empresa_response_model)
    @empresas_ns.response(404, 'Empresa no encontrada', error_response_model)
    @empresas_ns.response(401, 'No autorizado', error_response_model)
    @empresas_ns.doc(security='Bearer', description='''
    Actualiza una empresa existente.
    
    **Requiere permisos:**
    - Token del super_admin que la creó, o la propia empresa
    
    **Campos actualizables:**
    - nombre, descripcion, ubicacion, sedes
    - username, email, password
    
    **Validaciones:**
    - Username y email deben seguir siendo únicos
    - Solo el creador o la empresa pueden modificarla
    ''')
    def put(self, empresa_id):
        """Actualizar empresa"""
        try:
            response = empresa_controller.update_empresa(empresa_id)
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

    @empresas_ns.response(200, 'Empresa eliminada', success_response_model)
    @empresas_ns.response(404, 'Empresa no encontrada', error_response_model)
    @empresas_ns.response(401, 'No autorizado', error_response_model)
    @empresas_ns.doc(security='Bearer', description='''
    Elimina una empresa del sistema.
    
    **Requiere permisos:**
    - Token del super_admin que la creó
    
    **Proceso:**
    - Eliminación lógica (marca como inactiva)
    - Mantiene datos para auditoría
    - Afecta usuarios y hardware asociados
    ''')
    def delete(self, empresa_id):
        """Eliminar empresa"""
        try:
            response = empresa_controller.delete_empresa(empresa_id)
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

@empresas_ns.route('/mis-empresas')
class MisEmpresasAPI(Resource):
    @empresas_ns.response(200, 'Empresas del super admin', [empresa_response_model])
    @empresas_ns.response(401, 'No autorizado', error_response_model)
    @empresas_ns.doc(security='Bearer', description='''
    Obtiene las empresas creadas por el super admin autenticado.
    
    **Requiere permisos:**
    - Token de super_admin
    
    **Funcionalidad:**
    - Filtra empresas por creador (created_by)
    - Solo muestra empresas del super admin actual
    - Útil para gestión multi-tenant
    ''')
    def get(self):
        """Obtener empresas creadas por el super admin actual"""
        try:
            response = empresa_controller.get_mis_empresas()
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

@empresas_ns.route('/buscar-por-ubicacion')
class BuscarEmpresasPorUbicacionAPI(Resource):
    @empresas_ns.param('ubicacion', 'Ubicación a buscar', required=True)
    @empresas_ns.response(200, 'Empresas encontradas', [empresa_response_model])
    @empresas_ns.response(400, 'Parámetro faltante', error_response_model)
    @empresas_ns.doc(description='''
    Busca empresas por ubicación geográfica.
    
    **Parámetros:**
    - ubicacion: String con la ubicación a buscar
    
    **Funcionalidad:**
    - Búsqueda parcial en el campo ubicación
    - No requiere autenticación (endpoint público)
    - Útil para filtros geográficos
    ''')
    def get(self):
        """Buscar empresas por ubicación"""
        try:
            response = empresa_controller.buscar_por_ubicacion()
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

@empresas_ns.route('/estadisticas')
class EstadisticasEmpresasAPI(Resource):
    @empresas_ns.response(200, 'Estadísticas de empresas', success_response_model)
    @empresas_ns.response(401, 'No autorizado', error_response_model)
    @empresas_ns.doc(security='Bearer', description='''
    Obtiene estadísticas generales de empresas.
    
    **Requiere permisos:**
    - Token de super_admin
    
    **Estadísticas incluidas:**
    - Total de empresas activas/inactivas
    - Distribución por ubicaciones
    - Empresas por fecha de creación
    - Métricas de uso del sistema
    ''')
    def get(self):
        """Obtener estadísticas de empresas"""
        try:
            response = empresa_controller.get_estadisticas()
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

@empresas_ns.route('/<string:empresa_id>/activity')
class ActividadEmpresaAPI(Resource):
    @empresas_ns.response(200, 'Actividad de la empresa', success_response_model)
    @empresas_ns.response(404, 'Empresa no encontrada', error_response_model)
    @empresas_ns.response(401, 'No autorizado', error_response_model)
    @empresas_ns.doc(security='Bearer', description='''
    Registra y consulta la actividad de una empresa específica.
    
    **Requiere permisos:**
    - Token de empresa o super_admin
    
    **Funcionalidad:**
    - Rastrea acceso y uso del sistema
    - Logs de actividad por empresa
    - Métricas de uso para auditoría
    ''')
    def get(self, empresa_id):
        """Obtener actividad de la empresa"""
        try:
            response = empresa_controller.get_activity(empresa_id)
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500