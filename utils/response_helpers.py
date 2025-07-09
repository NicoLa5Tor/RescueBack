from flask import jsonify

def success_response(data, message=None, status_code=200):
    """
    Respuesta exitosa estandarizada
    
    Args:
        data: Datos a retornar
        message: Mensaje opcional
        status_code: Código de estado HTTP (default: 200)
    
    Returns:
        JSON response con formato estandarizado
    """
    response = {
        "success": True,
        "data": data
    }
    
    if message:
        response["message"] = message
    
    return jsonify(response), status_code

def error_response(errors, status_code=400):
    """
    Respuesta de error estandarizada
    
    Args:
        errors: Lista de errores o string único
        status_code: Código de estado HTTP (default: 400)
    
    Returns:
        JSON response con formato estandarizado
    """
    if isinstance(errors, str):
        errors = [errors]
    
    response = {
        "success": False,
        "errors": errors
    }
    
    return jsonify(response), status_code

def validation_error_response(errors, status_code=400):
    """
    Respuesta de error de validación estandarizada
    
    Args:
        errors: Diccionario de errores de validación por campo
        status_code: Código de estado HTTP (default: 400)
    
    Returns:
        JSON response con formato estandarizado
    """
    response = {
        "success": False,
        "validation_errors": errors
    }
    
    return jsonify(response), status_code
