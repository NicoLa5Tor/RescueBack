from flask import jsonify, request, make_response
from services.hardware_auth_service import HardwareAuthService
from utils.auth_utils import get_auth_cookie, get_auth_header
from typing import Dict, Any


class HardwareAuthController:
    """
    Controlador para autenticación de hardware.
    Implementa el endpoint único para validar hardware, empresa y sede,
    y generar tokens temporales de autorización.
    """
    
    def __init__(self):
        self.hardware_auth_service = HardwareAuthService()
    
    def authenticate_hardware(self):
        """
        POST /api/hardware-auth/authenticate
        Endpoint único que valida hardware, empresa y sede, y genera token temporal.
        
        Body JSON:
        {
            "hardware_nombre": "Sensor001",
            "empresa_nombre": "TechCorp",
            "sede": "Sede Principal"
        }
        
        Returns:
            200: Token generado exitosamente
            400: Parámetros faltantes o inválidos
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
            hardware_nombre = data.get('hardware_nombre', '').strip()
            empresa_nombre = data.get('empresa_nombre', '').strip()
            sede = data.get('sede', '').strip()
            
            # Validar que todos los parámetros estén presentes
            if not hardware_nombre or not empresa_nombre or not sede:
                return jsonify({
                    'success': False,
                    'error': 'Parámetros faltantes',
                    'message': 'Se requieren: hardware_nombre, empresa_nombre y sede',
                    'received': {
                        'hardware_nombre': bool(hardware_nombre),
                        'empresa_nombre': bool(empresa_nombre),
                        'sede': bool(sede)
                    }
                }), 400
            
            # Llamar al servicio de autenticación
            result = self.hardware_auth_service.authenticate_hardware(
                hardware_nombre=hardware_nombre,
                empresa_nombre=empresa_nombre,
                sede=sede
            )
            
            # Determinar código de respuesta HTTP
            if result['success']:
                # Crear respuesta exitosa con cookie segura
                token = result['data']['token']
                response_data = result.copy()
                # Remover el token del JSON response
                del response_data['data']['token']
                response_data['data']['message'] = 'Token enviado en cookie segura'
                
                response = make_response(jsonify(response_data), 200)
                
                # Configurar cookie segura con HttpOnly y Secure
                response.set_cookie(
                    'hardware_auth_token',
                    token,
                    max_age=self.hardware_auth_service.token_expiry_minutes * 60,  # 5 minutos en segundos
                    httponly=True,
                    secure=True,  # Solo HTTPS en producción
                    samesite='Strict'
                )
                
                return response
            else:
                # Determinar código específico basado en el error
                if 'no encontrada' in result['message'] or 'no existe' in result['message']:
                    return jsonify(result), 401
                elif 'faltante' in result['error']:
                    return jsonify(result), 400
                else:
                    return jsonify(result), 500
                    
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': f'Ha ocurrido un error inesperado: {str(e)}'
            }), 500
    
    def verify_token(self):
        """
        POST /api/hardware-auth/verify-token
        Verifica si un token es válido y no ha expirado.
        
        Headers:
            Authorization: Bearer <token>
        
        Returns:
            200: Token válido
            401: Token inválido o expirado
            400: Token faltante
            500: Error interno del servidor
        """
        try:
            # Obtener token de la cookie o del header Authorization (fallback)
            token = get_auth_cookie(request) or get_auth_header(request)
            
            if not token:
                return jsonify({
                    'success': False,
                    'error': 'Token faltante',
                    'message': 'Se requiere token en cookie o header Authorization'
                }), 400
            
            # Verificar token
            result = self.hardware_auth_service.verify_token(token)
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 401
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': f'Ha ocurrido un error inesperado: {str(e)}'
            }), 500
    
    def get_active_sessions(self):
        """
        GET /api/hardware-auth/sessions?hardware_id=<hardware_id>
        Obtiene las sesiones activas de autenticación.
        
        Query Parameters:
            hardware_id (opcional): ID del hardware para filtrar sesiones
        
        Returns:
            200: Lista de sesiones activas
            500: Error interno del servidor
        """
        try:
            hardware_id = request.args.get('hardware_id')
            
            result = self.hardware_auth_service.get_active_sessions(hardware_id)
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': f'Ha ocurrido un error inesperado: {str(e)}'
            }), 500
    
    def cleanup_expired_sessions(self):
        """
        DELETE /api/hardware-auth/cleanup
        Limpia sesiones expiradas de la base de datos.
        
        Returns:
            200: Limpieza exitosa
            500: Error interno del servidor
        """
        try:
            result = self.hardware_auth_service.cleanup_expired_sessions()
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': f'Ha ocurrido un error inesperado: {str(e)}'
            }), 500
    
    def get_hardware_auth_info(self):
        """
        GET /api/hardware-auth/info
        Obtiene información sobre el sistema de autenticación de hardware.
        
        Returns:
            200: Información del sistema
        """
        try:
            return jsonify({
                'success': True,
                'system_info': {
                    'name': 'Sistema de Autenticación de Hardware',
                    'version': '1.0.0',
                    'token_expiry_minutes': self.hardware_auth_service.token_expiry_minutes,
                    'endpoints': {
                        'authenticate': 'POST /api/hardware-auth/authenticate',
                        'verify_token': 'POST /api/hardware-auth/verify-token',
                        'active_sessions': 'GET /api/hardware-auth/sessions',
                        'cleanup': 'DELETE /api/hardware-auth/cleanup',
                        'info': 'GET /api/hardware-auth/info'
                    },
                    'authentication_flow': [
                        '1. Hardware envía credenciales (nombre, empresa, sede)',
                        '2. Sistema valida empresa existe y está activa',
                        '3. Sistema valida sede existe en la empresa',
                        '4. Sistema valida hardware existe, está activo y pertenece a la empresa',
                        '5. Sistema genera token temporal JWT válido por 5 minutos',
                        '6. Token se envía en cookie segura HttpOnly',
                        '7. Hardware usa token para autorizar envío de alertas'
                    ]
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': f'Ha ocurrido un error inesperado: {str(e)}'
            }), 500
    
    def logout_hardware(self):
        """
        POST /api/hardware-auth/logout
        Cierra sesión y limpia la cookie de autenticación.
        
        Returns:
            200: Logout exitoso
            500: Error interno del servidor
        """
        try:
            response = make_response(jsonify({
                'success': True,
                'message': 'Sesión cerrada exitosamente'
            }), 200)
            
            # Limpiar cookie estableciendo expiración en el pasado
            response.set_cookie(
                'hardware_auth_token',
                '',
                max_age=0,
                httponly=True,
                secure=True,
                samesite='Strict'
            )
            
            return response
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': f'Ha ocurrido un error inesperado: {str(e)}'
            }), 500
