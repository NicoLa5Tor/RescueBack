from flask import request, jsonify, make_response
from services.auth_service import AuthService
from middleware.security_middleware import SecurityMiddleware
from flask_jwt_extended import decode_token

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()
        self.security_middleware = SecurityMiddleware()

    def login(self):
        """Endpoint POST /auth/login"""
        try:
            data = request.get_json() or {}
            usuario = data.get('usuario')
            password = data.get('password')

            if not usuario or not password:
                return jsonify({'success': False, 'errors': ['Credenciales inválidas']}), 401

            result = self.auth_service.login(usuario, password)
            # print(f"Lo que viene de login es: {result}")

            if result['success']:
                # Crear respuesta exitosa con cookies seguras
                access_token = result['access_token']
                refresh_token = result['refresh_token']
                response_data = {
                    'success': True, 
                    'user': result['data'],
                    'message': 'Tokens enviados en cookies seguras'
                }
                
                response = make_response(jsonify(response_data), 200)
                
                # Decode access token to get JWT ID (jti)
                decoded_token = decode_token(access_token)
                jti = decoded_token.get('jti', None)
                
                # Create secure session record
                self.security_middleware.create_session_record(
                    user_id=result['data']['id'],
                    fingerprint=self.security_middleware.get_client_fingerprint(request),
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
            return jsonify({'success': False, 'errors': result.get('errors', ['Credenciales inválidas'])}), 401
        except Exception as e:
            return jsonify({'success': False, 'errors': ['Error interno del servidor']}), 500
    
    def logout(self):
        """Endpoint POST /auth/logout"""
        try:
            response = make_response(jsonify({
                'success': True,
                'message': 'Sesión cerrada exitosamente'
            }), 200)
            
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
            return jsonify({'success': False, 'errors': ['Error interno del servidor']}), 500

    def refresh(self):
        """Endpoint POST /auth/refresh"""
        try:
            # Obtener refresh token desde cookie
            refresh_token = request.cookies.get('refresh_token')
            
            if not refresh_token:
                return jsonify({'success': False, 'errors': ['Refresh token faltante']}), 401
            
            # Generar nuevo access token
            result = self.auth_service.refresh_token(refresh_token)
            
            if result['success']:
                response_data = {
                    'success': True,
                    'message': 'Access token renovado exitosamente'
                }
                
                response = make_response(jsonify(response_data), 200)
                
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
            
            return jsonify({'success': False, 'errors': result.get('errors', ['Refresh token inválido'])}), 401
            
        except Exception as e:
            return jsonify({'success': False, 'errors': ['Error interno del servidor']}), 500
