from services.empresa_service import EmpresaService

class DashboardService:
    """Service for dashboard data."""
    def __init__(self):
        self.empresa_service = EmpresaService()

    def get_activity(self):
        """Return sample global activity data"""
        data = {
            'labels': ['L', 'M', 'X', 'J', 'V', 'S', 'D'],
            'values': [65, 78, 90, 85, 92, 88, 95],
            'label': 'Actividad'
        }
        return {'success': True, 'data': data}

    def get_empresa_activity(self, empresa_id):
        """Return sample activity data for a specific company"""
        # Placeholder for future logic scoped to empresa_id
        return self.get_activity()

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
