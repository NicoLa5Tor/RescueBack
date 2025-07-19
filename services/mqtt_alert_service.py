from repositories.mqtt_alert_repository import MqttAlertRepository
from repositories.usuario_repository import UsuarioRepository
from models.mqtt_alert import MqttAlert
from datetime import datetime
import json

class MqttAlertService:
    """Servicio para manejar alertas MQTT"""
    
    def __init__(self):
        self.alert_repo = MqttAlertRepository()
        self.usuario_repo = UsuarioRepository()
    
    def process_mqtt_message(self, mqtt_data):
        """Procesa un mensaje MQTT y crea alertas"""
        try:
            results = []
            
            # Verificar si es un mensaje con múltiples empresas
            if isinstance(mqtt_data, dict):
                for empresa_nombre, empresa_data in mqtt_data.items():
                    if isinstance(empresa_data, dict):
                        for tipo_alerta, datos_hardware in empresa_data.items():
                            result = self._create_alert_from_mqtt(
                                empresa_nombre, 
                                tipo_alerta, 
                                datos_hardware,
                                mqtt_data
                            )
                            results.append(result)
            
            return results
        except Exception as e:
            print(f"Error procesando mensaje MQTT: {e}")
            return [{
                'success': False,
                'error': str(e),
                'message': 'Error procesando mensaje MQTT'
            }]
    
    def _create_alert_from_mqtt(self, empresa_nombre, tipo_alerta, datos_hardware, mensaje_original):
        """Crea una alerta desde datos MQTT"""
        try:
            # Extraer información del hardware
            sede = datos_hardware.get('sede', 'sede_desconocida')
            hardware_nombre = datos_hardware.get('nombre') or datos_hardware.get('hardware_id') or datos_hardware.get('id')
            
            # FILTRO INICIAL: Verificar hardware como primera validación
            if not hardware_nombre:
                return {
                    'success': False,
                    'error': 'Nombre del hardware es requerido',
                    'empresa': empresa_nombre,
                    'sede': sede
                }
            
            # Verificación completa: hardware, empresa, sede y usuarios
            verification_info = self.alert_repo.get_full_verification_info(hardware_nombre)
            
            # Determinar estados según verificación
            if not verification_info['hardware_exists']:
                # Hardware no existe: autorizado=false, estado_activo=false
                autorizado = False
                estado_activo = False
                usuarios = []
                
                # Aún extraer empresa y sede del mensaje para guardar
                empresa_nombre_final = empresa_nombre
                sede_final = sede
                
            else:
                # Hardware existe: verificar empresa y sede
                hardware_data = verification_info['hardware_data']
                empresa_data = verification_info.get('empresa_data', {})
                
                # Usar datos del hardware si están disponibles
                empresa_nombre_final = empresa_data.get('nombre', empresa_nombre)
                sede_final = hardware_data.get('sede', sede)
                
                # Estados según verificación
                if verification_info['empresa_exists'] and verification_info['sede_exists']:
                    # Todo correcto: autorizado=false (pendiente), estado_activo=true
                    autorizado = False
                    estado_activo = True
                    usuarios = verification_info['usuarios']
                else:
                    # Hardware existe pero empresa/sede no: autorizado=false, estado_activo=false
                    autorizado = False
                    estado_activo = False
                    usuarios = []
            
            # Obtener usuarios para notificación
            
            # Preparar lista de usuarios notificados
            usuarios_notificados = []
            for usuario in usuarios:
                usuario_info = {
                    'nombre': usuario.get('nombre'),
                    'telefono': usuario.get('telefono'),
                    'email': usuario.get('email'),
                    'rol': usuario.get('rol'),
                    'especialidades': usuario.get('especialidades', [])
                }
                usuarios_notificados.append(usuario_info)
            
            # Preparar datos adicionales (ruta, origen, etc.)
            data_adicional = {
                'ruta_origen': 'mqtt://empresas',  # ruta del topic MQTT
                'protocolo': 'MQTT',
                'broker': '161.35.239.177:17090',
                'topic_completo': f'empresas/{empresa_nombre_final}',
                'timestamp_procesamiento': datetime.utcnow().isoformat(),
                'cliente_origen': 'MqttConnection-Service',
                'verificacion': {
                    'hardware_exists': verification_info['hardware_exists'],
                    'empresa_exists': verification_info.get('empresa_exists', False),
                    'sede_exists': verification_info.get('sede_exists', False)
                },
                'metadatos': {
                    'tamano_mensaje': len(str(mensaje_original)),
                    'tipo_procesamiento': 'automatico',
                    'nivel_prioridad': self._determine_priority(tipo_alerta, datos_hardware)
                }
            }
            
            # Obtener hardware_id si está disponible en auth_info
            hardware_id = None
            if isinstance(mensaje_original, dict) and 'auth_info' in mensaje_original:
                hardware_id = mensaje_original['auth_info'].get('hardware_id')
            
            # Agregar información adicional a los datos
            data_adicional['datos_hardware'] = datos_hardware
            data_adicional['mensaje_original'] = mensaje_original
            data_adicional['usuarios_notificados'] = usuarios_notificados
            data_adicional['autorizado'] = autorizado
            data_adicional['estado_activo'] = estado_activo
            
            # Determinar prioridad de la alerta
            prioridad_alerta = self._determine_priority(tipo_alerta, datos_hardware)
            
            # Crear la alerta usando el método de fábrica
            alert = MqttAlert.create_from_hardware(
                empresa_nombre=empresa_nombre_final,
                sede=sede_final,
                hardware_nombre=hardware_nombre,
                hardware_id=hardware_id,
                tipo_alerta=tipo_alerta,
                data=data_adicional,
                prioridad=prioridad_alerta
            )
            # Validar datos
            errors = alert.validate()
            if errors:
                return {
                    'success': False,
                    'error': 'Datos inválidos',
                    'validation_errors': errors
                }
            
            # Guardar en base de datos
            created_alert = self.alert_repo.create_alert(alert)
            
            return {
                'success': True,
                'alert_id': str(created_alert._id),
                'empresa': empresa_nombre_final,
                'sede': sede_final,
                'tipo_alerta': tipo_alerta,
                'hardware_nombre': hardware_nombre,
                'hardware_exists': verification_info['hardware_exists'],
                'empresa_exists': verification_info.get('empresa_exists', False),
                'sede_exists': verification_info.get('sede_exists', False),
                'autorizado': autorizado,
                'estado_activo': estado_activo,
                'usuarios_notificados': usuarios_notificados,
                'message': 'Alerta creada exitosamente'
            }
            
        except Exception as e:
            print(f"Error creando alerta desde MQTT: {e}")
            return {
                'success': False,
                'error': str(e),
                'empresa': empresa_nombre,
                'sede': sede if 'sede' in locals() else 'desconocida'
            }
    
    def get_all_alerts(self, page=1, limit=50):
        """Obtiene todas las alertas"""
        try:
            alerts, total = self.alert_repo.get_all_alerts(page, limit)
            return {
                'success': True,
                'alerts': [alert.to_json() for alert in alerts],
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit
            }
        except Exception as e:
            print(f"Error obteniendo alertas: {e}")
            return {
                'success': False,
                'error': str(e),
                'alerts': [],
                'total': 0
            }
    
    def get_alert_by_id(self, alert_id):
        """Obtiene una alerta por ID"""
        try:
            alert = self.alert_repo.get_alert_by_id(alert_id)
            if alert:
                return {
                    'success': True,
                    'alert': alert.to_json()
                }
            else:
                return {
                    'success': False,
                    'error': 'Alerta no encontrada'
                }
        except Exception as e:
            print(f"Error obteniendo alerta por ID: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_alerts_by_empresa(self, empresa_nombre, page=1, limit=50):
        """Obtiene alertas por empresa"""
        try:
            alerts, total = self.alert_repo.get_alerts_by_empresa(empresa_nombre, page, limit)
            return {
                'success': True,
                'alerts': [alert.to_json() for alert in alerts],
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit
            }
        except Exception as e:
            print(f"Error obteniendo alertas por empresa: {e}")
            return {
                'success': False,
                'error': str(e),
                'alerts': [],
                'total': 0
            }
    
    def get_active_alerts(self, page=1, limit=50):
        """Obtiene alertas activas"""
        try:
            alerts, total = self.alert_repo.get_active_alerts(page, limit)
            return {
                'success': True,
                'alerts': [alert.to_json() for alert in alerts],
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit
            }
        except Exception as e:
            print(f"Error obteniendo alertas activas: {e}")
            return {
                'success': False,
                'error': str(e),
                'alerts': [],
                'total': 0
            }
    
    def get_unauthorized_alerts(self, page=1, limit=50):
        """Obtiene alertas no autorizadas"""
        try:
            alerts, total = self.alert_repo.get_unauthorized_alerts(page, limit)
            return {
                'success': True,
                'alerts': [alert.to_json() for alert in alerts],
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit
            }
        except Exception as e:
            print(f"Error obteniendo alertas no autorizadas: {e}")
            return {
                'success': False,
                'error': str(e),
                'alerts': [],
                'total': 0
            }
    
    def authorize_alert(self, alert_id, usuario_id):
        """Autoriza una alerta"""
        try:
            success = self.alert_repo.authorize_alert(alert_id, usuario_id)
            if success:
                return {
                    'success': True,
                    'message': 'Alerta autorizada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo autorizar la alerta'
                }
        except Exception as e:
            print(f"Error autorizando alerta: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def toggle_alert_status(self, alert_id):
        """Alterna el estado de una alerta"""
        try:
            success = self.alert_repo.toggle_alert_status(alert_id)
            if success:
                return {
                    'success': True,
                    'message': 'Estado de alerta actualizado exitosamente'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo actualizar el estado de la alerta'
                }
        except Exception as e:
            print(f"Error cambiando estado de alerta: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_alert(self, alert_id):
        """Elimina una alerta"""
        try:
            success = self.alert_repo.delete_alert(alert_id)
            if success:
                return {
                    'success': True,
                    'message': 'Alerta eliminada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo eliminar la alerta'
                }
        except Exception as e:
            print(f"Error eliminando alerta: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_alerts_stats(self):
        """Obtiene estadísticas de alertas"""
        try:
            stats = self.alert_repo.get_alerts_stats()
            return {
                'success': True,
                'stats': stats
            }
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': {}
            }
    
    def verify_empresa_sede(self, empresa_nombre, sede):
        """Verifica si existe una empresa con la sede especificada"""
        try:
            exists, message = self.alert_repo.verify_empresa_sede_exists(empresa_nombre, sede)
            usuarios = []
            
            if exists:
                usuarios = self.alert_repo.get_users_by_empresa_sede(empresa_nombre, sede)
            
            return {
                'success': exists,
                'message': message,
                'empresa': empresa_nombre,
                'sede': sede,
                'usuarios': usuarios
            }
        except Exception as e:
            print(f"Error verificando empresa y sede: {e}")
            return {
                'success': False,
                'error': str(e),
                'empresa': empresa_nombre,
                'sede': sede,
                'usuarios': []
            }
    
    def _determine_priority(self, tipo_alerta, datos_hardware):
        """Determina la prioridad de la alerta basada en el tipo y datos"""
        try:
            # Prioridades por tipo de alerta
            priority_map = {
                'semaforo': 'media',
                'alarma': 'alta',
                'emergencia': 'critica',
                'mantenimiento': 'baja'
            }
            
            base_priority = priority_map.get(tipo_alerta.lower(), 'media')
            
            # Ajustar prioridad según datos del hardware
            if isinstance(datos_hardware, dict):
                alerta_value = datos_hardware.get('alerta', '').lower()
                
                # Prioridades específicas por tipo de alerta
                if 'critica' in alerta_value or 'roja' in alerta_value:
                    return 'critica'
                elif 'amarilla' in alerta_value or 'precaucion' in alerta_value:
                    return 'media'
                elif 'verde' in alerta_value or 'normal' in alerta_value:
                    return 'baja'
                elif 'naranja' in alerta_value:
                    return 'alta'
            
            return base_priority
            
        except Exception as e:
            print(f"Error determinando prioridad: {e}")
            return 'media'  # prioridad por defecto
