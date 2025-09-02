from flask import request
from flask_restx import Resource
from core.swagger_config import (
    users_ns,
    user_model,
    user_response_model,
    success_response_model,
    error_response_model
)

# Para acceder a los servicios necesarios
from services.user_service import UserService
from services.empresa_service import EmpresaService

user_service = UserService()
empresa_service = EmpresaService()

@users_ns.route('/')
class UsersAPI(Resource):
    @users_ns.expect(user_model)
    @users_ns.response(201, 'Usuario creado exitosamente', user_response_model)
    @users_ns.response(400, 'Datos inválidos', error_response_model)
    @users_ns.response(401, 'No autorizado', error_response_model)
    @users_ns.doc(security='Bearer', description='''
    Crea un nuevo usuario en el sistema.
    
    **Requiere permisos:**
    - Token válido (cualquier rol)
    
    **Validaciones:**
    - empresa_id debe existir y estar activa
    - telefono es obligatorio
    - email debe ser único
    - whatsapp_verify se establece automáticamente en false
    
    **Campos obligatorios:**
    - name: Nombre del usuario
    - email: Email único del usuario  
    - empresa_id: ID de empresa existente
    - telefono: Número de teléfono
    
    **Campos opcionales:**
    - age: Edad del usuario
    ''')
    def post(self):
        """Crear un nuevo usuario"""
        try:
            data = request.get_json() or {}
            
            # Validaciones básicas
            required_fields = ['name', 'email', 'empresa_id', 'telefono']
            for field in required_fields:
                if not data.get(field):
                    return {'success': False, 'errors': [f'Campo {field} es obligatorio']}, 400
            
            # Validar que la empresa existe
            empresa = empresa_service.get_empresa_by_id(data['empresa_id'])
            if not empresa:
                return {'success': False, 'errors': ['La empresa especificada no existe']}, 400
            
            # Crear usuario
            result = user_service.create_user(data)
            
            if result['success']:
                return {
                    'success': True,
                    'message': 'Usuario creado correctamente',
                    'data': result['data']
                }, 201
            else:
                return {'success': False, 'errors': result.get('errors', ['Error al crear usuario'])}, 400
                
        except Exception as e:
            return {'success': False, 'errors': ['Error interno del servidor']}, 500

    @users_ns.response(200, 'Lista de usuarios', [user_response_model])
    @users_ns.response(401, 'No autorizado', error_response_model)
    @users_ns.doc(security='Bearer', description='''
    Obtiene todos los usuarios del sistema.
    
    **Requiere permisos:**
    - Token válido (cualquier rol)
    
    **Respuesta:**
    - Lista completa de usuarios con sus datos
    - Incluye información de empresa asociada
    - Información de verificación WhatsApp
    ''')
    def get(self):
        """Obtener todos los usuarios"""
        try:
            result = user_service.get_all_users()
            
            return {
                'success': True,
                'data': result['data'],
                'count': len(result['data'])
            }, 200
            
        except Exception as e:
            return {'success': False, 'errors': ['Error interno del servidor']}, 500

@users_ns.route('/<string:user_id>')
class UserAPI(Resource):
    @users_ns.response(200, 'Usuario encontrado', user_response_model)
    @users_ns.response(404, 'Usuario no encontrado', error_response_model)
    @users_ns.response(401, 'No autorizado', error_response_model)
    @users_ns.doc(security='Bearer', description='''
    Obtiene un usuario específico por su ID.
    
    **Requiere permisos:**
    - Token válido (cualquier rol)
    
    **Validaciones:**
    - El ID debe existir en el sistema
    ''')
    def get(self, user_id):
        """Obtener usuario por ID"""
        try:
            result = user_service.get_user_by_id(user_id)
            
            if result:
                return {
                    'success': True,
                    'data': result
                }, 200
            else:
                return {'success': False, 'errors': ['Usuario no encontrado']}, 404
                
        except Exception as e:
            return {'success': False, 'errors': ['Error interno del servidor']}, 500

    @users_ns.expect(user_model)
    @users_ns.response(200, 'Usuario actualizado', user_response_model)
    @users_ns.response(404, 'Usuario no encontrado', error_response_model)
    @users_ns.response(401, 'No autorizado', error_response_model)
    @users_ns.doc(security='Bearer', description='''
    Actualiza un usuario existente.
    
    **Requiere permisos:**
    - Token válido (cualquier rol)
    
    **Campos actualizables:**
    - name, email, age, telefono
    - empresa_id (debe existir la nueva empresa)
    - whatsapp_verify
    
    **Validaciones:**
    - Email debe seguir siendo único
    - Si cambia empresa_id, debe existir la nueva empresa
    ''')
    def put(self, user_id):
        """Actualizar usuario"""
        try:
            data = request.get_json() or {}
            
            # Si se proporciona empresa_id, validar que existe
            if 'empresa_id' in data:
                empresa = empresa_service.get_empresa_by_id(data['empresa_id'])
                if not empresa:
                    return {'success': False, 'errors': ['La empresa especificada no existe']}, 400
            
            result = user_service.update_user(user_id, data)
            
            if result['success']:
                return {
                    'success': True,
                    'message': 'Usuario actualizado correctamente',
                    'data': result['data']
                }, 200
            else:
                return {'success': False, 'errors': result.get('errors', ['Error al actualizar usuario'])}, 400
                
        except Exception as e:
            return {'success': False, 'errors': ['Error interno del servidor']}, 500

    @users_ns.response(200, 'Usuario eliminado', success_response_model)
    @users_ns.response(404, 'Usuario no encontrado', error_response_model)
    @users_ns.response(401, 'No autorizado', error_response_model)
    @users_ns.doc(security='Bearer', description='''
    Elimina un usuario del sistema.
    
    **Requiere permisos:**
    - Token válido (cualquier rol)
    
    **Proceso:**
    - Eliminación física del usuario
    - No se puede deshacer la operación
    ''')
    def delete(self, user_id):
        """Eliminar usuario"""
        try:
            result = user_service.delete_user(user_id)
            
            if result['success']:
                return {
                    'success': True,
                    'message': 'Usuario eliminado correctamente'
                }, 200
            else:
                return {'success': False, 'errors': result.get('errors', ['Error al eliminar usuario'])}, 400
                
        except Exception as e:
            return {'success': False, 'errors': ['Error interno del servidor']}, 500

@users_ns.route('/age-range')
class UsersAgeRangeAPI(Resource):
    @users_ns.param('min_age', 'Edad mínima', type='integer', required=True)
    @users_ns.param('max_age', 'Edad máxima', type='integer', required=True)
    @users_ns.response(200, 'Usuarios encontrados', [user_response_model])
    @users_ns.response(400, 'Parámetros inválidos', error_response_model)
    @users_ns.response(401, 'No autorizado', error_response_model)
    @users_ns.doc(security='Bearer', description='''
    Busca usuarios por rango de edad.
    
    **Requiere permisos:**
    - Token válido (cualquier rol)
    
    **Parámetros:**
    - min_age: Edad mínima (incluida)
    - max_age: Edad máxima (incluida)
    
    **Funcionalidad:**
    - Filtra usuarios dentro del rango especificado
    - Útil para segmentación demográfica
    ''')
    def get(self):
        """Buscar usuarios por rango de edad"""
        try:
            min_age = request.args.get('min_age', type=int)
            max_age = request.args.get('max_age', type=int)
            
            if min_age is None or max_age is None:
                return {'success': False, 'errors': ['min_age y max_age son obligatorios']}, 400
            
            if min_age < 0 or max_age < 0 or min_age > max_age:
                return {'success': False, 'errors': ['Rango de edad inválido']}, 400
            
            result = user_service.get_users_by_age_range(min_age, max_age)
            
            return {
                'success': True,
                'data': result['data'],
                'count': len(result['data'])
            }, 200
            
        except Exception as e:
            return {'success': False, 'errors': ['Error interno del servidor']}, 500

@users_ns.route('/buscar-por-telefono')
class BuscarUsuarioPorTelefonoAPI(Resource):
    @users_ns.param('telefono', 'Número de teléfono a buscar', required=True)
    @users_ns.response(200, 'Usuario encontrado', user_response_model)
    @users_ns.response(404, 'Usuario no encontrado', error_response_model)
    @users_ns.response(400, 'Parámetro faltante', error_response_model)
    @users_ns.response(401, 'No autorizado', error_response_model)
    @users_ns.doc(security='Bearer', description='''
    Busca un usuario por su número de teléfono.
    
    **Requiere permisos:**
    - Token válido (cualquier rol)
    
    **Parámetros:**
    - telefono: Número de teléfono exacto
    
    **Funcionalidad:**
    - Búsqueda exacta por número de teléfono
    - Útil para verificaciones y soporte
    ''')
    def get(self):
        """Buscar usuario por teléfono"""
        try:
            telefono = request.args.get('telefono')
            
            if not telefono:
                return {'success': False, 'errors': ['Parámetro telefono es obligatorio']}, 400
            
            result = user_service.get_user_by_phone(telefono)
            
            if result:
                return {
                    'success': True,
                    'data': result
                }, 200
            else:
                return {'success': False, 'errors': ['Usuario no encontrado']}, 404
                
        except Exception as e:
            return {'success': False, 'errors': ['Error interno del servidor']}, 500