from flask import jsonify, request
from services.mqtt_alert_service import MqttAlertService
from services.hardware_auth_service import HardwareAuthService
from utils.auth_utils import get_auth_header, get_auth_cookie
from models.mqtt_alert import MqttAlert
from datetime import datetime
from bson import ObjectId
from utils.geocoding import generar_url_google_maps, generar_url_openstreetmap

class MqttAlertController:
    """Controlador para gestionar las alertas MQTT"""

    def __init__(self):
        self.service = MqttAlertService()
        self.hardware_auth_service = HardwareAuthService()

    def _extract_tipo_alerta_identifiers(self, raw_tipo_alerta):
        """Extrae identificadores válidos desde el payload recibido."""
        tipo_alerta_id = None
        tipo_alerta_value = None

        if isinstance(raw_tipo_alerta, dict):
            tipo_alerta_id = (
                raw_tipo_alerta.get('_id')
                or raw_tipo_alerta.get('id')
                or raw_tipo_alerta.get('tipo_alerta_id')
            )

            for key in ('tipo_alerta', 'codigo', 'clave', 'slug', 'nombre'):
                value = raw_tipo_alerta.get(key)
                if isinstance(value, str) and value.strip():
                    tipo_alerta_value = value.strip()
                    break

        elif isinstance(raw_tipo_alerta, str):
            trimmed = raw_tipo_alerta.strip()
            if trimmed:
                if ObjectId.is_valid(trimmed):
                    tipo_alerta_id = trimmed
                else:
                    tipo_alerta_value = trimmed

        elif raw_tipo_alerta is not None:
            raw_str = str(raw_tipo_alerta).strip()
            if raw_str:
                if ObjectId.is_valid(raw_str):
                    tipo_alerta_id = raw_str
                else:
                    tipo_alerta_value = raw_str

        return tipo_alerta_id, tipo_alerta_value

    def _resolve_tipo_alerta(self, raw_tipo_alerta):
        """Normaliza y busca la información asociada al tipo de alerta."""
        tipo_alerta_id, tipo_alerta_value = self._extract_tipo_alerta_identifiers(raw_tipo_alerta)
        has_identifier = bool(tipo_alerta_id or (tipo_alerta_value and tipo_alerta_value.strip()))

        normalized_value = tipo_alerta_value.strip().upper() if tipo_alerta_value else None

        from repositories.tipo_alarma_repository import TipoAlarmaRepository

        tipo_alarma_repo = TipoAlarmaRepository()
        tipo_alarma_info = None

        if tipo_alerta_id:
            tipo_alarma_info = tipo_alarma_repo.get_tipo_alarma_by_id(tipo_alerta_id)

        if not tipo_alarma_info and normalized_value:
            tipo_alarma_info = tipo_alarma_repo.find_by_tipo_alerta(normalized_value)

        if not tipo_alarma_info and tipo_alerta_value:
            tipo_alarma_info = tipo_alarma_repo.find_by_tipo_alerta_case_insensitive(tipo_alerta_value)

        if not tipo_alarma_info and tipo_alerta_value:
            tipo_alarma_info = tipo_alarma_repo.find_by_nombre(tipo_alerta_value)

        resolved_value = None
        resolved_id = tipo_alerta_id
        tipo_alarma_payload = None

        if tipo_alarma_info:
            resolved_value = tipo_alarma_info.tipo_alerta
            resolved_id = str(tipo_alarma_info._id) if getattr(tipo_alarma_info, '_id', None) else resolved_id
            tipo_alarma_payload = {
                '_id': resolved_id,
                'nombre': getattr(tipo_alarma_info, 'nombre', None),
                'descripcion': getattr(tipo_alarma_info, 'descripcion', None),
                'tipo_alerta': getattr(tipo_alarma_info, 'tipo_alerta', None),
                'color_alerta': getattr(tipo_alarma_info, 'color_alerta', None),
                'imagen_base64': getattr(tipo_alarma_info, 'imagen_base64', None),
                'implementos_necesarios': getattr(tipo_alarma_info, 'implementos_necesarios', []),
                'recomendaciones': getattr(tipo_alarma_info, 'recomendaciones', [])
            }
        elif normalized_value:
            resolved_value = normalized_value

        return {
            'tipo_alarma_info': tipo_alarma_info,
            'tipo_alerta_resolved': resolved_value,
            'tipo_alerta_id': resolved_id,
            'tipo_alerta_input': tipo_alerta_value,
            'has_identifier': has_identifier,
            'tipo_alarma_payload': tipo_alarma_payload
        }

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
            # print(f"🔍 Buscando alerta con ID: {alert_id}")
            result = self.service.get_alert_by_id(alert_id)
            # print(f"📊 Resultado del servicio: {result}")
            return jsonify(result), 200 if result['success'] else 404
        except Exception as e:
            # print(f"❌ Error en get_alert_by_id: {e}")
            import traceback
            traceback.print_exc()
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
            # Debug: CREATE_ALERT endpoint
            
            # Obtener token y extraer información del hardware
            token = get_auth_cookie(request) or get_auth_header(request)
            print(f"🔑 TOKEN OBTENIDO: {'Sí' if token else 'No'}")
            if not token:
                return jsonify({
                    'success': False,
                    'error': 'Token de autenticación requerido',
                    'message': 'Se requiere token de hardware para crear alertas'
                }), 401
            
            token_result = self.hardware_auth_service.verify_token(token)
            print(f"🔐 TOKEN VERIFICATION RESULT: {token_result}")
            if not token_result['success']:
                return jsonify(token_result), 401
            
            token_payload = token_result['payload']
            hardware_id = token_payload.get('hardware_id')
            print(f"🏗️ HARDWARE_ID FROM TOKEN: {hardware_id}")
            
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
            print(f"📋 JSON DATA RECEIVED: {data}")
            
            # Validación estricta de parámetros
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'Datos requeridos',
                    'message': 'El cuerpo de la petición no puede estar vacío'
                }), 400
            
            alert_data = data.get('data')
            if alert_data is None:
                return jsonify({
                    'success': False,
                    'error': 'Campo data requerido',
                    'message': 'El campo "data" es obligatorio'
                }), 400
            
            if not isinstance(alert_data, dict):
                return jsonify({
                    'success': False,
                    'error': 'Formato de data inválido',
                    'message': 'El campo "data" debe ser un objeto JSON'
                }), 400
            
            # Validar campos obligatorios dentro de data
            raw_tipo_alerta = (
                alert_data.get('tipo_alerta')
                or alert_data.get('tipo_alarma')
                or alert_data.get('tipo_alerta_id')
            )
            print(f"📝 TIPO_ALERTA FOUND: {raw_tipo_alerta}")

            tipo_alerta_details = self._resolve_tipo_alerta(raw_tipo_alerta)

            if not tipo_alerta_details['has_identifier']:
                return jsonify({
                    'success': False,
                    'error': 'Campo tipo_alerta requerido',
                    'message': 'El campo "data.tipo_alerta" o "data.tipo_alarma" es obligatorio'
                }), 400

            resolved_tipo_alerta = tipo_alerta_details['tipo_alerta_resolved']
            if not resolved_tipo_alerta and tipo_alerta_details['tipo_alerta_input']:
                resolved_tipo_alerta = tipo_alerta_details['tipo_alerta_input'].upper()

            if not resolved_tipo_alerta:
                return jsonify({
                    'success': False,
                    'error': 'tipo_alerta inválido',
                    'message': 'No se pudo determinar un tipo de alerta válido a partir del payload recibido'
                }), 400

            # Validar descripción si se proporciona
            descripcion = alert_data.get('descripcion')
            if descripcion is not None and (not isinstance(descripcion, str) or not descripcion.strip()):
                return jsonify({
                    'success': False,
                    'error': 'Descripción inválida',
                    'message': 'El campo "descripcion" debe ser una cadena no vacía si se proporciona'
                }), 400
            
            # Buscar información del tipo de alarma para obtener nombre, imagen, elementos e instrucciones
            tipo_alarma_info = tipo_alerta_details['tipo_alarma_info']
            tipo_alarma_payload = tipo_alerta_details['tipo_alarma_payload']

            # Normalizar y dejar trazabilidad en los datos originales
            alert_data['tipo_alerta'] = resolved_tipo_alerta
            if tipo_alerta_details['tipo_alerta_id']:
                alert_data['tipo_alerta_id'] = tipo_alerta_details['tipo_alerta_id']
            alert_data['tipo_alerta_normalizada'] = resolved_tipo_alerta
            if tipo_alerta_details['tipo_alerta_input']:
                alert_data['tipo_alerta_original'] = tipo_alerta_details['tipo_alerta_input']

            if tipo_alarma_payload:
                alert_data.setdefault('tipo_alarma_detalle', tipo_alarma_payload)
                if tipo_alarma_payload.get('nombre') and not alert_data.get('nombre_alerta'):
                    alert_data['nombre_alerta'] = tipo_alarma_payload['nombre']
                if tipo_alarma_payload.get('imagen_base64') and not alert_data.get('image_alert'):
                    alert_data['image_alert'] = tipo_alarma_payload['imagen_base64']
                if tipo_alarma_payload.get('implementos_necesarios') and not alert_data.get('elementos_necesarios'):
                    alert_data['elementos_necesarios'] = tipo_alarma_payload['implementos_necesarios']
                if tipo_alarma_payload.get('recomendaciones') and not alert_data.get('instrucciones'):
                    alert_data['instrucciones'] = tipo_alarma_payload['recomendaciones']
            
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
                        'nombre': usuario.get('nombre', ''),
                        'usuario_id': str(usuario.get('_id')),
                        'disponible': False,  # Por defecto False para alertas de hardware
                        'embarcado': False    # Por defecto False
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
            
            # Determinar prioridad de la alerta basada en los datos
            prioridad_alerta = self.service._determine_priority(
                resolved_tipo_alerta,
                alert_data
            )
            
            # Preparar información de ubicación
            ubicacion_info = {
                'direccion': hardware.direccion or '',
                'url_maps': hardware.direccion_url or '',
                'url_open_maps': getattr(hardware, 'direccion_open_maps', '') or ''
            }
            
            # Obtener detalles de tipo de alarma
            nombre_alerta_val = alert_data.get('nombre_alerta')
            if not nombre_alerta_val and tipo_alarma_info and getattr(tipo_alarma_info, 'nombre', None):
                nombre_alerta_val = tipo_alarma_info.nombre
            elif not nombre_alerta_val and tipo_alarma_payload:
                nombre_alerta_val = tipo_alarma_payload.get('nombre')

            image_alert = alert_data.get('image_alert')
            if not image_alert and tipo_alarma_info and tipo_alarma_info.imagen_base64:
                image_alert = tipo_alarma_info.imagen_base64
            elif not image_alert and tipo_alarma_payload:
                image_alert = tipo_alarma_payload.get('imagen_base64')

            elementos_necesarios = alert_data.get('elementos_necesarios') or []
            instrucciones = alert_data.get('instrucciones') or []
            if not elementos_necesarios:
                if tipo_alarma_info:
                    elementos_necesarios = getattr(tipo_alarma_info, 'implementos_necesarios', [])
                elif tipo_alarma_payload:
                    elementos_necesarios = tipo_alarma_payload.get('implementos_necesarios', [])
            if not instrucciones:
                if tipo_alarma_info:
                    instrucciones = getattr(tipo_alarma_info, 'recomendaciones', [])
                elif tipo_alarma_payload:
                    instrucciones = tipo_alarma_payload.get('recomendaciones', [])

            if nombre_alerta_val:
                alert_data['nombre_alerta'] = nombre_alerta_val
            if image_alert:
                alert_data['image_alert'] = image_alert
            if elementos_necesarios:
                alert_data['elementos_necesarios'] = elementos_necesarios
            if instrucciones:
                alert_data['instrucciones'] = instrucciones
            
            # Crear alerta con la información del hardware usando el método de fábrica actualizado
            alert = MqttAlert.create_from_hardware(
                empresa_nombre=empresa.nombre,
                sede=hardware.sede,
                hardware_nombre=hardware.nombre,
                hardware_id=hardware_id,
                tipo_alerta=resolved_tipo_alerta,
                nombre_alerta=nombre_alerta_val,
                descripcion=alert_data.get('descripcion', f'Alerta generada por {hardware.nombre}'),
                prioridad=prioridad_alerta,
                image_alert=image_alert,
                elementos_necesarios=elementos_necesarios,
                instrucciones=instrucciones,
                data=alert_data,
                numeros_telefonicos=numeros_telefonicos,
                topic=hardware.topic,
                topics_otros_hardware=topics_otros_hardware,
                ubicacion=ubicacion_info
            )
            
            # Crear en base de datos
            created_alert = self.service.alert_repo.create_alert(alert)
            
            # INVALIDAR TOKEN DESPUÉS DE USO EXITOSO
            self.hardware_auth_service.invalidate_token_after_use(token)
            
            return jsonify({
                'success': True,
                'message': 'Alerta creada exitosamente',
                'alert': created_alert.to_json(),
                'token_status': 'invalidated'  # Indicar que el token ya no es válido
            }), 201
            
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
    
    def get_inactive_alerts(self):
        """Obtener alertas inactivas/desactivadas"""
        try:
            # Obtener parámetros de paginación y filtros
            limit = int(request.args.get('limit', 50))
            offset = int(request.args.get('offset', 0))
            page = (offset // limit) + 1  # Convertir offset a página
            empresa_id = request.args.get('empresaId')  # Filtro por empresa
            
            print(f"🔍 DEBUG get_inactive_alerts:")
            print(f"  - limit: {limit}")
            print(f"  - offset: {offset}")
            print(f"  - page: {page}")
            print(f"  - empresa_id: {empresa_id}")
            
            # Si se proporciona empresa_id, filtrar por empresa
            if empresa_id:
                print(f"  ➡️ Buscando alertas inactivas por empresa ID: {empresa_id}")
                result = self.service.get_inactive_alerts_by_empresa(empresa_id, page, limit)
                print(f"  📊 Resultado del servicio: success={result.get('success')}, total={result.get('total')}, alerts_count={len(result.get('alerts', []))}")
            else:
                print(f"  ➡️ Buscando todas las alertas inactivas")
                result = self.service.get_inactive_alerts(page, limit)
                print(f"  📊 Resultado del servicio: success={result.get('success')}, total={result.get('total')}, alerts_count={len(result.get('alerts', []))}")
            
            # Transformar la respuesta para incluir paginación compatible con offset
            if result['success']:
                # Calcular valores de paginación basados en offset
                total_items = result.get('total', 0)
                total_pages = (total_items + limit - 1) // limit
                current_page = page
                has_next = offset + limit < total_items
                has_prev = offset > 0
                
                # Restructurar respuesta
                response = {
                    'success': True,
                    'data': result.get('alerts', []),
                    'pagination': {
                        'total_pages': total_pages,
                        'current_page': current_page,
                        'total_items': total_items,
                        'has_next': has_next,
                        'has_prev': has_prev
                    }
                }
                return jsonify(response), 200
            else:
                return jsonify(result), 200
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': 'Parámetros de paginación inválidos',
                'message': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': str(e)
            }), 500
    
    def update_alert_user_status(self):
        """
        PATCH /api/mqtt-alerts/update-user-status - Actualizar estado de usuario en alerta
        """
        try:
            if not request.is_json:
                return jsonify({
                    'success': False, 
                    'error': 'Invalid format', 
                    'message': 'Content must be JSON'
                }), 400
            
            data = request.get_json()
            
            # Validar campos requeridos
            alert_id = data.get('alert_id')
            usuario_id = data.get('usuario_id')
            
            if not alert_id:
                return jsonify({
                    'success': False,
                    'error': 'alert_id is required'
                }), 400
            
            if not usuario_id:
                return jsonify({
                    'success': False,
                    'error': 'usuario_id is required'
                }), 400
            
            # Extraer solo los campos de actualización
            update_data = {}
            if 'disponible' in data:
                update_data['disponible'] = data['disponible']
            if 'embarcado' in data:
                update_data['embarcado'] = data['embarcado']
            
            result = self.service.update_alert_user_status(alert_id, usuario_id, update_data)
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 404 if 'not found' in result.get('error', '').lower() else 400

        except Exception as e:
            return jsonify({
                'success': False, 
                'error': 'Internal server error', 
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
    
    def get_active_alerts_by_empresa_sede(self, empresa_id):
        """Obtener alertas activas por empresa y sede con paginación"""
        try:
            # Obtener parámetros de paginación
            limit = int(request.args.get('limit', 5))
            offset = int(request.args.get('offset', 0))
            page = (offset // limit) + 1  # Convertir offset a página
            
            # Llamar al servicio
            result = self.service.get_alerts_active_by_empresa_sede(empresa_id, page, limit)
            
            if result['success']:
                # Transformar la estructura para que coincida exactamente con lo solicitado
                # Incluir campos específicos en formato de ejemplo
                transformed_data = []
                for alert in result['data']:
                    alert_dict = alert if isinstance(alert, dict) else alert
                    
                    # Contar contactos - necesitamos buscar en la data para números telefónicos
                    contactos_count = 0
                    if isinstance(alert_dict.get('data'), dict):
                        numeros = alert_dict['data'].get('numeros_telefonicos', [])
                        contactos_count = len(numeros) if numeros else 2  # Default según ejemplo
                    
                    transformed_alert = {
                        "_id": str(alert_dict.get('_id', '')),
                        "hardware_nombre": alert_dict.get('hardware_nombre', 'Sensor Principal'),
                        "prioridad": alert_dict.get('prioridad', 'media'),
                        "activo": alert_dict.get('estado_activo', True),
                        "empresa_nombre": alert_dict.get('empresa_nombre', 'Nicolas Empresa'),
                        "sede": alert_dict.get('sede', 'Secundaria'),
                        "fecha_creacion": alert_dict.get('fecha_creacion', '2024-07-21T10:30:00Z'),
                        "contactos_count": contactos_count
                    }
                    transformed_data.append(transformed_alert)
                
                response = {
                    "success": True,
                    "data": transformed_data,
                    "pagination": result['pagination']
                }
                
                return jsonify(response), 200
            else:
                return jsonify(result), 400
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': 'Parámetros de paginación inválidos',
                'message': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': str(e)
            }), 500
    
    def create_user_alert(self):
        """Crear alerta de usuario con ID de usuario - SIN AUTENTICACIÓN"""
        try:
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Formato inválido',
                    'message': 'El contenido debe ser JSON'
                }), 400
            
            data = request.get_json()
            
            # Validación estricta del cuerpo de la petición
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'Datos requeridos',
                    'message': 'El cuerpo de la petición no puede estar vacío'
                }), 400
            
            if not isinstance(data, dict):
                return jsonify({
                    'success': False,
                    'error': 'Formato de datos inválido',
                    'message': 'El cuerpo de la petición debe ser un objeto JSON válido'
                }), 400
            
            # Validar estructura de campos requeridos
            creador = data.get('creador')
            ubicacion = data.get('ubicacion')
            raw_tipo_alerta = (
                data.get('tipo_alerta')
                or data.get('tipo_alarma')
                or data.get('tipo_alerta_id')
            )
            descripcion = data.get('descripcion')
            
            # Validación del campo creador
            if creador is None:
                return jsonify({
                    'success': False,
                    'error': 'Campo creador requerido',
                    'message': 'El campo "creador" es obligatorio',
                    'estructura_esperada': {
                        'usuario': {'creador': {'usuario_id': 'string', 'tipo': 'usuario'}, 'ubicacion': {'latitud': 'string', 'longitud': 'string'} },
                        'empresa': {'creador': {'empresa_id': 'string', 'tipo': 'empresa', 'sede': 'string'}}
                    }
                }), 400
            
            if not isinstance(creador, dict):
                return jsonify({
                    'success': False,
                    'error': 'Formato de creador inválido',
                    'message': 'El campo "creador" debe ser un objeto',
                    'estructura_esperada': {
                        'usuario': {'creador': {'usuario_id': 'string', 'tipo': 'usuario'}, 'ubicacion': {'latitud': 'string', 'longitud': 'string'} },
                        'empresa': {'creador': {'empresa_id': 'string', 'tipo': 'empresa', 'sede': 'string'}}
                    }
                }), 400
            
            # Obtener tipo de creador para determinar validaciones
            tipo_creador = creador.get('tipo', 'usuario')  # Por defecto 'usuario'
            
            # Validar que el tipo de creador sea válido
            tipos_creador_validos = ['usuario', 'empresa']
            if tipo_creador not in tipos_creador_validos:
                return jsonify({
                    'success': False,
                    'error': f'Tipo de creador inválido. Tipos válidos: {tipos_creador_validos}'
                }), 400
            
            # Validaciones específicas según el tipo de creador
            if tipo_creador == 'usuario':
                # Para usuarios: validar ubicacion si se proporciona, pero no es obligatoria
                if ubicacion is not None and not isinstance(ubicacion, dict):
                    return jsonify({
                        'success': False,
                        'error': 'Formato de ubicacion inválido',
                        'message': 'El campo "ubicacion" debe ser un objeto si se proporciona',
                        'estructura_esperada': {'latitud': 'string', 'longitud': 'string'}
                    }), 400
                    
                # Validar que usuario_id esté presente
                usuario_id = creador.get('usuario_id')
                if not usuario_id:
                    return jsonify({
                        'success': False,
                        'error': 'El ID de usuario en creador es obligatorio para tipo usuario'
                    }), 400
                    
            elif tipo_creador == 'empresa':
                # Para empresas: validar empresa_id, sede y direccion obligatorios
                empresa_id = creador.get('empresa_id')
                sede_empresa = creador.get('sede')
                direccion_empresa = creador.get('direccion')
                
                if not empresa_id:
                    return jsonify({
                        'success': False,
                        'error': 'El ID de empresa en creador es obligatorio para tipo empresa',
                        'estructura_esperada': {'empresa_id': 'string', 'tipo': 'empresa', 'sede': 'string', 'direccion': 'string'}
                    }), 400
                    
                if not sede_empresa:
                    return jsonify({
                        'success': False,
                        'error': 'La sede es obligatoria cuando el creador es una empresa',
                        'estructura_esperada': {'empresa_id': 'string', 'tipo': 'empresa', 'sede': 'string', 'direccion': 'string'}
                    }), 400
                    
                if not direccion_empresa:
                    return jsonify({
                        'success': False,
                        'error': 'La dirección es obligatoria cuando el creador es una empresa',
                        'estructura_esperada': {'empresa_id': 'string', 'tipo': 'empresa', 'sede': 'string', 'direccion': 'string'}
                    }), 400

            # Resolver información del tipo de alerta
            tipo_alerta_details = self._resolve_tipo_alerta(raw_tipo_alerta)

            if not tipo_alerta_details['has_identifier']:
                return jsonify({
                    'success': False,
                    'error': 'El tipo de alerta es obligatorio'
                }), 400

            resolved_tipo_alerta = tipo_alerta_details['tipo_alerta_resolved']
            if not resolved_tipo_alerta and tipo_alerta_details['tipo_alerta_input']:
                resolved_tipo_alerta = tipo_alerta_details['tipo_alerta_input'].upper()

            if not resolved_tipo_alerta:
                return jsonify({
                    'success': False,
                    'error': 'El tipo de alerta proporcionado no es válido'
                }), 400

            tipo_alarma_info = tipo_alerta_details['tipo_alarma_info']
            tipo_alarma_payload = tipo_alerta_details['tipo_alarma_payload']

            # Validar campos obligatorios básicos
            if not descripcion:
                return jsonify({
                    'success': False,
                    'error': 'La descripción es obligatoria'
                }), 400
            
            # Variables para almacenar información según el tipo de creador
            usuario = None
            empresa = None
            sede = None
            usuario_id = None
            latitud = None
            longitud = None
            
            # Procesar según el tipo de creador
            if tipo_creador == 'usuario':
                # Validar ubicación para usuarios (si se proporciona)
                if ubicacion is not None:
                    latitud = ubicacion.get('latitud')
                    longitud = ubicacion.get('longitud')
                    
                    if not latitud or not longitud:
                        return jsonify({
                            'success': False,
                            'error': 'Si se proporciona ubicación, latitud y longitud son obligatorias',
                            'estructura_esperada': {'latitud': 'string', 'longitud': 'string'}
                        }), 400
                
                # Buscar usuario por ID
                usuario_id = creador.get('usuario_id')
                from repositories.usuario_repository import UsuarioRepository
                usuario_repo = UsuarioRepository()
                usuario = usuario_repo.find_by_id(usuario_id)
                
                if not usuario:
                    return jsonify({
                        'success': False,
                        'error': 'Usuario no encontrado',
                        'message': f'No existe un usuario con el ID {usuario_id}'
                    }), 404
                
                # Obtener empresa del usuario
                from repositories.empresa_repository import EmpresaRepository
                empresa_repo = EmpresaRepository()
                empresa = empresa_repo.find_by_id(usuario.empresa_id)
                
                if not empresa:
                    return jsonify({
                        'success': False,
                        'error': 'Empresa no encontrada para el usuario'
                    }), 404
                
                # Obtener sede del usuario (por defecto usar la sede del usuario o 'Principal')
                sede = getattr(usuario, 'sede', 'Principal')
                
            elif tipo_creador == 'empresa':
                # Para empresas: verificar empresa y usar geocodificación de dirección
                empresa_id_creador = creador.get('empresa_id')
                sede = creador.get('sede')
                direccion_empresa = creador.get('direccion')
                
                # Verificar que la empresa sea legítima
                from repositories.empresa_repository import EmpresaRepository
                empresa_repo = EmpresaRepository()
                empresa = empresa_repo.find_by_id(empresa_id_creador)
                
                if not empresa:
                    return jsonify({
                        'success': False,
                        'error': 'Empresa no encontrada',
                        'message': f'No existe una empresa con el ID {empresa_id_creador}'
                    }), 404
                
                # Geocodificar la dirección proporcionada
                from utils.geocoding import procesar_direccion_para_hardware
                direccion_url_google, direccion_url_openstreetmap, coordenadas_string, direccion_error = procesar_direccion_para_hardware(direccion_empresa)
                
                if direccion_error:
                    return jsonify({
                        'success': False,
                        'error': 'Error procesando dirección',
                        'message': direccion_error
                    }), 400
                
                # Extraer coordenadas del string "lat,lon"
                if coordenadas_string:
                    try:
                        lat_lon = coordenadas_string.split(',')
                        latitud = lat_lon[0].strip()
                        longitud = lat_lon[1].strip()
                    except (IndexError, ValueError):
                        return jsonify({
                            'success': False,
                            'error': 'Error extrayendo coordenadas',
                            'message': f'No se pudieron extraer coordenadas válidas de: {coordenadas_string}'
                        }), 500
                else:
                    return jsonify({
                        'success': False,
                        'error': 'No se obtuvieron coordenadas',
                        'message': 'La geocodificación no devolvió coordenadas válidas'
                    }), 500
                
                # Para empresas, no necesitamos un usuario_id específico, usaremos el ID de la empresa
                usuario_id = empresa_id_creador
            
            # Obtener prioridad (opcional)
            prioridad = data.get('prioridad', 'media')
            
            # Obtener topics de otros hardware (excluir botoneras) para notificaciones
            from repositories.hardware_repository import HardwareRepository
            hardware_repo = HardwareRepository()
            todos_hardware = hardware_repo.find_with_filters({
                'empresa_id': empresa._id,
                'sede': sede,
                'activa': True  # Solo hardware activo
            })
            
            topics = []
            for hw in todos_hardware:
                if hw.topic and hw.tipo.upper() != 'BOTONERA':
                    topics.append(hw.topic)
            
            # Obtener números telefónicos de usuarios de la misma empresa y sede
            usuarios_relacionados = self.service.alert_repo.get_users_by_empresa_sede(
                empresa.nombre, sede
            )
            
            # Extraer números telefónicos
            numeros_telefonicos = []
            for usr in usuarios_relacionados:
                if usr.get('telefono'):
                    # Determinar si este usuario es el creador de la alerta
                    es_creador = str(usr.get('_id')) == usuario_id
                    
                    numeros_telefonicos.append({
                        'numero': usr['telefono'],
                        'nombre': usr.get('nombre', ''),
                        'usuario_id': str(usr.get('_id')),
                        'disponible': es_creador,  # True si es el creador, False para otros
                        'embarcado': False  # Por defecto False para todos
                    })
            
            # Preparar datos adicionales simplificados sin redundancias
            data_adicional = {
                'origen': 'usuario_movil' if tipo_creador == 'usuario' else 'empresa_web',
                'creador_id': usuario_id,
                'creador_tipo': tipo_creador,
                'timestamp_creacion': datetime.utcnow().isoformat(),
                'topics_notificacion': topics,  # Guardar topics para notificaciones
                'tipo_alerta': resolved_tipo_alerta,
                'metadatos': {
                    'tipo_procesamiento': 'manual',
                    'plataforma': 'mobile_app' if tipo_creador == 'usuario' else 'web_app'
                }
            }

            if tipo_alerta_details['tipo_alerta_id']:
                data_adicional['tipo_alerta_id'] = tipo_alerta_details['tipo_alerta_id']
            if tipo_alerta_details['tipo_alerta_input']:
                data_adicional['tipo_alerta_original'] = tipo_alerta_details['tipo_alerta_input']
            if tipo_alarma_payload:
                data_adicional['tipo_alarma_detalle'] = tipo_alarma_payload
                if tipo_alarma_payload.get('imagen_base64') and not data_adicional.get('image_alert'):
                    data_adicional['image_alert'] = tipo_alarma_payload['imagen_base64']
                if tipo_alarma_payload.get('implementos_necesarios') and not data_adicional.get('elementos_necesarios'):
                    data_adicional['elementos_necesarios'] = tipo_alarma_payload['implementos_necesarios']
                if tipo_alarma_payload.get('recomendaciones') and not data_adicional.get('instrucciones'):
                    data_adicional['instrucciones'] = tipo_alarma_payload['recomendaciones']
            
            # Preparar información de ubicación
            ubicacion_info = {}
            if latitud and longitud:
                # Si tenemos coordenadas (de usuario o empresa geocodificada), generar URLs
                ubicacion_info = {
                    'direccion': direccion_empresa if tipo_creador == 'empresa' else '',
                    'url_maps': generar_url_google_maps(latitud, longitud),
                    'url_open_maps': generar_url_openstreetmap(latitud, longitud)
                }
            else:
                # Si no hay coordenadas, ubicación vacía
                ubicacion_info = {
                    'direccion': '',
                    'url_maps': '',
                    'url_open_maps': ''
                }
            
            nombre_alerta_val = data.get('nombre_alerta')
            if not nombre_alerta_val and tipo_alarma_info and getattr(tipo_alarma_info, 'nombre', None):
                nombre_alerta_val = tipo_alarma_info.nombre
            elif not nombre_alerta_val and tipo_alarma_payload:
                nombre_alerta_val = tipo_alarma_payload.get('nombre')

            # Obtener imagen desde tipo_alarma_info si existe
            image_alert = data.get('image_alert')
            if not image_alert and tipo_alarma_info and tipo_alarma_info.imagen_base64:
                image_alert = tipo_alarma_info.imagen_base64
            elif not image_alert and tipo_alarma_payload and tipo_alarma_payload.get('imagen_base64'):
                image_alert = tipo_alarma_payload.get('imagen_base64')

            # Obtener elementos necesarios e instrucciones desde tipo_alarma_info si existe
            elementos_necesarios = data.get('elementos_necesarios') or data_adicional.get('elementos_necesarios') or []
            instrucciones = data.get('instrucciones') or data_adicional.get('instrucciones') or []
            if not elementos_necesarios:
                if tipo_alarma_info:
                    elementos_necesarios = getattr(tipo_alarma_info, 'implementos_necesarios', [])
                elif tipo_alarma_payload:
                    elementos_necesarios = tipo_alarma_payload.get('implementos_necesarios', [])
            if not instrucciones:
                if tipo_alarma_info:
                    instrucciones = getattr(tipo_alarma_info, 'recomendaciones', [])
                elif tipo_alarma_payload:
                    instrucciones = tipo_alarma_payload.get('recomendaciones', [])
            
            # Preparar nombre y usuario_id para la creación de la alerta
            if tipo_creador == 'usuario':
                creador_nombre = usuario.nombre
                creador_id_final = str(usuario._id)
            else:  # tipo_creador == 'empresa'
                creador_nombre = f"Empresa {empresa.nombre}"
                creador_id_final = str(empresa._id)
            
            # Crear alerta usando el método de fábrica para usuarios actualizado
            alert = MqttAlert.create_from_user(
                empresa_nombre=empresa.nombre,
                sede=sede,
                usuario_id=creador_id_final,
                usuario_nombre=creador_nombre,
                tipo_alerta=resolved_tipo_alerta,
                nombre_alerta=nombre_alerta_val,
                descripcion=descripcion,
                prioridad=prioridad,
                image_alert=image_alert,
                elementos_necesarios=elementos_necesarios,
                instrucciones=instrucciones,
                data=data_adicional,
                numeros_telefonicos=numeros_telefonicos,
                topics_otros_hardware=topics,  # Guardar los topics para notificaciones
                ubicacion=ubicacion_info
            )
            
            # Validar alerta
            errors = alert.validate()
            if errors:
                return jsonify({
                    'success': False,
                    'error': 'Datos inválidos',
                    'validation_errors': errors
                }), 400
            
            # Guardar en base de datos
            created_alert = self.service.alert_repo.create_alert(alert)
            
            # Respuesta exitosa unificada
            return jsonify({
                'success': True,
                'message': 'Alerta de usuario creada exitosamente',
                'alert': created_alert.to_json()
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': str(e)
            }), 500

    def deactivate_alert_from_body(self):
        """Desactiva una alerta usando alert_id en el cuerpo, junto con desactivado_por_id y desactivado_por_tipo"""
        try:
            # Validación estricta del formato JSON
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Formato inválido',
                    'message': 'El contenido debe ser JSON válido con Content-Type: application/json'
                }), 400
            
            data = request.get_json()
            
            # Validar que el cuerpo no esté vacío
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'Datos requeridos',
                    'message': 'El cuerpo de la petición no puede estar vacío',
                    'required_fields': ['alert_id', 'desactivado_por_id', 'desactivado_por_tipo']
                }), 400
            
            if not isinstance(data, dict):
                return jsonify({
                    'success': False,
                    'error': 'Formato de datos inválido',
                    'message': 'El cuerpo debe ser un objeto JSON válido',
                    'required_fields': ['alert_id', 'desactivado_por_id', 'desactivado_por_tipo']
                }), 400
            
            # Validación estricta de campos requeridos
            alert_id = data.get('alert_id')
            desactivado_por_id = data.get('desactivado_por_id')
            desactivado_por_tipo = data.get('desactivado_por_tipo')
            mensaje_desactivacion = data.get('mensaje_desactivacion')  # Campo opcional
            
            # Validación de alert_id
            if alert_id is None:
                return jsonify({
                    'success': False,
                    'error': 'Campo alert_id requerido',
                    'message': 'El campo "alert_id" es obligatorio'
                }), 400
            
            if not isinstance(alert_id, str) or not alert_id.strip():
                return jsonify({
                    'success': False,
                    'error': 'alert_id inválido',
                    'message': 'El campo "alert_id" debe ser una cadena no vacía'
                }), 400
            
            # Validación de desactivado_por_id
            if desactivado_por_id is None:
                return jsonify({
                    'success': False,
                    'error': 'Campo desactivado_por_id requerido',
                    'message': 'El campo "desactivado_por_id" es obligatorio'
                }), 400
            
            if not isinstance(desactivado_por_id, str) or not desactivado_por_id.strip():
                return jsonify({
                    'success': False,
                    'error': 'desactivado_por_id inválido',
                    'message': 'El campo "desactivado_por_id" debe ser una cadena no vacía'
                }), 400
            
            # Validación de desactivado_por_tipo
            if desactivado_por_tipo is None:
                return jsonify({
                    'success': False,
                    'error': 'Campo desactivado_por_tipo requerido',
                    'message': 'El campo "desactivado_por_tipo" es obligatorio'
                }), 400
            
            if not isinstance(desactivado_por_tipo, str) or not desactivado_por_tipo.strip():
                return jsonify({
                    'success': False,
                    'error': 'desactivado_por_tipo inválido',
                    'message': 'El campo "desactivado_por_tipo" debe ser una cadena no vacía'
                }), 400
            
            # Limpiar valores (trim)
            alert_id = alert_id.strip()
            desactivado_por_id = desactivado_por_id.strip()
            desactivado_por_tipo = desactivado_por_tipo.strip().lower()
            
            # Validar y limpiar mensaje_desactivacion si se proporciona (campo opcional)
            if mensaje_desactivacion is not None:
                if not isinstance(mensaje_desactivacion, str):
                    return jsonify({
                        'success': False,
                        'error': 'mensaje_desactivacion inválido',
                        'message': 'El campo "mensaje_desactivacion" debe ser una cadena si se proporciona'
                    }), 400
                mensaje_desactivacion = mensaje_desactivacion.strip()
                # Si queda vacío después del trim, convertir a None
                if not mensaje_desactivacion:
                    mensaje_desactivacion = None
            
            # print(f"🧩 Valores limpiados:")
            # print(f"  alert_id: '{alert_id}'")
            # print(f"  desactivado_por_id: '{desactivado_por_id}'")
            # print(f"  desactivado_por_tipo: '{desactivado_por_tipo}'")
            
            if not alert_id:
                # print(f"❌ ERROR: alert_id vacío después del trim")
                return jsonify({
                    'success': False,
                    'error': 'El ID de la alerta es obligatorio'
                }), 400
            
            if not desactivado_por_id:
                # print(f"❌ ERROR: desactivado_por_id vacío después del trim")
                return jsonify({
                    'success': False,
                    'error': 'El ID de quien desactiva es obligatorio'
                }), 400
            
            if not desactivado_por_tipo:
                # print(f"❌ ERROR: desactivado_por_tipo vacío después del trim")
                return jsonify({
                    'success': False,
                    'error': 'El tipo de quien desactiva es obligatorio'
                }), 400
            
            # Validar tipo permitido
            tipos_permitidos = ['usuario', 'hardware', 'administrador', 'super_admin', 'empresa']
            if desactivado_por_tipo not in tipos_permitidos:
                return jsonify({
                    'success': False,
                    'error': f'Tipo no válido. Tipos permitidos: {tipos_permitidos}'
                }), 400
            
            # Validar que quien desactiva existe (opcional: verificar según tipo)
            if desactivado_por_tipo == 'usuario':
                from repositories.usuario_repository import UsuarioRepository
                usuario_repo = UsuarioRepository()
                usuario = usuario_repo.find_by_id(desactivado_por_id)
                if not usuario:
                    return jsonify({
                        'success': False,
                        'error': 'Usuario no encontrado'
                    }), 404
            elif desactivado_por_tipo == 'hardware':
                from repositories.hardware_repository import HardwareRepository
                hardware_repo = HardwareRepository()
                hardware = hardware_repo.find_by_id(desactivado_por_id)
                if not hardware:
                    return jsonify({
                        'success': False,
                        'error': 'Hardware no encontrado'
                    }), 404
            elif desactivado_por_tipo == 'empresa':
                from repositories.empresa_repository import EmpresaRepository
                empresa_repo = EmpresaRepository()
                empresa = empresa_repo.find_by_id(desactivado_por_id)
                if not empresa:
                    return jsonify({
                        'success': False,
                        'error': 'Empresa no encontrada'
                    }), 404
                
                # Verificar que la empresa corresponda a la alerta (necesitamos buscar la alerta primero)
                alert_temp = self.service.alert_repo.get_alert_by_id(alert_id)
                if not alert_temp:
                    return jsonify({
                        'success': False,
                        'error': 'Alerta no encontrada para validación de empresa'
                    }), 404
                
                # Validar que la empresa corresponda a la alerta
                if empresa.nombre != alert_temp.empresa_nombre:
                    return jsonify({
                        'success': False,
                        'error': 'La empresa no está autorizada para desactivar esta alerta',
                        'message': f'Esta alerta pertenece a la empresa "{alert_temp.empresa_nombre}" y no puede ser desactivada por "{empresa.nombre}"'
                    }), 403
            # Para administrador y super_admin podrías agregar más validaciones si es necesario

            # Buscar la alerta
            # print(f"🔍 Buscando alerta con ID: {alert_id}")
            alert = self.service.alert_repo.get_alert_by_id(alert_id)
            if not alert:
                # print(f"❌ ERROR: Alerta no encontrada con ID: {alert_id}")
                return jsonify({
                    'success': False,
                    'error': 'Alerta no encontrada'
                }), 404
            
            # print(f"✅ Alerta encontrada: {alert}")
            # print(f"🔍 Estado actual de la alerta - activo: {alert.activo}")

            # Verificar si la alerta ya fue desactivada
            if not alert.activo:
                # print(f"⚠️ Alerta ya estaba desactivada")
                # Obtener números telefónicos reales de la alerta ya desactivada
                numeros_telefonicos = alert.numeros_telefonicos if hasattr(alert, 'numeros_telefonicos') and alert.numeros_telefonicos else []
                
                # Si no hay números en la alerta, buscar usuarios relacionados (fallback)
                if not numeros_telefonicos:
                    usuarios_relacionados = self.service.alert_repo.get_users_by_empresa_sede(
                        alert.empresa_nombre, alert.sede
                    )
                    
                    for usr in usuarios_relacionados:
                        if usr.get('telefono'):
                            numeros_telefonicos.append({
                                'numero': usr['telefono'],
                                'nombre': usr.get('nombre', ''),
                                'usuario_id': str(usr.get('_id')),
                                'disponible': False,  # Fallback por defecto
                                'embarcado': False    # Fallback por defecto
                            })
                
                return jsonify({
                    'success': True,
                    'message': 'Alerta ya fue desactivada previamente',
                    'already_deactivated': True,
                    'numeros_telefonicos': numeros_telefonicos,
                    'desactivado_por': alert.desactivado_por,
                    'fecha_desactivacion': alert.fecha_desactivacion.isoformat() if alert.fecha_desactivacion else None,
                    'mensaje_desactivacion': alert.mensaje_desactivacion  # Incluir el mensaje de desactivación
                }), 200

            # Obtener números telefónicos reales de la alerta existente
            # En lugar de recrear desde cero, usar los datos que ya existen en la alerta
            numeros_telefonicos = alert.numeros_telefonicos if hasattr(alert, 'numeros_telefonicos') and alert.numeros_telefonicos else []
            
            # Si no hay números en la alerta, buscar usuarios relacionados (fallback)
            if not numeros_telefonicos:
                usuarios_relacionados = self.service.alert_repo.get_users_by_empresa_sede(
                    alert.empresa_nombre, alert.sede
                )
                
                for usr in usuarios_relacionados:
                    if usr.get('telefono'):
                        numeros_telefonicos.append({
                            'numero': usr['telefono'],
                            'nombre': usr.get('nombre', ''),
                            'usuario_id': str(usr.get('_id')),
                            'disponible': False,  # Fallback por defecto
                            'embarcado': False    # Fallback por defecto
                        })

            # Obtener topics de hardware de la empresa y sede (excluyendo botoneras)
            from repositories.hardware_repository import HardwareRepository
            hardware_repo = HardwareRepository()
            todos_hardware = hardware_repo.find_with_filters({
                'activa': True  # Solo hardware activo
            })
            
            topics = []
            for hw in todos_hardware:
                # Filtrar por empresa y sede, y excluir botoneras
                if (hw.topic and 
                    hw.tipo.upper() != 'BOTONERA' and
                    hasattr(hw, 'empresa_id')):
                    
                    # Obtener información de la empresa del hardware
                    from repositories.empresa_repository import EmpresaRepository
                    empresa_repo = EmpresaRepository()
                    hw_empresa = empresa_repo.find_by_id(hw.empresa_id)
                    
                    # Solo incluir si coincide con empresa y sede de la alerta
                    if (hw_empresa and 
                        hw_empresa.nombre == alert.empresa_nombre and 
                        hw.sede == alert.sede):
                        topics.append(hw.topic)

            # Desactivar con información de quien desactiva
            alert.deactivate(desactivado_por_id=desactivado_por_id, desactivado_por_tipo=desactivado_por_tipo, mensaje_desactivacion=mensaje_desactivacion)
            
            # Actualizar en base de datos
            success = self.service.alert_repo.update_alert(alert_id, alert)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Alerta desactivada exitosamente',
                    'topics': topics,  # Topics de hardware de la empresa y sede
                    'numeros_telefonicos': numeros_telefonicos,
                    'desactivado_por': {
                        'id': desactivado_por_id,
                        'tipo': desactivado_por_tipo,
                        'fecha_desactivacion': alert.fecha_desactivacion.isoformat()
                    },
                    'prioridad': alert.prioridad,  # Incluir la prioridad de la alerta
                    'mensaje_desactivacion': alert.mensaje_desactivacion  # Incluir el mensaje de desactivación
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'No se pudo desactivar la alerta'
                }), 500

        except Exception as e:
            # print(f"❌ EXCEPCIÓN en deactivate_alert_from_body: {e}")
            import traceback
            # print(f"🔍 Stack trace completo:")
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': str(e)
            }), 500

    def get_alert_details_for_user(self):
        """Obtener detalles de una alerta si el usuario tiene acceso (SIN AUTENTICACIÓN)"""
        try:
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Formato inválido',
                    'message': 'El contenido debe ser JSON'
                }), 400
            
            data = request.get_json()
            
            # Validar campos requeridos
            alert_id = data.get('alert_id')
            user_id = data.get('user_id')
            
            if not alert_id:
                return jsonify({
                    'success': False,
                    'error': 'alert_id es requerido'
                }), 400
            
            if not user_id:
                return jsonify({
                    'success': False,
                    'error': 'user_id es requerido'
                }), 400
            
            # print(f"🔍 Buscando alerta {alert_id} para usuario {user_id}")
            result = self.service.get_alert_for_user(alert_id, user_id)
            # print(f"📊 Resultado del servicio: {result}")
            
            if result['success']:
                return jsonify(result), 200
            else:
                # Determinar el código de estado según el tipo de error
                if 'not found' in result.get('error', '').lower():
                    return jsonify(result), 404
                elif 'access denied' in result.get('error', '').lower() or 'no autorizado' in result.get('error', '').lower():
                    return jsonify(result), 403
                else:
                    return jsonify(result), 400
                    
        except Exception as e:
            # print(f"❌ Error en get_alert_details_for_user: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False, 
                'error': 'Error interno del servidor',
                'message': str(e)
            }), 500
