from flask import Blueprint
from controllers.user_controller import UserController
from controllers.empresa_controller import EmpresaController
from controllers.admin_controller import AdminController
from controllers.auth_controller import AuthController

# ========== BLUEPRINT DE AUTENTICACIÓN ==========
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_controller = AuthController()

@auth_bp.route('/login', methods=['POST'])
def login():
    """POST /auth/login - Iniciar sesión"""
    return auth_controller.login()

# ========== BLUEPRINT DE USUARIOS ==========
user_bp = Blueprint('users', __name__, url_prefix='/api/users')
user_controller = UserController()

@user_bp.route('/', methods=['POST'])
def create_user():
    """POST /api/users - Crear usuario"""
    return user_controller.create_user()

@user_bp.route('/', methods=['GET'])
def get_all_users():
    """GET /api/users - Obtener todos los usuarios"""
    return user_controller.get_all_users()

@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    """GET /api/users/<id> - Obtener usuario por ID"""
    return user_controller.get_user(user_id)

@user_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    """PUT /api/users/<id> - Actualizar usuario"""
    return user_controller.update_user(user_id)

@user_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """DELETE /api/users/<id> - Eliminar usuario"""
    return user_controller.delete_user(user_id)

@user_bp.route('/age-range', methods=['GET'])
def get_users_by_age():
    """GET /api/users/age-range?min_age=18&max_age=30 - Obtener usuarios por rango de edad"""
    return user_controller.get_users_by_age()

@user_bp.route('/buscar-por-telefono', methods=['GET'])
def get_user_by_phone():
    """GET /api/users/buscar-por-telefono?telefono=<numero> - Obtener usuario por telefono"""
    return user_controller.get_user_by_phone()

# ========== BLUEPRINT DE EMPRESAS ==========
empresa_bp = Blueprint('empresas', __name__, url_prefix='/api/empresas')
empresa_controller = EmpresaController()

@empresa_bp.route('/', methods=['POST'])
def create_empresa():
    """POST /api/empresas - Crear empresa (solo super admin)"""
    return empresa_controller.create_empresa()

@empresa_bp.route('/', methods=['GET'])
def get_all_empresas():
    """GET /api/empresas - Obtener todas las empresas activas"""
    return empresa_controller.get_all_empresas()

@empresa_bp.route('/<empresa_id>', methods=['GET'])
def get_empresa(empresa_id):
    """GET /api/empresas/<id> - Obtener empresa por ID"""
    return empresa_controller.get_empresa(empresa_id)

@empresa_bp.route('/<empresa_id>', methods=['PUT'])
def update_empresa(empresa_id):
    """PUT /api/empresas/<id> - Actualizar empresa (solo el creador)"""
    return empresa_controller.update_empresa(empresa_id)

@empresa_bp.route('/<empresa_id>', methods=['DELETE'])
def delete_empresa(empresa_id):
    """DELETE /api/empresas/<id> - Eliminar empresa (solo el creador)"""
    return empresa_controller.delete_empresa(empresa_id)

@empresa_bp.route('/mis-empresas', methods=['GET'])
def get_my_empresas():
    """GET /api/empresas/mis-empresas - Obtener empresas del super admin autenticado"""
    return empresa_controller.get_my_empresas()

@empresa_bp.route('/buscar-por-ubicacion', methods=['GET'])
def search_by_ubicacion():
    """GET /api/empresas/buscar-por-ubicacion?ubicacion=<ubicacion> - Buscar por ubicación"""
    return empresa_controller.search_empresas_by_ubicacion()

@empresa_bp.route('/estadisticas', methods=['GET'])
def get_stats():
    """GET /api/empresas/estadisticas - Obtener estadísticas (solo super admin)"""
    return empresa_controller.get_empresa_stats()
@empresa_bp.route('/<empresa_id>/activity', methods=['GET'])
def empresa_activity(empresa_id):
    return admin_controller.get_empresa_activity(empresa_id)

# ========== BLUEPRINT DE ADMIN ==========
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
admin_controller = AdminController()

@admin_bp.route('/activity', methods=['GET'])
def get_admin_activity():
    return admin_controller.get_activity()

@admin_bp.route('/activity-admin', methods=['GET'])
def get_admin_activity_only():
    return admin_controller.get_activity_admin_only()

@admin_bp.route('/distribution', methods=['GET'])
def get_admin_distribution():
    return admin_controller.get_distribution()
# ========== BLUEPRINT DE MULTI-TENANT (USUARIOS POR EMPRESA) ==========
from controllers.multitenant_controller import MultiTenantController

multitenant_bp = Blueprint('multitenant', __name__, url_prefix='/empresas')
multitenant_controller = MultiTenantController()

@multitenant_bp.route('/<empresa_id>/usuarios', methods=['POST'])
def create_usuario_for_empresa(empresa_id):
    """POST /empresas/<empresa_id>/usuarios - Crear usuario para empresa específica"""
    return multitenant_controller.create_usuario_for_empresa(empresa_id)

@multitenant_bp.route('/<empresa_id>/usuarios', methods=['GET'])
def get_usuarios_by_empresa(empresa_id):
    """GET /empresas/<empresa_id>/usuarios - Obtener usuarios de una empresa"""
    return multitenant_controller.get_usuarios_by_empresa(empresa_id)

@multitenant_bp.route('/<empresa_id>/usuarios/<usuario_id>', methods=['GET'])
def get_usuario_by_empresa(empresa_id, usuario_id):
    """GET /empresas/<empresa_id>/usuarios/<usuario_id> - Obtener usuario específico"""
    return multitenant_controller.get_usuario_by_empresa(empresa_id, usuario_id)

@multitenant_bp.route('/<empresa_id>/usuarios/<usuario_id>', methods=['PUT'])
def update_usuario_by_empresa(empresa_id, usuario_id):
    """PUT /empresas/<empresa_id>/usuarios/<usuario_id> - Actualizar usuario"""
    return multitenant_controller.update_usuario_by_empresa(empresa_id, usuario_id)

@multitenant_bp.route('/<empresa_id>/usuarios/<usuario_id>', methods=['DELETE'])
def delete_usuario_by_empresa(empresa_id, usuario_id):
    """DELETE /empresas/<empresa_id>/usuarios/<usuario_id> - Eliminar usuario"""
    return multitenant_controller.delete_usuario_by_empresa(empresa_id, usuario_id)

# ========== FUNCIÓN PARA REGISTRAR TODAS LAS RUTAS ==========
def register_routes(app):
    """Registra todos los blueprints en la aplicación Flask"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(empresa_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(multitenant_bp)
