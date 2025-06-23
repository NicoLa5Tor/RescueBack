from functools import wraps
from flask import request, jsonify, g
from config import Config


def require_super_admin_token(f):
    """Requiere token de super admin para acceder"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("X-Super-Admin-Token")
        if not token or token != Config.SUPER_ADMIN_TOKEN:
            return (
                jsonify(
                    {"success": False, "errors": ["Token de super admin inválido"]}
                ),
                401,
            )
        g.super_admin_id = request.headers.get("X-Super-Admin-ID")
        return f(*args, **kwargs)

    return decorated_function


def require_empresa_or_super_token(require_empresa_id=False):
    """Permite token de empresa o de super admin"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            super_token = request.headers.get("X-Super-Admin-Token")
            empresa_token = request.headers.get("X-Empresa-Token")
            if super_token and super_token == Config.SUPER_ADMIN_TOKEN:
                g.is_super_admin = True
                return f(*args, **kwargs)
            if empresa_token and empresa_token == Config.EMPRESA_TOKEN:
                g.is_super_admin = False
                if require_empresa_id:
                    empresa_id = request.headers.get("X-Empresa-ID")
                    if not empresa_id or empresa_id != kwargs.get("empresa_id"):
                        return (
                            jsonify(
                                {"success": False, "errors": ["ID de empresa inválido"]}
                            ),
                            401,
                        )
                    g.empresa_id = empresa_id
                return f(*args, **kwargs)
            return jsonify({"success": False, "errors": ["Token inválido"]}), 401

        return decorated_function

    return decorator
