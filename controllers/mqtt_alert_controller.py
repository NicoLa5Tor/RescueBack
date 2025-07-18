from flask import jsonify, request
from services.mqtt_alert_service import MqttAlertService
from services.hardware_auth_service import HardwareAuthService
from utils.auth_utils import get_auth_header, get_auth_cookie
from models.mqtt_alert import MqttAlert

class MqttAlertController:
    """Controlador para gestionar las alertas MQTT"""

    def __init__(self):
        self.service = MqttAlertService()
        self.hardware_auth_service = HardwareAuthService()

    def process_mqtt_message(self):
        """Procesar mensaje MQTT recibido con autenticación de hardware"""
        try:
            token = get_auth_cookie(request) or get_auth_header(request)
            if not token:
                return jsonify({
                    'success': False,
                    'error': 'Token de autenticación requerido',
                    'message': 'Se requiere token de autenticación en cookie o header Authorization'
                }), 401
            
            token_result = self.hardware_auth_service.verify_token(token)
            if not token_result['success']:
                return jsonify(token_result), 401
            
            token_payload = token_result['payload']
            
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Formato inválido',
                    'message': 'El contenido debe ser JSON'
                }), 400
            
            data = request.get_json()
            
            # Agregar información de autenticación al mensaje
            data['auth_info'] = {
                'hardware_id': token_payload['hardware_id'],
                'hardware_nombre': token_payload['hardware_nombre'],
                'authenticated': True,
                'token_expires_at': token_payload['expires_at']
            }
            
            # Procesar mensaje
            result = self.service.process_mqtt_message(data)
            
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': f'Ha ocurrido un error inesperado: {str(e)}'
            }), 500

    def get_alerts(self):
        """Obtener todas las alertas"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))
            result = self.service.get_all_alerts(page, limit)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    def get_alert_by_id(self, alert_id):
        """Obtener alerta por ID"""
        try:
            result = self.service.get_alert_by_id(alert_id)
            return jsonify(result), 200 if result['success'] else 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    def verify_empresa_sede(self):
        """Verificar si la empresa y sede existen y obtener usuarios"""
        try:
            empresa_nombre = request.args.get('empresa_nombre')
            sede = request.args.get('sede')
            result = self.service.verify_empresa_sede(empresa_nombre, sede)
            return jsonify(result), 200 if result['success'] else 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def test_complete_flow(self):
        """Endpoint de prueba para demostrar el flujo completo - SIN DATOS HARDCODEADOS"""
        try:
            return jsonify({
                'success': True,
                'message': 'Endpoint de prueba disponible',
                'note': 'Este endpoint NO procesa datos hardcodeados. Use POST /api/mqtt-alerts con datos reales.',
                'usage': {
                    'endpoint': 'POST /api/mqtt-alerts',
                    'authentication': 'Requiere token de hardware válido',
                    'data_format': 'JSON con estructura de datos MQTT real'
                },
                'verification_logic': {
                    'step_1': 'Verificar hardware_nombre como filtro inicial',
                    'step_2': 'Si hardware no existe: autorizado=false, estado_activo=false',
                    'step_3': 'Si hardware existe: verificar empresa y sede',
                    'step_4': 'Todo correcto: autorizado=false (pendiente), estado_activo=true',
                    'step_5': 'Hardware existe pero empresa/sede no: autorizado=false, estado_activo=false'
                },
                'data_field_info': {
                    'description': 'El campo data contiene metadatos y verificación',
                    'includes': [
                        'ruta_origen: ruta del topic MQTT',
                        'protocolo: tipo de protocolo (MQTT)',
                        'broker: dirección del broker MQTT',
                        'topic_completo: topic completo del mensaje',
                        'timestamp_procesamiento: cuándo se procesó',
                        'cliente_origen: servicio que procesó el mensaje',
                        'verificacion.hardware_exists: si el hardware existe',
                        'verificacion.empresa_exists: si la empresa existe',
                        'verificacion.sede_exists: si la sede existe',
                        'metadatos.nivel_prioridad: prioridad calculada automáticamente'
                    ]
                }
            }), 200
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def verify_hardware(self):
        """Verificar si el hardware existe y obtener información completa"""
        try:
            hardware_nombre = request.args.get('hardware_nombre')
            if not hardware_nombre:
                return jsonify({
                    'success': False,
                    'error': 'Parámetro hardware_nombre es requerido'
                }), 400
            
            # Usar el repositorio para verificación completa
            verification_info = self.service.alert_repo.get_full_verification_info(hardware_nombre)
            
            return jsonify({
                'success': True,
                'hardware_nombre': hardware_nombre,
                'verification_info': verification_info
            }), 200
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def create_alert(self):
        """Crear una nueva alerta (Solo necesita data - hardware_id desde token)"""
        try:
            # Obtener token y extraer información del hardware
            token = get_auth_cookie(request) or get_auth_header(request)
            if not token:
                return jsonify({
                    'success': False,
                    'error': 'Token de autenticación requerido',
                    'message': 'Se requiere token de hardware para crear alertas'
                }), 401
            
            token_result = self.hardware_auth_service.verify_token(token)
            if not token_result['success']:
                return jsonify(token_result), 401
            
            token_payload = token_result['payload']
            hardware_id = token_payload.get('hardware_id')
            
            if not hardware_id:
                return jsonify({
                    'success': False,
                    'error': 'Token inválido',
                    'message': 'El token no contiene información válida del hardware'
                }), 401
            
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Formato inválido',
                    'message': 'El contenido debe ser JSON'
                }), 400
            
            data = request.get_json()
            alert_data = data.get('data', {})
            
            # Buscar información del tipo de alarma si viene en los datos
            tipo_alarma_info = None
            if 'tipo_alarma' in alert_data:
                from repositories.tipo_alarma_repository import TipoAlarmaRepository
                tipo_alarma_repo = TipoAlarmaRepository()
                tipo_alarma_info = tipo_alarma_repo.find_by_tipo_alerta(alert_data['tipo_alarma'])
                
                # Agregar información del tipo de alarma a los datos
                if tipo_alarma_info:
                    alert_data['tipo_alarma_info'] = {
                        'id': str(tipo_alarma_info._id),
                        'nombre': tipo_alarma_info.nombre,
                        'descripcion': tipo_alarma_info.descripcion,
                        'tipo_alerta': tipo_alarma_info.tipo_alerta,
                        'color_alerta': tipo_alarma_info.color_alerta,
                        'recomendaciones': tipo_alarma_info.recomendaciones,
                        'implementos_necesarios': tipo_alarma_info.implementos_necesarios,
                        'imagen_base64': tipo_alarma_info.imagen_base64
                    }
            
            # Buscar el hardware en la base de datos para obtener toda la información
            from repositories.hardware_repository import HardwareRepository
            hardware_repo = HardwareRepository()
            hardware = hardware_repo.find_by_id(hardware_id)
            
            if not hardware:
                return jsonify({
                    'success': False,
                    'error': 'Hardware no encontrado',
                    'message': 'El hardware del token no existe en la base de datos'
                }), 404
            
            # Obtener empresa desde el hardware
            from repositories.empresa_repository import EmpresaRepository
            empresa_repo = EmpresaRepository()
            empresa = empresa_repo.find_by_id(hardware.empresa_id)
            
            if not empresa:
                return jsonify({
                    'success': False,
                    'error': 'Empresa no encontrada para el hardware'
                }), 404
            
            # Buscar automáticamente los números telefónicos de usuarios de esa empresa y sede
            usuarios_relacionados = self.service.alert_repo.get_users_by_empresa_sede(
                empresa.nombre, hardware.sede
            )
            
            # Extraer números telefónicos con nombres
            numeros_telefonicos = []
            for usuario in usuarios_relacionados:
                if usuario.get('telefono'):
                    numeros_telefonicos.append({
                        'numero': usuario['telefono'],
                        'nombre': usuario.get('nombre', '')
                    })
            
            # Buscar otros hardware de la misma empresa y sede que NO sean botoneras
            otros_hardware = hardware_repo.find_with_filters({
                'empresa_id': hardware.empresa_id,
                'sede': hardware.sede
            })
            
            # Filtrar para excluir botoneras y obtener topics
            topics_otros_hardware = []
            for hw in otros_hardware:
                # Excluir el hardware actual y las botoneras
                if hw._id != hardware._id and hw.tipo.upper() != 'BOTONERA':
                    if hw.topic:
                        topics_otros_hardware.append(hw.topic)
            
            # Crear alerta con la información del hardware
            alert = MqttAlert(
                empresa_nombre=empresa.nombre,
                sede=hardware.sede,
                hardware_nombre=hardware.nombre,
                hardware_id=hardware_id,
                data=alert_data,
                numeros_telefonicos=numeros_telefonicos,
                topic=hardware.topic,
                topics_otros_hardware=topics_otros_hardware
            )
            
            # Crear en base de datos
            created_alert = self.service.alert_repo.create_alert(alert)
            
            # INVALIDAR TOKEN DESPUÉS DE USO EXITOSO
            self.hardware_auth_service.invalidate_token_after_use(token)
            
            response_data = {
                'success': True,
                'message': 'Alerta creada exitosamente',
                'alert_id': str(created_alert._id),
                'numeros_telefonicos': numeros_telefonicos,
                'topic': hardware.topic,
                'topics_otros_hardware': topics_otros_hardware,
                'activo': created_alert.activo,
                'fecha_creacion': created_alert.fecha_creacion.isoformat(),
                'fecha_desactivacion': None,
                'token_status': 'invalidated'  # Indicar que el token ya no es válido
            }
            
            # Agregar información del tipo de alarma si se encontró
            if tipo_alarma_info:
                response_data['tipo_alarma_info'] = {
                    'id': str(tipo_alarma_info._id),
                    'nombre': tipo_alarma_info.nombre,
                    'descripcion': tipo_alarma_info.descripcion,
                    'tipo_alerta': tipo_alarma_info.tipo_alerta,
                    'color_alerta': tipo_alarma_info.color_alerta,
                    'recomendaciones': tipo_alarma_info.recomendaciones,
                    'implementos_necesarios': tipo_alarma_info.implementos_necesarios,
                    'imagen_base64': tipo_alarma_info.imagen_base64
                }
            
            return jsonify(response_data), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': str(e)
            }), 500
    
    def update_alert(self, alert_id):
        """Actualizar una alerta existente"""
        try:
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Formato inválido',
                    'message': 'El contenido debe ser JSON'
                }), 400
            
            data = request.get_json()
            
            # Obtener alerta existente
            existing_alert = self.service.alert_repo.get_alert_by_id(alert_id)
            if not existing_alert:
                return jsonify({
                    'success': False,
                    'error': 'Alerta no encontrada'
                }), 404
            
            # Actualizar campos
            if 'empresa_nombre' in data:
                existing_alert.empresa_nombre = data['empresa_nombre']
            if 'sede' in data:
                existing_alert.sede = data['sede']
            if 'hardware_nombre' in data:
                existing_alert.hardware_nombre = data['hardware_nombre']
            if 'data' in data:
                existing_alert.data = data['data']
            if 'numeros_telefonicos' in data:
                existing_alert.numeros_telefonicos = data['numeros_telefonicos']
            if 'topic' in data:
                existing_alert.topic = data['topic']
            if 'topics_otros_hardware' in data:
                existing_alert.topics_otros_hardware = data['topics_otros_hardware']
            if 'activo' in data:
                existing_alert.activo = data['activo']
            
            # Validar datos actualizados
            errors = existing_alert.validate()
            if errors:
                return jsonify({
                    'success': False,
                    'error': 'Datos inválidos',
                    'validation_errors': errors
                }), 400
            
            # Actualizar en base de datos
            success = self.service.alert_repo.update_alert(alert_id, existing_alert)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Alerta actualizada exitosamente',
                    'alert': existing_alert.to_json()
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'No se pudo actualizar la alerta'
                }), 500
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': str(e)
            }), 500
    
    def delete_alert(self, alert_id):
        """Eliminar una alerta"""
        try:
            # Verificar que la alerta existe
            existing_alert = self.service.alert_repo.get_alert_by_id(alert_id)
            if not existing_alert:
                return jsonify({
                    'success': False,
                    'error': 'Alerta no encontrada'
                }), 404
            
            # Eliminar alerta
            success = self.service.alert_repo.delete_alert(alert_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Alerta eliminada exitosamente'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'No se pudo eliminar la alerta'
                }), 500
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': str(e)
            }), 500
    
    def authorize_alert(self, alert_id):
        """Autorizar una alerta"""
        try:
            data = request.get_json() if request.is_json else {}
            usuario_id = data.get('usuario_id')
            
            result = self.service.authorize_alert(alert_id, usuario_id)
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 404
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': str(e)
            }), 500
    
    def toggle_alert_status(self, alert_id):
        """Alternar estado activo/inactivo de una alerta"""
        try:
            result = self.service.toggle_alert_status(alert_id)
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 404
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': str(e)
            }), 500
    
    def get_alerts_by_empresa(self, empresa_id):
        """Obtener alertas por empresa"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))
            
            # Buscar nombre de empresa por ID
            # TODO: Implementar búsqueda por ID si es necesario
            # Por ahora usar el empresa_id como nombre directamente
            
            result = self.service.get_alerts_by_empresa(empresa_id, page, limit)
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': str(e)
            }), 500
    
    def get_active_alerts(self):
        """Obtener alertas activas"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))
            result = self.service.get_active_alerts(page, limit)
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': str(e)
            }), 500
    
    def get_unauthorized_alerts(self):
        """Obtener alertas no autorizadas"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))
            result = self.service.get_unauthorized_alerts(page, limit)
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': str(e)
            }), 500
    
    def get_alerts_stats(self):
        """Obtener estadísticas de alertas"""
        try:
            result = self.service.get_alerts_stats()
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': str(e)
            }), 500

