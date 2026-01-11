from functools import wraps
from flask import jsonify, request
from core.config import Config


def require_internal_token(f):
    """Valida un token interno enviado en un header custom."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        header_name = Config.INTERNAL_TOKEN_HEADER or 'X-Internal-Token'
        expected_token = Config.INTERNAL_TOKEN

        if not expected_token:
            return jsonify({
                'success': False,
                'errors': ['Token interno no configurado']
            }), 500

        token = request.headers.get(header_name)
        if not token:
            return jsonify({
                'success': False,
                'errors': ['Token interno faltante']
            }), 401

        if token != expected_token:
            return jsonify({
                'success': False,
                'errors': ['Token interno inválido']
            }), 401

        return f(*args, **kwargs)

    return decorated_function
