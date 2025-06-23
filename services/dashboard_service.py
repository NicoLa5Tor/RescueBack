from services.empresa_service import EmpresaService
from services.activity_service import ActivityService

class DashboardService:
    """Service for dashboard data."""
    def __init__(self):
        self.empresa_service = EmpresaService()
        self.activity_service = ActivityService()

    def get_activity(self):
        """Return recent activity logs for all companies."""
        return self.activity_service.get_all()

    def get_empresa_activity(self, empresa_id):
        """Return recent activity logs for a specific company."""
        return self.activity_service.get_by_empresa(empresa_id)

    def get_distribution(self):
        """Return totals of registered companies for distribution chart"""
        result = self.empresa_service.get_empresa_stats()
        if result['success']:
            total = result['data']['total_general']
            distribution = {
                'labels': ['Empresas Registradas'],
                'values': [total]
            }
            return {'success': True, 'data': distribution}
        return result
