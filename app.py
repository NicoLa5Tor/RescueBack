from flask import Flask, jsonify, request, make_response, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from database import Database
from routes import register_routes
from services.activity_service import ActivityService

def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración de la aplicación
    app.config.from_object(Config)
    
    # Habilitar CORS para todos los endpoints de la API
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Inicializar JWT
    JWTManager(app)

    @app.before_request
    def handle_options_requests():
        """Responde a las peticiones OPTIONS para evitar errores 404"""
        if request.method == 'OPTIONS':
            response = make_response()
            response.status_code = 204
            return response

    activity_service = ActivityService()

    @app.after_request
    def after_request_handler(response):
        """Agrega encabezados CORS y registra actividad"""
        empresa_id = getattr(g, 'empresa_id', None)
        if empresa_id:
            activity_service.log(str(empresa_id), request.method, request.path)
        response.headers.setdefault('Access-Control-Allow-Origin', '*')
        response.headers.setdefault('Access-Control-Allow-Headers',
                                   'Content-Type,Authorization')
        response.headers.setdefault('Access-Control-Allow-Methods',
                                   'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    # Inicializar base de datos
    db = Database()
    
    # Verificar conexión a la base de datos al iniciar
    if not db.test_connection():
        print("Error: No se pudo conectar a MongoDB")
        exit(1)
    
    # Registrar rutas
    register_routes(app)
    
    # Ruta de salud de la aplicación
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'OK',
            'message': 'API funcionando correctamente',
            'database': 'Connected' if db.test_connection() else 'Disconnected'
        }), 200
    
    # Ruta raíz
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'message': 'API CRUD con Flask y MongoDB',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'empresas': '/api/empresas',
                'create_empresa': 'POST /api/empresas',
                'get_empresas': 'GET /api/empresas',
                'hardware': '/api/hardware',
                'usuarios_empresa': '/empresas/<empresa_id>/usuarios',
                'auth_login': 'POST /auth/login'
            }
        }), 200
    
    # Manejo de errores 404
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint no encontrado',
            'message': 'La ruta solicitada no existe'
        }), 404
    
    # Manejo de errores 500
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'Ha ocurrido un error inesperado'
        }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5002,
        debug=Config.DEBUG
    )
