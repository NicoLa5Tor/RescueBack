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
                # Crear respuesta exitosa con cookie segura
                token = result['token']
                response_data = {
                    'success': True, 
                    'user': result['data'],
                    'message': 'Token enviado en cookie segura'
                }
                
                response = make_response(jsonify(response_data), 200)
                
                # Decode token to get JWT ID (jti)
                decoded_token = decode_token(token)
                jti = decoded_token.get('jti', None)
                
                # Create secure session record
                self.security_middleware.create_session_record(
                    user_id=result['data']['id'],
                    fingerprint=self.security_middleware.get_client_fingerprint(request),
                    jti=jti
                )
                
                # Configurar cookie para desarrollo HTTP
                response.set_cookie(
                    'auth_token',
                    token,
                    max_age=24 * 60 * 60,  # 24 horas en segundos
                    httponly=True,         # Cookie no accesible desde JavaScript
                    secure=False,          # False para desarrollo HTTP local
                    samesite='Lax',        # Lax para desarrollo HTTP local
                    domain=None,           # Solo para el dominio actual
                    path='/'               # Disponible en toda la aplicación
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
            
            # Limpiar cookie estableciendo expiración en el pasado
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
            
            return response
            
        except Exception as e:
            return jsonify({'success': False, 'errors': ['Error interno del servidor']}), 500
