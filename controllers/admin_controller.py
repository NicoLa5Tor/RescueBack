from flask import request, jsonify
from functools import wraps
from config import Config
from services.empresa_service import EmpresaService


def require_admin_token(f):
    """Decorator to ensure request contains valid admin token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-Admin-Token')
        if not token or token != Config.ADMIN_TOKEN:
            return jsonify({
                'success': False,
                'errors': ['Token de administrador inválido']
            }), 401
        return f(*args, **kwargs)
    return decorated_function


class AdminController:
    def __init__(self):
        self.empresa_service = EmpresaService()

    @require_admin_token
    def get_activity(self):
        """Return sample activity data for dashboard"""
        data = {
            'labels': ['L', 'M', 'X', 'J', 'V', 'S', 'D'],
            'values': [65, 78, 90, 85, 92, 88, 95],
            'label': 'Actividad'
        }
        return jsonify({'success': True, 'data': data}), 200

    @require_admin_token
    def get_empresa_activity(self, empresa_id):
        """Return activity data scoped to a company"""
        # In this demo we return static data regardless of empresa_id
        data = {
            'labels': ['L', 'M', 'X', 'J', 'V', 'S', 'D'],
            'values': [65, 78, 90, 85, 92, 88, 95],
            'label': 'Actividad'
        }
        return jsonify({'success': True, 'data': data}), 200

    @require_admin_token
    def get_distribution(self):
        """Return totals of registered companies"""
        result = self.empresa_service.get_empresa_stats()
        if result['success']:
            total = result['data']['total_general']
            distribution = {
                'labels': ['Empresas Registradas'],
                'values': [total]
            }
            return jsonify({'success': True, 'data': distribution}), 200
        return jsonify(result), 500

