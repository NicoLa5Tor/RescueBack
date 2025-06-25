from functools import wraps
from flask import jsonify, g
from functools import wraps
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt,
    get_jwt_identity,
)


def require_super_admin_token(f):
    """Valida que el JWT pertenezca a un super admin"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "super_admin":
            return (
                jsonify({"success": False, "errors": ["Permiso de super admin requerido"]}),
                401,
            )
        g.super_admin_id = get_jwt_identity()
        return f(*args, **kwargs)

    return decorated_function


def require_empresa_or_super_token(require_empresa_id=False):
    """Permite el acceso con token de empresa o de super admin"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            if role == "super_admin":
                g.is_super_admin = True
                g.super_admin_id = get_jwt_identity()
            elif role == "empresa":
                g.is_super_admin = False
                g.empresa_id = get_jwt_identity()
                if require_empresa_id:
                    if kwargs.get("empresa_id") != str(g.empresa_id):
                        return (
                            jsonify({"success": False, "errors": ["ID de empresa inválido"]}),
                            401,
                        )
            else:
                return (
                    jsonify({"success": False, "errors": ["Permisos insuficientes"]}),
                    401,
                )
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_admin_token(f):
    """Permite solo tokens con rol admin o super_admin"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        role = claims.get("role")
        if role not in ["admin", "super_admin"]:
            return (
                jsonify({"success": False, "errors": ["Permisos de administrador requeridos"]}),
                401,
            )
        g.admin_id = get_jwt_identity()
        g.is_super_admin = role == "super_admin"
        return f(*args, **kwargs)

    return decorated_function


def require_only_admin_token(f):
    """Permite acceso únicamente a usuarios con rol admin"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "admin":
            return (
                jsonify({"success": False, "errors": ["Permisos de administrador requeridos"]}),
                401,
            )
        g.admin_id = get_jwt_identity()
        g.is_super_admin = False
        return f(*args, **kwargs)

    return decorated_function

def require_empresa_or_admin_token(f):
    """Permite el acceso con token de empresa, admin o super_admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        role = claims.get("role")
        if role == "empresa":
            g.empresa_id = get_jwt_identity()
            g.is_super_admin = False
        elif role in ["admin", "super_admin"]:
            g.admin_id = get_jwt_identity()
            g.is_super_admin = role == "super_admin"
        else:
            return (
                jsonify({"success": False, "errors": ["Permisos insuficientes"]}),
                401,
            )
        return f(*args, **kwargs)
    return decorated_function
