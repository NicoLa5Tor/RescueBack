from flask import request, jsonify, make_response
from flask_restx import Resource
from core.swagger_config import (
    auth_ns, 
    login_model, 
    login_response_model, 
    success_response_model, 
    error_response_model,
    refresh_response_model
)
from services.auth_service import AuthService
from middleware.security_middleware import SecurityMiddleware
from flask_jwt_extended import decode_token

# Instancias de servicios
auth_service = AuthService()
security_middleware = SecurityMiddleware()

@auth_ns.route('/login')
class LoginAPI(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(200, 'Login exitoso', login_response_model)
    @auth_ns.response(401, 'Credenciales inválidas', error_response_model)
    @auth_ns.response(500, 'Error interno del servidor', error_response_model)
    @auth_ns.doc(description='''
    Endpoint para iniciar sesión en el sistema RESCUE.
    
    **Funcionamiento:**
    - Valida credenciales de usuario (username/email + password)
    - Genera access token (15 minutos) y refresh token (7 días)
    - Establece ambos tokens como cookies HTTP-only
    - Retorna información del usuario autenticado
    
    **Roles soportados:**
    - `super_admin`: Acceso completo al sistema
    - `admin`: Acceso administrativo limitado
    - `empresa`: Acceso específico a funciones de empresa
    
    **Cookies establecidas:**
    - `auth_token`: Access token para API requests (15 min)
    - `refresh_token`: Token para renovación automática (7 días)
    ''')
    def post(self):
        """Iniciar sesión y obtener tokens de autenticación"""
        try:
            data = request.get_json() or {}
            usuario = data.get('usuario')
            password = data.get('password')

            if not usuario or not password:
                return {'success': False, 'errors': ['Credenciales inválidas']}, 401

            result = auth_service.login(usuario, password)

            if result['success']:
                # Crear respuesta exitosa con cookies seguras
                access_token = result['access_token']
                refresh_token = result['refresh_token']
                response_data = {
                    'success': True, 
                    'user': result['data'],
                    'message': 'Tokens enviados en cookies seguras'
                }
                
                # Necesitamos crear una respuesta personalizada para establecer cookies
                from flask import current_app
                response = current_app.make_response((response_data, 200))
                
                # Decode access token to get JWT ID (jti)
                decoded_token = decode_token(access_token)
                jti = decoded_token.get('jti', None)
                
                # Create secure session record
                security_middleware.create_session_record(
                    user_id=result['data']['id'],
                    fingerprint=security_middleware.get_client_fingerprint(request),
                    jti=jti
                )
                
                # Configurar cookie de access token para desarrollo HTTP
                response.set_cookie(
                    'auth_token',
                    access_token,
                    max_age=15 * 60,       # 15 minutos en segundos
                    httponly=True,         # Cookie no accesible desde JavaScript
                    secure=False,          # False para desarrollo HTTP local
                    samesite='Lax',        # Lax para desarrollo HTTP local
                    domain=None,           # Solo para el dominio actual
                    path='/'               # Disponible en toda la aplicación
                )
                
                # Configurar cookie de refresh token para desarrollo HTTP
                response.set_cookie(
                    'refresh_token',
                    refresh_token,
                    max_age=7 * 24 * 60 * 60,  # 7 días en segundos
                    httponly=True,             # Cookie no accesible desde JavaScript
                    secure=False,              # False para desarrollo HTTP local
                    samesite='Lax',            # Lax para desarrollo HTTP local
                    domain=None,               # Solo para el dominio actual
                    path='/'                   # Disponible en toda la aplicación
                )
                
                return response
            
            return {'success': False, 'errors': result.get('errors', ['Credenciales inválidas'])}, 401
        except Exception as e:
            return {'success': False, 'errors': ['Error interno del servidor']}, 500

@auth_ns.route('/refresh')
class RefreshAPI(Resource):
    @auth_ns.response(200, 'Token renovado exitosamente', refresh_response_model)
    @auth_ns.response(401, 'Refresh token inválido o expirado', error_response_model)
    @auth_ns.response(500, 'Error interno del servidor', error_response_model)
    @auth_ns.doc(description='''
    Endpoint para renovar el access token usando el refresh token.
    
    **Funcionamiento:**
    - Lee el refresh token desde la cookie `refresh_token`
    - Valida que el token sea válido y no haya expirado
    - Verifica que el usuario siga activo en el sistema
    - Genera un nuevo access token (15 minutos)
    - Establece el nuevo access token como cookie
    
    **Uso típico:**
    - Llamado automáticamente por el frontend cuando el access token expira
    - Permite mantener la sesión del usuario sin requerir nuevo login
    - Si el refresh token también expiró, se debe hacer login nuevamente
    
    **Seguridad:**
    - Valida la existencia y estado activo del usuario
    - Actualiza la última actividad del usuario
    - Mantiene los mismos permisos y rol del login original
    ''')
    def post(self):
        """Renovar access token usando refresh token"""
        try:
            # Obtener refresh token desde cookie
            refresh_token = request.cookies.get('refresh_token')
            
            if not refresh_token:
                return {'success': False, 'errors': ['Refresh token faltante']}, 401
            
            # Generar nuevo access token
            result = auth_service.refresh_token(refresh_token)
            
            if result['success']:
                response_data = {
                    'success': True,
                    'message': 'Access token renovado exitosamente'
                }
                
                # Crear respuesta personalizada para establecer cookie
                from flask import current_app
                response = current_app.make_response((response_data, 200))
                
                # Configurar nueva cookie de access token
                response.set_cookie(
                    'auth_token',
                    result['access_token'],
                    max_age=15 * 60,       # 15 minutos en segundos
                    httponly=True,         # Cookie no accesible desde JavaScript
                    secure=False,          # False para desarrollo HTTP local
                    samesite='Lax',        # Lax para desarrollo HTTP local
                    domain=None,           # Solo para el dominio actual
                    path='/'               # Disponible en toda la aplicación
                )
                
                return response
            
            return {'success': False, 'errors': result.get('errors', ['Refresh token inválido'])}, 401
            
        except Exception as e:
            return {'success': False, 'errors': ['Error interno del servidor']}, 500

@auth_ns.route('/logout')
class LogoutAPI(Resource):
    @auth_ns.response(200, 'Logout exitoso', success_response_model)
    @auth_ns.response(500, 'Error interno del servidor', error_response_model)
    @auth_ns.doc(description='''
    Endpoint para cerrar sesión y limpiar tokens.
    
    **Funcionamiento:**
    - Limpia ambas cookies (auth_token y refresh_token)
    - Establece expiración en el pasado para eliminar cookies del navegador
    - Invalida la sesión del usuario
    
    **Recomendaciones:**
    - Llamar siempre al hacer logout para limpiar cookies de seguridad
    - Después del logout, redirigir al usuario a la página de login
    - Las cookies se limpian automáticamente del navegador
    ''')
    def post(self):
        """Cerrar sesión y limpiar tokens"""
        try:
            response_data = {
                'success': True,
                'message': 'Sesión cerrada exitosamente'
            }
            
            # Crear respuesta personalizada para limpiar cookies
            from flask import current_app
            response = current_app.make_response((response_data, 200))
            
            # Limpiar cookies estableciendo expiración en el pasado
            response.set_cookie(
                'auth_token',
                '',
                max_age=0,
                httponly=True,
                secure=False,          # False para desarrollo HTTP local
                samesite='Lax',        # Lax para desarrollo HTTP local
                domain=None,
                path='/'
            )
            
            response.set_cookie(
                'refresh_token',
                '',
                max_age=0,
                httponly=True,
                secure=False,          # False para desarrollo HTTP local
                samesite='Lax',        # Lax para desarrollo HTTP local
                domain=None,
                path='/'
            )
            
            return response
            
        except Exception as e:
            return {'success': False, 'errors': ['Error interno del servidor']}, 500

@auth_ns.route('/test-protected')
class TestProtectedAPI(Resource):
    @auth_ns.doc(security='Bearer')
    @auth_ns.response(200, 'Acceso autorizado', success_response_model)
    @auth_ns.response(401, 'Token inválido o expirado', error_response_model)
    @auth_ns.response(422, 'Token malformado', error_response_model)
    @auth_ns.doc(description='''
    Endpoint de prueba para verificar que la autenticación funciona correctamente.
    
    **Funcionamiento:**
    - Requiere access token válido en cookie `auth_token`
    - Verifica que el token no haya expirado
    - Retorna información básica del usuario autenticado
    
    **Uso:**
    - Ideal para probar el sistema de autenticación
    - Verificar que el refresh token funciona correctamente
    - Debugging de problemas de autenticación
    ''')
    def get(self):
        """Endpoint protegido para probar autenticación"""
        from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
        
        try:
            # Verificar que hay un token válido
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()
            
            user_id = get_jwt_identity()
            jwt_claims = get_jwt()
            
            return jsonify({
                'success': True,
                'message': 'Acceso autorizado',
                'data': {
                    'user_id': user_id,
                    'role': jwt_claims.get('role'),
                    'token_expires': jwt_claims.get('exp')
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': ['Token inválido o expirado']
            }), 401