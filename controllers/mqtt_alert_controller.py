from flask import jsonify, request
from services.mqtt_alert_service import MqttAlertService
from services.hardware_auth_service import HardwareAuthService
from utils.auth_utils import get_auth_header, get_auth_cookie

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
                'empresa_id': token_payload['empresa_id'],
                'empresa_nombre': token_payload['empresa_nombre'],
                'sede': token_payload['sede'],
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
        """Endpoint de prueba para demostrar el flujo completo"""
        try:
            # Datos de prueba que simulan mensaje MQTT
            test_data = {
                'empresa1': {
                    'semaforo': {
                        'sede': 'principal',
                        'alerta': 'amarilla',
                        'ubicacion': 'Cruce principal',
                        'hardware_id': 'SEM001',
                        'nombre': 'Semaforo001',
                        'coordenadas': {'lat': 4.6097, 'lng': -74.0817}
                    }
                }
            }
            
            # Procesar mensaje
            result = self.service.process_mqtt_message(test_data)
            
            # Agregar información adicional sobre la funcionalidad
            response = {
                'test_result': result,
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
                },
                'message': 'Prueba del flujo completo con verificación de hardware'
            }
            
            return jsonify(response), 200
            
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

