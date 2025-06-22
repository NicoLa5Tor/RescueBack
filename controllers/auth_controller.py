from flask import request, jsonify
from flask_jwt_extended import create_access_token
from models.auth_user import AuthUser, db

class AuthController:
    def login(self):
        try:
            data = request.get_json() or {}
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return jsonify({'success': False, 'errors': ['Credenciales faltantes']}), 400

            user = AuthUser.query.filter_by(email=email).first()
            if not user or not user.check_password(password):
                return jsonify({'success': False, 'errors': ['Credenciales inválidas']}), 401

            if not user.is_active:
                return jsonify({'success': False, 'errors': ['Usuario inactivo']}), 403

            additional_claims = {
                'email': user.email,
                'role': user.role
            }
            access_token = create_access_token(identity=user.id, additional_claims=additional_claims)

            return jsonify({
                'success': True,
                'access_token': access_token,
                'role': user.role
            }), 200
        except Exception:
            return jsonify({'success': False, 'errors': ['Error interno']}), 500
