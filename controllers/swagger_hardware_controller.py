from flask import request
from flask_restx import Resource
from core.swagger_config import (
    hardware_ns,
    hardware_types_ns,
    hardware_model,
    hardware_response_model,
    hardware_type_model,
    hardware_type_response_model,
    success_response_model,
    error_response_model
)
from controllers.hardware_controller import HardwareController
from controllers.hardware_type_controller import HardwareTypeController

# Instancias de controladores
hardware_controller = HardwareController()
hardware_type_controller = HardwareTypeController()

@hardware_ns.route('/')
class HardwareAPI(Resource):
    @hardware_ns.expect(hardware_model)
    @hardware_ns.response(201, 'Hardware creado exitosamente', hardware_response_model)
    @hardware_ns.response(400, 'Datos inválidos', error_response_model)
    @hardware_ns.response(401, 'No autorizado', error_response_model)
    @hardware_ns.doc(security='Bearer', description='''
    Crea un nuevo dispositivo de hardware.
    
    **Requiere permisos:**
    - Token válido (cualquier rol)
    
    **Validaciones:**
    - empresa_nombre debe existir y estar activa
    - nombre debe ser único por empresa
    - tipo debe existir en hardware_types
    - sede debe existir en la empresa especificada
    
    **Campos obligatorios:**
    - empresa_nombre: Nombre de la empresa propietaria
    - nombre: Nombre único del hardware
    - tipo: Tipo de hardware (botonera, semaforo, televisor, etc.)
    - sede: Sede donde está ubicado el hardware
    
    **Campos opcionales:**
    - datos: Objeto JSON con información adicional del hardware
    ''')
    def post(self):
        """Crear un nuevo hardware"""
        try:
            response = hardware_controller.create_hardware()
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

    @hardware_ns.response(200, 'Lista de hardware', [hardware_response_model])
    @hardware_ns.response(401, 'No autorizado', error_response_model)
    @hardware_ns.doc(security='Bearer', description='''
    Obtiene todos los dispositivos de hardware del sistema.
    
    **Requiere permisos:**
    - Token válido (cualquier rol)
    
    **Respuesta:**
    - Lista completa de hardware con información de empresa
    - Estado activo/inactivo de cada dispositivo
    - Información de tipo y ubicación
    ''')
    def get(self):
        """Obtener todos los dispositivos de hardware"""
        try:
            response = hardware_controller.get_hardware()
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

@hardware_ns.route('/<string:hardware_id>')
class HardwareDetailAPI(Resource):
    @hardware_ns.response(200, 'Hardware encontrado', hardware_response_model)
    @hardware_ns.response(404, 'Hardware no encontrado', error_response_model)
    @hardware_ns.response(401, 'No autorizado', error_response_model)
    @hardware_ns.doc(security='Bearer', description='''
    Obtiene un dispositivo de hardware específico por su ID.
    
    **Requiere permisos:**
    - Token válido (cualquier rol)
    
    **Validaciones:**
    - El ID debe existir en el sistema
    ''')
    def get(self, hardware_id):
        """Obtener hardware por ID"""
        try:
            response = hardware_controller.get_hardware_by_id(hardware_id)
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

    @hardware_ns.expect(hardware_model)
    @hardware_ns.response(200, 'Hardware actualizado', hardware_response_model)
    @hardware_ns.response(404, 'Hardware no encontrado', error_response_model)
    @hardware_ns.response(401, 'No autorizado', error_response_model)
    @hardware_ns.doc(security='Bearer', description='''
    Actualiza un dispositivo de hardware existente.
    
    **Requiere permisos:**
    - Token válido (cualquier rol)
    
    **Campos actualizables:**
    - nombre, tipo, sede, datos
    - empresa_nombre (requiere validación)
    
    **Validaciones:**
    - Nuevo nombre debe ser único por empresa
    - Nuevo tipo debe existir en hardware_types
    - Nueva sede debe existir en la empresa
    ''')
    def put(self, hardware_id):
        """Actualizar hardware"""
        try:
            response = hardware_controller.update_hardware(hardware_id)
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

    @hardware_ns.response(200, 'Hardware eliminado', success_response_model)
    @hardware_ns.response(404, 'Hardware no encontrado', error_response_model)
    @hardware_ns.response(401, 'No autorizado', error_response_model)
    @hardware_ns.doc(security='Bearer', description='''
    Elimina un dispositivo de hardware del sistema.
    
    **Requiere permisos:**
    - Token válido (cualquier rol)
    
    **Proceso:**
    - Eliminación lógica (marca como inactivo)
    - Mantiene datos para auditoría
    - Afecta alertas y registros asociados
    ''')
    def delete(self, hardware_id):
        """Eliminar hardware"""
        try:
            response = hardware_controller.delete_hardware(hardware_id)
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

@hardware_ns.route('/empresa/<string:empresa_id>')
class HardwarePorEmpresaAPI(Resource):
    @hardware_ns.response(200, 'Hardware de la empresa', [hardware_response_model])
    @hardware_ns.response(404, 'Empresa no encontrada', error_response_model)
    @hardware_ns.response(401, 'No autorizado', error_response_model)
    @hardware_ns.doc(security='Bearer', description='''
    Obtiene todos los dispositivos de hardware de una empresa específica.
    
    **Requiere permisos:**
    - Token válido (cualquier rol)
    
    **Funcionalidad:**
    - Filtra hardware por empresa_id
    - Incluye solo hardware activo
    - Agrupa por sedes de la empresa
    ''')
    def get(self, empresa_id):
        """Obtener hardware por empresa"""
        try:
            response = hardware_controller.get_hardware_by_empresa(empresa_id)
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

# ===== ENDPOINTS DE TIPOS DE HARDWARE =====

@hardware_types_ns.route('/')
class HardwareTypesAPI(Resource):
    @hardware_types_ns.expect(hardware_type_model)
    @hardware_types_ns.response(201, 'Tipo de hardware creado', hardware_type_response_model)
    @hardware_types_ns.response(400, 'Datos inválidos', error_response_model)
    @hardware_types_ns.response(401, 'No autorizado', error_response_model)
    @hardware_types_ns.doc(security='Bearer', description='''
    Crea un nuevo tipo de hardware.
    
    **Requiere permisos:**
    - Token de super_admin
    
    **Validaciones:**
    - nombre debe ser único
    - nombre no puede estar vacío
    
    **Tipos por defecto:**
    - botonera, semaforo, televisor
    
    **Uso:**
    - Define qué tipos de dispositivos acepta el sistema
    - Usado en validación al crear hardware
    ''')
    def post(self):
        """Crear un nuevo tipo de hardware"""
        try:
            response = hardware_type_controller.create_hardware_type()
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

    @hardware_types_ns.response(200, 'Lista de tipos de hardware', [hardware_type_response_model])
    @hardware_types_ns.response(401, 'No autorizado', error_response_model)
    @hardware_types_ns.doc(security='Bearer', description='''
    Obtiene todos los tipos de hardware disponibles.
    
    **Requiere permisos:**
    - Token válido (cualquier rol)
    
    **Respuesta:**
    - Lista completa de tipos disponibles
    - Estado activo/inactivo de cada tipo
    - Usado para validación en formularios
    ''')
    def get(self):
        """Obtener todos los tipos de hardware"""
        try:
            response = hardware_type_controller.get_hardware_types()
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

@hardware_types_ns.route('/<string:type_id>')
class HardwareTypeDetailAPI(Resource):
    @hardware_types_ns.response(200, 'Tipo encontrado', hardware_type_response_model)
    @hardware_types_ns.response(404, 'Tipo no encontrado', error_response_model)
    @hardware_types_ns.response(401, 'No autorizado', error_response_model)
    @hardware_types_ns.doc(security='Bearer', description='''
    Obtiene un tipo de hardware específico por su ID.
    
    **Requiere permisos:**
    - Token válido (cualquier rol)
    
    **Validaciones:**
    - El ID debe existir en el sistema
    ''')
    def get(self, type_id):
        """Obtener tipo de hardware por ID"""
        try:
            response = hardware_type_controller.get_hardware_type_by_id(type_id)
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

    @hardware_types_ns.expect(hardware_type_model)
    @hardware_types_ns.response(200, 'Tipo actualizado', hardware_type_response_model)
    @hardware_types_ns.response(404, 'Tipo no encontrado', error_response_model)
    @hardware_types_ns.response(401, 'No autorizado', error_response_model)
    @hardware_types_ns.doc(security='Bearer', description='''
    Actualiza un tipo de hardware existente.
    
    **Requiere permisos:**
    - Token de super_admin
    
    **Campos actualizables:**
    - nombre (debe seguir siendo único)
    
    **Consideraciones:**
    - Afecta hardware existente que use este tipo
    - Validar que no rompa integridad referencial
    ''')
    def put(self, type_id):
        """Actualizar tipo de hardware"""
        try:
            response = hardware_type_controller.update_hardware_type(type_id)
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500

    @hardware_types_ns.response(200, 'Tipo eliminado', success_response_model)
    @hardware_types_ns.response(404, 'Tipo no encontrado', error_response_model)
    @hardware_types_ns.response(401, 'No autorizado', error_response_model)
    @hardware_types_ns.doc(security='Bearer', description='''
    Elimina un tipo de hardware del sistema.
    
    **Requiere permisos:**
    - Token de super_admin
    
    **Proceso:**
    - Eliminación lógica (marca como inactivo)
    - Verificar que no esté en uso por hardware existente
    - Mantiene datos para auditoría
    ''')
    def delete(self, type_id):
        """Eliminar tipo de hardware"""
        try:
            response = hardware_type_controller.delete_hardware_type(type_id)
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
                return data, response.status_code
            return response
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}, 500