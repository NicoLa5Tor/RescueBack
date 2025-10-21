from flask_restx import Api, Resource, fields
from flask import Blueprint

# Crear blueprint para la API documentada
api_bp = Blueprint('api_docs', __name__)

# Configurar Flask-RESTX
api = Api(
    api_bp,
    version='1.0',
    title='RESCUE Backend API',
    description='API para el sistema RESCUE - Gestión de operaciones de rescate con arquitectura multi-tenant',
    doc='/docs/',  # URL donde estará disponible la documentación
    prefix='/api/v1',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'auth_token',
            'description': 'Access token como cookie HTTP-only'
        },
        'RefreshToken': {
            'type': 'apiKey',
            'in': 'cookie', 
            'name': 'refresh_token',
            'description': 'Refresh token como cookie HTTP-only'
        }
    },
    security='Bearer'
)

# Namespaces para la API
auth_ns = api.namespace('auth', description='Endpoints de autenticación')
empresas_ns = api.namespace('empresas', description='Gestión de empresas')
users_ns = api.namespace('users', description='Gestión de usuarios')
hardware_ns = api.namespace('hardware', description='Gestión de hardware')
hardware_types_ns = api.namespace('hardware-types', description='Tipos de hardware')
admin_ns = api.namespace('admin', description='Administración y dashboards')
multitenant_ns = api.namespace('multitenant', description='Endpoints multi-tenant por empresa')

# Modelos de datos para la documentación
login_model = api.model('Login', {
    'usuario': fields.String(required=True, description='Nombre de usuario o email', example='superadmin'),
    'password': fields.String(required=True, description='Contraseña', example='secreto')
})

user_response_model = api.model('UserResponse', {
    'id': fields.String(description='ID único del usuario'),
    'email': fields.String(description='Email del usuario'),
    'username': fields.String(description='Nombre de usuario'),
    'role': fields.String(description='Rol del usuario', enum=['super_admin', 'admin', 'empresa']),
    'permisos': fields.List(fields.String, description='Lista de endpoints permitidos'),
    'is_super_admin': fields.Boolean(description='Indica si es super administrador')
})

success_response_model = api.model('SuccessResponse', {
    'success': fields.Boolean(description='Indica si la operación fue exitosa'),
    'message': fields.String(description='Mensaje descriptivo'),
    'data': fields.Raw(description='Datos de respuesta')
})

error_response_model = api.model('ErrorResponse', {
    'success': fields.Boolean(description='Siempre false para errores'),
    'errors': fields.List(fields.String, description='Lista de mensajes de error')
})

login_response_model = api.model('LoginResponse', {
    'success': fields.Boolean(description='Indica si el login fue exitoso'),
    'user': fields.Nested(user_response_model, description='Datos del usuario autenticado'),
    'message': fields.String(description='Mensaje descriptivo')
})

# Modelo para refresh token response
refresh_response_model = api.model('RefreshResponse', {
    'success': fields.Boolean(description='Indica si el refresh fue exitoso'),
    'message': fields.String(description='Mensaje descriptivo')
})

# Modelo para empresas
empresa_model = api.model('Empresa', {
    'nombre': fields.String(required=True, description='Nombre de la empresa'),
    'descripcion': fields.String(description='Descripción de la empresa'),
    'ubicacion': fields.String(description='Ubicación de la empresa'),
    'sedes': fields.List(fields.String, description='Lista de sedes de la empresa'),
    'username': fields.String(required=True, description='Nombre de usuario para login'),
    'email': fields.String(required=True, description='Email de la empresa'),
    'password': fields.String(required=True, description='Contraseña')
})

empresa_response_model = api.model('EmpresaResponse', {
    'id': fields.String(description='ID único de la empresa'),
    'nombre': fields.String(description='Nombre de la empresa'),
    'descripcion': fields.String(description='Descripción de la empresa'),
    'ubicacion': fields.String(description='Ubicación de la empresa'),
    'sedes': fields.List(fields.String, description='Lista de sedes'),
    'username': fields.String(description='Nombre de usuario'),
    'email': fields.String(description='Email de la empresa'),
    'activa': fields.Boolean(description='Estado de la empresa'),
    'created_by': fields.String(description='ID del super admin que la creó')
})

# Modelo para usuarios
user_model = api.model('User', {
    'name': fields.String(required=True, description='Nombre del usuario'),
    'email': fields.String(required=True, description='Email del usuario'),
    'age': fields.Integer(description='Edad del usuario'),
    'empresa_id': fields.String(required=True, description='ID de la empresa a la que pertenece'),
    'telefono': fields.String(required=True, description='Número de teléfono')
})

user_response_model = api.model('UserResponse', {
    'id': fields.String(description='ID único del usuario'),
    'name': fields.String(description='Nombre del usuario'),
    'email': fields.String(description='Email del usuario'),
    'age': fields.Integer(description='Edad del usuario'),
    'empresa_id': fields.String(description='ID de la empresa'),
    'telefono': fields.String(description='Teléfono del usuario'),
    'whatsapp_verify': fields.Boolean(description='Estado de verificación WhatsApp')
})

# Modelo para hardware
hardware_model = api.model('Hardware', {
    'empresa_nombre': fields.String(required=True, description='Nombre de la empresa'),
    'nombre': fields.String(required=True, description='Nombre único del hardware'),
    'tipo': fields.String(required=True, description='Tipo de hardware', enum=['botonera', 'semaforo', 'televisor']),
    'sede': fields.String(required=True, description='Sede donde está ubicado el hardware'),
    'datos': fields.Raw(description='Datos adicionales del hardware')
})

hardware_response_model = api.model('HardwareResponse', {
    'id': fields.String(description='ID único del hardware'),
    'empresa_id': fields.String(description='ID de la empresa'),
    'empresa_nombre': fields.String(description='Nombre de la empresa'),
    'nombre': fields.String(description='Nombre del hardware'),
    'tipo': fields.String(description='Tipo de hardware'),
    'sede': fields.String(description='Sede donde está ubicado'),
    'datos': fields.Raw(description='Datos adicionales'),
    'activo': fields.Boolean(description='Estado del hardware')
})

# Modelo para tipos de hardware
hardware_type_model = api.model('HardwareType', {
    'nombre': fields.String(required=True, description='Nombre del tipo de hardware')
})

hardware_type_response_model = api.model('HardwareTypeResponse', {
    'id': fields.String(description='ID único del tipo'),
    'nombre': fields.String(description='Nombre del tipo de hardware'),
    'activo': fields.Boolean(description='Estado del tipo')
})

# Modelo para usuarios multi-tenant
multitenant_user_model = api.model('MultitenantUser', {
    'nombre': fields.String(required=True, description='Nombre del usuario'),
    'cedula': fields.String(required=True, description='Número de cédula'),
    'rol': fields.String(required=True, description='Rol del usuario (debe existir en la empresa)')
})

multitenant_user_response_model = api.model('MultitenantUserResponse', {
    'id': fields.String(description='ID único del usuario'),
    'nombre': fields.String(description='Nombre del usuario'),
    'cedula': fields.String(description='Cédula del usuario'),
    'rol': fields.String(description='Rol del usuario'),
    'empresa_id': fields.String(description='ID de la empresa')
})

# Importar los controladores para registrar las rutas
from controllers.swagger_auth_controller import *
from controllers.swagger_empresas_controller import *
from controllers.swagger_users_controller import *
from controllers.swagger_hardware_controller import *
from controllers.swagger_admin_controller import *
from controllers.swagger_multitenant_controller import *

