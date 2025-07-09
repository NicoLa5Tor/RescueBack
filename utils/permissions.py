from functools import wraps
from flask import jsonify, g
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt,
    get_jwt_identity,
)


def require_super_admin_token(f):
    """Solo permite acceso a super_admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "super_admin":
            return (
                jsonify({"success": False, "errors": ["Permiso de super admin requerido"]}),
                401,
            )
        g.user_id = get_jwt_identity()
        g.role = "super_admin"
        return f(*args, **kwargs)
    return decorated_function


def require_empresa_token(f):
    """Solo permite acceso a empresa"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "empresa":
            return (
                jsonify({"success": False, "errors": ["Permiso de empresa requerido"]}),
                401,
            )
        g.user_id = get_jwt_identity()
        g.role = "empresa"
        return f(*args, **kwargs)
    return decorated_function


def require_empresa_or_admin_token(f):
    """Permite acceso tanto a empresa como a super_admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        role = claims.get("role")
        if role in ["empresa", "super_admin"]:
            g.user_id = get_jwt_identity()
            g.role = role
        else:
            return (
                jsonify({"success": False, "errors": ["Permisos insuficientes"]}),
                401,
            )
        return f(*args, **kwargs)
    return decorated_function
