from flask import jsonify
from services.dashboard_service import DashboardService
from utils.permissions import (
    require_super_admin_token,
    require_empresa_or_admin_token,
)

class AdminController:
    def __init__(self):
        self.dashboard_service = DashboardService()

    @require_super_admin_token
    def get_activity(self):
        """Return logged activity for all companies."""
        result = self.dashboard_service.get_activity()
        return jsonify(result), 200 if result.get("success") else 500

    @require_super_admin_token
    def get_activity_admin_only(self):
        """Return logged activity for all companies (solo admin)."""
        result = self.dashboard_service.get_activity()
        return jsonify(result), 200 if result.get("success") else 500

    @require_empresa_or_admin_token
    def get_empresa_activity(self, empresa_id):
        """Return logged activity for a specific company."""
        result = self.dashboard_service.get_empresa_activity(empresa_id)
        return jsonify(result), 200 if result.get("success") else 500

    @require_super_admin_token
    def get_distribution(self):
        """Return totals of registered companies"""
        result = self.dashboard_service.get_distribution()
        return jsonify(result), 200 if result.get("success") else 500
