from flask import request, jsonify
from services.auth_service import AuthService

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()

    def login(self):
        """Endpoint POST /auth/login"""
        try:
            data = request.get_json() or {}
            usuario = data.get('usuario')
            password = data.get('password')

            if not usuario or not password:
                return jsonify({'success': False, 'errors': ['Credenciales inválidas']}), 401

            result = self.auth_service.login(usuario, password)
            print(f"Lo que viene de login es: {result}")

            if result['success']:
                return jsonify({'success': True, 'token': result['token'], 'user': result['data']}), 200
            return jsonify({'success': False, 'errors': result.get('errors', ['Credenciales inválidas'])}), 401
        except Exception as e:
            return jsonify({'success': False, 'errors': [f'Error interno del servidor: {str(e)}']}), 500
