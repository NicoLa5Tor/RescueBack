from flask import jsonify, request
from services.hardware_auth_service import HardwareAuthService


class HardwareAuthController:
    """
    Controlador simple para autenticación de hardware.
    Solo autentica hardware verificando que existe y tópico coincide.
    """
    
    def __init__(self):
        self.hardware_auth_service = HardwareAuthService()
    
    def authenticate_hardware(self):
        """
        POST /api/hardware-auth/authenticate
        ÚNICO endpoint de autenticación de hardware.
        Verifica que el hardware existe y que el tópico coincide.
        
        Body JSON:
        {
            "empresa": "nombre_empresa",
            "sede": "nombre_sede", 
            "tipo_hardware": "tipo_hardware",
            "hardware": "nombre_hardware"
        }
        
        Returns:
            200: Token generado exitosamente
            400: Parámetros faltantes
            401: Autenticación fallida
            500: Error interno del servidor
        """
        try:
            # Validar que el request tenga JSON
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Formato inválido',
                    'message': 'El contenido debe ser JSON'
                }), 400
            
            data = request.get_json()
            
            # Extraer parámetros del body
            empresa_nombre = data.get('empresa', '').strip()
            sede_nombre = data.get('sede', '').strip()
            tipo_hardware = data.get('tipo_hardware', '').strip()
            hardware_nombre = data.get('hardware', '').strip()
            
            # Validar que todos los parámetros estén presentes
            if not empresa_nombre or not sede_nombre or not hardware_nombre or not tipo_hardware:
                return jsonify({
                    'success': False,
                    'error': 'Parámetros faltantes',
                    'message': 'Se requieren: empresa, sede, tipo de hardware y hardware'
                }), 400
            
            # Llamar a la función de autenticación
            result = self.hardware_auth_service.authenticate_hardware(
                empresa_nombre=empresa_nombre,
                sede_nombre=sede_nombre,
                tipo_hardware=tipo_hardware,
                hardware_nombre=hardware_nombre
            )
            
            # Determinar código de respuesta HTTP
            if result['success']:
                return jsonify(result), 200
            else:
                # Determinar código específico basado en el error
                if 'Credenciales inválidas' in result.get('error', '') or 'Credenciales inválidas' in result.get('message', ''):
                    return jsonify(result), 401
                else:
                    return jsonify(result), 500
                    
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': f'Ha ocurrido un error inesperado: {str(e)}'
            }), 500
