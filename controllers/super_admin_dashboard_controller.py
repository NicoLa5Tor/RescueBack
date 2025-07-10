from flask import jsonify, request
from services.super_admin_dashboard_service import SuperAdminDashboardService
from utils.permissions import require_super_admin_token
from utils.response_helpers import success_response, error_response
import logging

logger = logging.getLogger(__name__)

class SuperAdminDashboardController:
    """Controller para el dashboard del Super Admin"""
    
    def __init__(self):
        self.dashboard_service = SuperAdminDashboardService()
    
    @require_super_admin_token
    def get_dashboard_stats(self):
        """GET /api/dashboard/stats - Estadísticas generales del sistema"""
        try:
            result = self.dashboard_service.get_dashboard_stats()
            print(f"los stats son: {result}")
            if result['success']:
                return success_response(result['data'])
            else:
                return error_response(result.get('errors', ['Error al obtener estadísticas']))
        except Exception as e:
            logger.error(f"Error en get_dashboard_stats: {e}")
            return error_response([f"Error interno del servidor: {str(e)}"], 500)
    
    @require_super_admin_token
    def get_recent_companies(self):
        """GET /api/dashboard/recent-companies - Empresas recientes"""
        try:
            limit = request.args.get('limit', 5, type=int)
            result = self.dashboard_service.get_recent_companies(limit)
            if result['success']:
                return success_response(result['data'])
            else:
                return error_response(result.get('errors', ['Error al obtener empresas recientes']))
        except Exception as e:
            logger.error(f"Error en get_recent_companies: {e}")
            return error_response([f"Error interno del servidor: {str(e)}"], 500)
    
    @require_super_admin_token
    def get_recent_users(self):
        """GET /api/dashboard/recent-users - Usuarios recientes"""
        try:
            limit = request.args.get('limit', 5, type=int)
            result = self.dashboard_service.get_recent_users(limit)
            if result['success']:
                return success_response(result['data'])
            else:
                return error_response(result.get('errors', ['Error al obtener usuarios recientes']))
        except Exception as e:
            logger.error(f"Error en get_recent_users: {e}")
            return error_response([f"Error interno del servidor: {str(e)}"], 500)
    
    @require_super_admin_token
    def get_activity_chart(self):
        """GET /api/dashboard/activity-chart - Datos para gráfico de actividad"""
        try:
            period = request.args.get('period', '30d')
            limit = request.args.get('limit', 8, type=int)
            result = self.dashboard_service.get_activity_chart_data(period, limit)
            if result['success']:
                return success_response(result['data'])
            else:
                return error_response(result.get('errors', ['Error al obtener datos de actividad']))
        except Exception as e:
            logger.error(f"Error en get_activity_chart: {e}")
            return error_response([f"Error interno del servidor: {str(e)}"], 500)
    
    @require_super_admin_token
    def get_distribution_chart(self):
        """GET /api/dashboard/distribution-chart - Datos para gráfico de distribución"""
        try:
            result = self.dashboard_service.get_distribution_chart_data()
            if result['success']:
                return success_response(result['data'])
            else:
                return error_response(result.get('errors', ['Error al obtener datos de distribución']))
        except Exception as e:
            logger.error(f"Error en get_distribution_chart: {e}")
            return error_response([f"Error interno del servidor: {str(e)}"], 500)
    
    @require_super_admin_token
    def get_hardware_stats(self):
        """GET /api/dashboard/hardware-stats - Estadísticas de hardware"""
        try:
            result = self.dashboard_service.get_hardware_stats()
            if result['success']:
                return success_response(result['data'])
            else:
                return error_response(result.get('errors', ['Error al obtener estadísticas de hardware']))
        except Exception as e:
            logger.error(f"Error en get_hardware_stats: {e}")
            return error_response([f"Error interno del servidor: {str(e)}"], 500)
    
    @require_super_admin_token
    def get_system_performance(self):
        """GET /api/dashboard/system-performance - Rendimiento del sistema"""
        try:
            result = self.dashboard_service.get_system_performance()
            if result['success']:
                return success_response(result['data'])
            else:
                return error_response(result.get('errors', ['Error al obtener rendimiento del sistema']))
        except Exception as e:
            logger.error(f"Error en get_system_performance: {e}")
            return error_response([f"Error interno del servidor: {str(e)}"], 500)
