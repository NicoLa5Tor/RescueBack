from flask import jsonify, request
from services.phone_lookup_service import PhoneLookupService


class PhoneLookupController:
    """
    Controlador para buscar información de una persona por su número de teléfono.
    No requiere autenticación.
    """
    
    def __init__(self):
        self.phone_lookup_service = PhoneLookupService()
    
    def lookup_by_phone(self):
        """
        GET /api/phone-lookup?telefono=NUMERO
        Busca información de una persona por su número de teléfono.
        
        Query Parameters:
            telefono (str): Número de teléfono a buscar
            
        Returns:
            200: Información encontrada exitosamente
            400: Parámetros faltantes o inválidos
            404: Usuario no encontrado
            500: Error interno del servidor
        """
        try:
            # Obtener número de teléfono desde query parameters
            telefono = request.args.get('telefono', '').strip()
            
            # Validar que el teléfono esté presente
            if not telefono:
                return jsonify({
                    'success': False,
                    'error': 'Parámetro requerido',
                    'message': 'El parámetro "telefono" es obligatorio'
                }), 400
            
            # Llamar al servicio
            result = self.phone_lookup_service.lookup_by_phone(telefono)
            
            # Determinar código de respuesta HTTP
            if result['success']:
                return jsonify(result), 200
            else:
                # Determinar código específico basado en el error
                if 'Usuario no encontrado' in result.get('error', ''):
                    return jsonify(result), 404
                elif 'Teléfono requerido' in result.get('error', ''):
                    return jsonify(result), 400
                else:
                    return jsonify(result), 500
                    
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': f'Ha ocurrido un error inesperado: {str(e)}'
            }), 500
