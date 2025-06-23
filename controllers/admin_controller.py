from flask import request, jsonify
from functools import wraps
from config import Config
from services.dashboard_service import DashboardService
from utils.permissions import require_empresa_or_super_token


def require_admin_token(f):
    """Decorator to ensure request contains valid admin or super token"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("X-Admin-Token")
        super_token = request.headers.get("X-Super-Admin-Token")
        if token == Config.ADMIN_TOKEN or super_token == Config.SUPER_ADMIN_TOKEN:
            return f(*args, **kwargs)
        return (
            jsonify({"success": False, "errors": ["Token de administrador inválido"]}),
            401,
        )

    return decorated_function


class AdminController:
    def __init__(self):
        self.dashboard_service = DashboardService()

    @require_admin_token
    def get_activity(self):
        """Return sample activity data for dashboard"""
        result = self.dashboard_service.get_activity()
        return jsonify(result), 200 if result.get("success") else 500

    @require_empresa_or_super_token(require_empresa_id=True)
    def get_empresa_activity(self, empresa_id):
        """Return activity data scoped to a company"""
        result = self.dashboard_service.get_empresa_activity(empresa_id)
        return jsonify(result), 200 if result.get("success") else 500

    @require_admin_token
    def get_distribution(self):
        """Return totals of registered companies"""
        result = self.dashboard_service.get_distribution()
        return jsonify(result), 200 if result.get("success") else 500
