from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import Database
from routes import register_routes

def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración de la aplicación
    app.config.from_object(Config)
    
    # Habilitar CORS
    CORS(app)
    
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
                'users': '/api/users',
                'create_user': 'POST /api/users',
                'get_users': 'GET /api/users',
                'get_user': 'GET /api/users/<id>',
                'update_user': 'PUT /api/users/<id>',
                'delete_user': 'DELETE /api/users/<id>',
                'users_by_age': 'GET /api/users/age-range?min_age=18&max_age=30'
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
        port=5000,
        debug=Config.DEBUG
    )