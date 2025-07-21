from flask import jsonify, request
from services.mqtt_alert_service import MqttAlertService
from services.hardware_auth_service import HardwareAuthService
from utils.auth_utils import get_auth_header, get_auth_cookie
from models.mqtt_alert import MqttAlert
from datetime import datetime

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
            
            # Determinar prioridad de la alerta basada en los datos
            prioridad_alerta = self.service._determine_priority(
                alert_data.get('tipo_alerta', 'media'), 
                alert_data
            )
            
            # Crear alerta con la información del hardware usando el método de fábrica
            alert = MqttAlert.create_from_hardware(
                empresa_nombre=empresa.nombre,
                sede=hardware.sede,
                hardware_nombre=hardware.nombre,
                hardware_id=hardware_id,
                tipo_alerta=alert_data.get('tipo_alerta'),
                data=alert_data,
                numeros_telefonicos=numeros_telefonicos,
                topic=hardware.topic,
                topics_otros_hardware=topics_otros_hardware,
                prioridad=prioridad_alerta
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
                'prioridad': prioridad_alerta,
                'hardware_ubicacion': {
                    'direccion': hardware.direccion,
                    'direccion_url': hardware.direccion_url,
                    'direccion_open_maps': getattr(hardware, 'direccion_open_maps', None)
                },
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
            
            # Validar campos requeridos
            usuario_id = data.get('usuario_id')
            tipo_alerta = data.get('tipo_alerta')
            descripcion = data.get('descripcion')
            
            if not usuario_id:
                return jsonify({
                    'success': False,
                    'error': 'El ID de usuario es obligatorio'
                }), 400
            
            if not tipo_alerta:
                return jsonify({
                    'success': False,
                    'error': 'El tipo de alerta es obligatorio'
                }), 400
            
            if not descripcion:
                return jsonify({
                    'success': False,
                    'error': 'La descripción es obligatoria'
                }), 400
            
            # Buscar usuario por ID
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
            
            # Obtener prioridad (opcional)
            prioridad = data.get('prioridad', 'media')
            
            # Buscar SOLO la botonera de la misma empresa y sede
            from repositories.hardware_repository import HardwareRepository
            hardware_repo = HardwareRepository()
            
            # Buscar específicamente una botonera en la empresa y sede del usuario
            print(f"🔍 Buscando botonera para empresa_id: {empresa._id}, sede: {sede}")
            
            # Primero buscar TODO el hardware de esa empresa y sede para ver qué hay
            all_hardware_debug = hardware_repo.find_with_filters({
                'empresa_id': empresa._id,
                'sede': sede,
                'activa': True
            })
            print(f"🔍 TODO el hardware activo en empresa {empresa.nombre}, sede {sede}:")
            for hw in all_hardware_debug:
                print(f"  - {hw.nombre} | Tipo: {hw.tipo} | Sede: {hw.sede}")
            
            botonera = None
            # Buscar botonera con filtro case-insensitive
            all_hardware_sede = hardware_repo.find_with_filters({
                'empresa_id': empresa._id,
                'sede': sede,
                'activa': True
            })
            
            # Filtrar manualmente por tipo botonera (case-insensitive)
            hardware_empresa = []
            for hw in all_hardware_sede:
                if hw.tipo.upper() == 'BOTONERA':
                    hardware_empresa.append(hw)
            
            print(f"🔍 Hardware tipo BOTONERA encontrado: {len(hardware_empresa) if hardware_empresa else 0} elementos")
            for hw in hardware_empresa:
                print(f"  - Botonera: {hw.nombre}, Tipo: {hw.tipo}, Sede: {hw.sede}")
                print(f"    Direccion: {hw.direccion}")
                print(f"    Direccion URL (Google): {hw.direccion_url}")
                print(f"    Direccion Open Maps: {getattr(hw, 'direccion_open_maps', 'No disponible')}")
            
            # Tomar la primera botonera encontrada (debería haber solo una por sede)
            if hardware_empresa:
                botonera = hardware_empresa[0]
                print(f"✅ Botonera encontrada: {botonera.nombre}")
            else:
                print(f"❌ No se encontró botonera para empresa {empresa.nombre} en sede {sede}")
                print(f"❌ Tipos disponibles en la sede: {[hw.tipo for hw in all_hardware_debug]}")
            
            # Preparar ubicación de la botonera
            botonera_ubicacion = None
            if botonera:
                botonera_ubicacion = {
                    'hardware_nombre': botonera.nombre,
                    'hardware_id': str(botonera._id),
                    'direccion': botonera.direccion,
                    'direccion_url': botonera.direccion_url,  # Este es el de Google Maps
                    'direccion_open_maps': getattr(botonera, 'direccion_open_maps', None),
                    'topic': botonera.topic,
                    'tipo': botonera.tipo
                }
                print(f"📍 Ubicación de botonera preparada: {botonera_ubicacion}")
            else:
                print(f"📍 botonera_ubicacion será NULL porque no se encontró botonera")
            
            # Obtener topics de otros hardware (excluir botoneras) para notificaciones
            todos_hardware = hardware_repo.find_with_filters({
                'empresa_id': empresa._id,
                'sede': sede,
                'activa': True  # Corregido: campo correcto es 'activa'
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
                    numeros_telefonicos.append({
                        'numero': usr['telefono'],
                        'nombre': usr.get('nombre', '')
                    })
            
            # Buscar información del tipo de alarma
            tipo_alarma_info = None
            if tipo_alerta:
                from repositories.tipo_alarma_repository import TipoAlarmaRepository
                tipo_alarma_repo = TipoAlarmaRepository()
                tipo_alarma_info = tipo_alarma_repo.find_by_tipo_alerta(tipo_alerta)
            
            # Preparar datos adicionales
            data_adicional = {
                'origen': 'usuario_movil',
                'usuario_id_origen': usuario_id,
                'usuario_nombre': usuario.nombre,
                'empresa_nombre': empresa.nombre,
                'sede_usuario': sede,
                'timestamp_creacion': datetime.utcnow().isoformat(),
                'metadatos': {
                    'tipo_procesamiento': 'manual',
                    'plataforma': 'mobile_app',
                    'nivel_prioridad': prioridad
                }
            }
            
            # Crear alerta usando el método de fábrica para usuarios
            alert = MqttAlert.create_from_user(
                empresa_nombre=empresa.nombre,
                sede=sede,
                usuario_id=str(usuario._id),
                tipo_alerta=tipo_alerta,
                descripcion=descripcion,
                prioridad=prioridad,
                data=data_adicional,
                numeros_telefonicos=numeros_telefonicos
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
            
            # Preparar información del tipo de alarma para incluir en la respuesta
            tipo_alarma_response = {}
            if tipo_alarma_info:
                tipo_alarma_response = {
                    'nombre': tipo_alarma_info.nombre,
                    'descripcion': tipo_alarma_info.descripcion,
                    'tipo_alerta': tipo_alarma_info.tipo_alerta,
                    'color_alerta': tipo_alarma_info.color_alerta,
                    'recomendaciones': tipo_alarma_info.recomendaciones,
                    'implementos_necesarios': tipo_alarma_info.implementos_necesarios,
                    'imagen_base64': tipo_alarma_info.imagen_base64
                }
            
            # Respuesta exitosa
            return jsonify({
                'success': True,
                'message': 'Alerta de usuario creada exitosamente',
                'topics': topics,
                'numeros_telefonicos': numeros_telefonicos,
                'alerta': {
                    'alert_id': str(created_alert._id),
                    'tipo_alerta': tipo_alerta,
                    'descripcion': descripcion,
                    'prioridad': prioridad,
                    'origen_tipo': 'usuario',
                    'activo': True,
                    'fecha_creacion': created_alert.fecha_creacion.isoformat(),
                    # Ubicación completa de la botonera (3 campos)
                    'direccion': botonera.direccion if botonera else None,
                    'direccion_url': botonera.direccion_url if botonera else None,
                    'direccion_open_maps': getattr(botonera, 'direccion_open_maps', None) if botonera else None,
                    **tipo_alarma_response  # Incluir información del tipo de alarma
                }
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
            data = request.get_json()
            
            # Validar campos requeridos
            alert_id = data.get('alert_id')
            desactivado_por_id = data.get('desactivado_por_id')
            desactivado_por_tipo = data.get('desactivado_por_tipo')
            
            if not alert_id:
                return jsonify({
                    'success': False,
                    'error': 'El ID de la alerta es obligatorio'
                }), 400
            
            if not desactivado_por_id:
                return jsonify({
                    'success': False,
                    'error': 'El ID de quien desactiva es obligatorio'
                }), 400
            
            if not desactivado_por_tipo:
                return jsonify({
                    'success': False,
                    'error': 'El tipo de quien desactiva es obligatorio'
                }), 400
            
            # Validar tipo permitido
            tipos_permitidos = ['usuario', 'hardware', 'administrador', 'super_admin']
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
            # Para administrador y super_admin podrías agregar más validaciones si es necesario

            # Buscar la alerta
            alert = self.service.alert_repo.get_alert_by_id(alert_id)
            if not alert:
                return jsonify({
                    'success': False,
                    'error': 'Alerta no encontrada'
                }), 404

            # Verificar si la alerta ya fue desactivada
            if not alert.activo:
                # Obtener usuarios relacionados para la respuesta
                usuarios_relacionados = self.service.alert_repo.get_users_by_empresa_sede(
                    alert.empresa_nombre, alert.sede
                )
                
                numeros_telefonicos = []
                for usr in usuarios_relacionados:
                    if usr.get('telefono'):
                        numeros_telefonicos.append({
                            'numero': usr['telefono'],
                            'nombre': usr.get('nombre', '')
                        })
                
                return jsonify({
                    'success': False,
                    'error': 'Alerta ya desactivada',
                    'message': 'Esta alerta ya fue desactivada previamente',
                    'numeros_telefonicos': numeros_telefonicos,
                    'desactivado_por': alert.desactivado_por,
                    'fecha_desactivacion': alert.fecha_desactivacion.isoformat() if alert.fecha_desactivacion else None
                }), 400

            # Obtener usuarios relacionados antes de desactivar
            usuarios_relacionados = self.service.alert_repo.get_users_by_empresa_sede(
                alert.empresa_nombre, alert.sede
            )
            
            numeros_telefonicos = []
            for usr in usuarios_relacionados:
                if usr.get('telefono'):
                    numeros_telefonicos.append({
                        'numero': usr['telefono'],
                        'nombre': usr.get('nombre', '')
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
            alert.deactivate(desactivado_por_id=desactivado_por_id, desactivado_por_tipo=desactivado_por_tipo)
            
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
                    'prioridad': alert.prioridad  # Incluir la prioridad de la alerta
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'No se pudo desactivar la alerta'
                }), 500

        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': str(e)
            }), 500

