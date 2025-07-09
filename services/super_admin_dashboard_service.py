from services.empresa_service import EmpresaService
from services.usuario_service import UsuarioService
from services.activity_service import ActivityService
from services.hardware_service import HardwareService
from repositories.usuario_repository import UsuarioRepository
from repositories.empresa_repository import EmpresaRepository
from repositories.hardware_repository import HardwareRepository
from datetime import datetime, timedelta
import random

class SuperAdminDashboardService:
    """Service para el Super Admin Dashboard"""
    
    def __init__(self):
        self.empresa_service = EmpresaService()
        self.usuario_service = UsuarioService()
        self.activity_service = ActivityService()
        self.hardware_service = HardwareService()
        self.empresa_repository = EmpresaRepository()
        self.usuario_repository = UsuarioRepository()
        self.hardware_repository = HardwareRepository()

    def get_dashboard_stats(self):
        """Obtiene estadísticas generales del dashboard"""
        try:
            # Obtener estadísticas de empresas
            empresas_stats = self.empresa_service.get_empresa_stats()
            
            # Obtener estadísticas de usuarios
            users_stats = self._get_users_stats()
            
            # Obtener estadísticas de hardware
            hardware_stats = self._get_hardware_stats()
            
            # Generar datos de rendimiento (mock)
            performance = random.randint(75, 95)
            avg_performance = random.randint(65, 85)
            
            if empresas_stats['success'] and users_stats['success'] and hardware_stats['success']:
                data = {
                    'total_empresas': empresas_stats['data']['total_general'],
                    'active_empresas': empresas_stats['data']['total_activas'],
                    'total_users': users_stats['data']['total'],
                    'active_users': users_stats['data']['active'],
                    'total_hardware': hardware_stats['data']['total_items'],
                    'available_hardware': hardware_stats['data']['available_items'],
                    'performance': performance,
                    'avg_performance': avg_performance
                }
                return {'success': True, 'data': data}
            
            return {'success': False, 'errors': ['Error al obtener estadísticas generales del sistema']}
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}

    def _get_users_stats(self):
        """Obtiene estadísticas de usuarios"""
        try:
            total_users = self.usuario_repository.count_all()
            active_users = self.usuario_repository.count_active()
            
            return {
                'success': True,
                'data': {
                    'total': total_users,
                    'active': active_users,
                    'inactive': total_users - active_users
                }
            }
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}

    def _get_hardware_stats(self):
        """Obtiene estadísticas de hardware"""
        try:
            hardware_result = self.hardware_service.get_all_hardware_including_inactive()
            
            if hardware_result['success']:
                hardware_list = hardware_result['data']
                total_items = len(hardware_list)
                available_items = len([h for h in hardware_list if h.get('activa', True)])
                
                return {
                    'success': True,
                    'data': {
                        'total_items': total_items,
                        'available_items': available_items,
                        'out_of_stock': total_items - available_items
                    }
                }
            else:
                return {'success': False, 'errors': ['Error al obtener estadísticas de hardware']}
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}

    def get_recent_companies(self, limit=5):
        """Obtiene empresas recientes"""
        try:
            empresas_result = self.empresa_service.get_all_empresas(include_inactive=True)
            
            if empresas_result['success']:
                empresas = empresas_result['data']
                
                # Ordenar por fecha de creación descendente
                empresas_sorted = sorted(empresas, 
                                       key=lambda x: x.get('fecha_creacion', ''), 
                                       reverse=True)
                
                # Tomar solo las más recientes
                recent_empresas = empresas_sorted[:limit]
                
                # Formatear datos para el frontend
                formatted_companies = []
                for empresa in recent_empresas:
                    formatted_companies.append({
                        'id': empresa['_id'],
                        'name': empresa['nombre'],
                        'industry': empresa.get('descripcion', 'Tecnología'),
                        'members_count': random.randint(5, 75),  # Mock data
                        'status': 'active' if empresa.get('activa', True) else 'inactive',
                        'created_at': empresa.get('fecha_creacion', ''),
                        'revenue': random.randint(50000, 2000000),  # Mock data
                        'growth_rate': round(random.uniform(-5.0, 25.0), 1)  # Mock data
                    })
                
                return {'success': True, 'data': formatted_companies}
            else:
                return {'success': False, 'errors': ['Error al obtener empresas recientes']}
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}

    def get_recent_users(self, limit=5):
        """Obtiene usuarios recientes"""
        try:
            # Obtener usuarios de todas las empresas
            empresas_result = self.empresa_service.get_all_empresas(include_inactive=True)
            
            if not empresas_result['success']:
                return {'success': False, 'errors': ['Error al obtener empresas']}
            
            all_users = []
            for empresa in empresas_result['data']:
                users_result = self.usuario_service.get_usuarios_by_empresa_including_inactive(empresa['_id'])
                if users_result['success']:
                    for user in users_result['data']:
                        user['empresa_nombre'] = empresa['nombre']
                        all_users.append(user)
            
            # Ordenar por fecha de creación descendente
            users_sorted = sorted(all_users, 
                                key=lambda x: x.get('fecha_creacion', ''), 
                                reverse=True)
            
            # Tomar solo los más recientes
            recent_users = users_sorted[:limit]
            
            # Formatear datos para el frontend
            formatted_users = []
            for user in recent_users:
                formatted_users.append({
                    'id': user['_id'],
                    'name': user['nombre'],
                    'email': user.get('email', f"{user['nombre'].lower().replace(' ', '.')}@example.com"),
                    'role': user.get('rol', 'user'),
                    'status': 'active' if user.get('activo', True) else 'inactive',
                    'joined_at': user.get('fecha_creacion', ''),
                    'company': user.get('empresa_nombre', 'N/A'),
                    'last_login': (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%Y-%m-%d'),
                    'tasks_completed': random.randint(5, 50)  # Mock data
                })
            
            return {'success': True, 'data': formatted_users}
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}

    def get_activity_chart_data(self, period='30d', limit=8):
        """Obtiene datos para gráfico de actividad"""
        try:
            empresas_result = self.empresa_service.get_all_empresas(include_inactive=False)
            
            if empresas_result['success']:
                empresas = empresas_result['data'][:limit]
                
                labels = [empresa['nombre'] for empresa in empresas]
                data = [random.randint(10, 100) for _ in empresas]
                
                chart_data = {
                    'labels': labels,
                    'datasets': [{
                        'label': 'Actividad Mensual',
                        'data': data,
                        'backgroundColor': [
                            '#8b5cf6', '#f472b6', '#60a5fa', '#34d399', 
                            '#fbbf24', '#ef4444', '#06b6d4', '#84cc16'
                        ],
                        'borderWidth': 2
                    }]
                }
                
                return {'success': True, 'data': chart_data}
            else:
                return {'success': False, 'errors': ['Error al obtener datos de actividad']}
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}

    def get_distribution_chart_data(self):
        """Obtiene datos para gráfico de distribución"""
        try:
            # Generar distribución por industria (mock data)
            industries = {
                'Tecnología': random.randint(15, 25),
                'Servicios': random.randint(10, 20),
                'Manufactura': random.randint(8, 15),
                'Retail': random.randint(5, 12),
                'Salud': random.randint(3, 8),
                'Educación': random.randint(2, 6),
                'Finanzas': random.randint(4, 10)
            }
            
            chart_data = {
                'labels': list(industries.keys()),
                'datasets': [{
                    'data': list(industries.values()),
                    'backgroundColor': [
                        '#8b5cf6', '#f472b6', '#60a5fa', '#34d399', 
                        '#fbbf24', '#ef4444', '#06b6d4'
                    ],
                    'borderWidth': 2,
                    'borderColor': '#ffffff'
                }]
            }
            
            return {'success': True, 'data': chart_data}
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}

    def get_hardware_stats(self):
        """Obtiene estadísticas detalladas de hardware"""
        try:
            hardware_result = self.hardware_service.get_all_hardware_including_inactive()
            
            if hardware_result['success']:
                hardware_list = hardware_result['data']
                
                total_items = len(hardware_list)
                available_items = len([h for h in hardware_list if h.get('activa', True)])
                out_of_stock = total_items - available_items
                
                # Distribución por tipo
                type_distribution = {}
                for hardware in hardware_list:
                    hw_type = hardware.get('tipo', 'Unknown')
                    type_distribution[hw_type] = type_distribution.get(hw_type, 0) + 1
                
                stats = {
                    'total_items': total_items,
                    'available_items': available_items,
                    'out_of_stock': out_of_stock,
                    'discontinued': 0,  # Mock data
                    'total_value': random.randint(500000, 2000000),  # Mock data
                    'avg_price': random.randint(3000, 8000),  # Mock data
                    'type_distribution': type_distribution
                }
                
                return {'success': True, 'data': stats}
            else:
                return {'success': False, 'errors': ['Error al obtener estadísticas de hardware']}
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}

    def get_system_performance(self):
        """Obtiene métricas de rendimiento del sistema"""
        try:
            # Generar datos de rendimiento del sistema (mock)
            performance_data = {
                'uptime_percentage': round(random.uniform(98.5, 99.9), 2),
                'response_time': random.randint(150, 500),  # milliseconds
                'error_rate': round(random.uniform(0.1, 2.0), 2),  # percentage
                'active_sessions': random.randint(200, 800),
                'avg_session_duration': random.randint(15, 45),  # minutes
                'cpu_usage': round(random.uniform(45.0, 85.0), 1),
                'memory_usage': round(random.uniform(60.0, 90.0), 1),
                'disk_usage': round(random.uniform(30.0, 70.0), 1)
            }
            
            return {'success': True, 'data': performance_data}
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
