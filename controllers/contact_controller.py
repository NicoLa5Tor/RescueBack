from flask import request, jsonify
from services.contact_service import ContactService

class ContactController:
    """Controlador para manejar las peticiones de contacto"""
    
    def __init__(self):
        self.contact_service = ContactService()
    
    def send_contact_email(self):
        """
        POST /api/contact/send
        Procesar formulario de contacto y enviar email
        """
        try:
            # Verificar Content-Type
            if not request.is_json:
                return jsonify({
                    "success": False,
                    "error": "Content-Type debe ser application/json"
                }), 400
            
            # Verificar User-Agent específico
            user_agent = request.headers.get('User-Agent', '')
            expected_user_agent = 'RESCUE-Frontend/1.0'
            
            if user_agent != expected_user_agent:
                return jsonify({
                    "success": False,
                    "error": "User-Agent no autorizado",
                    "details": {
                        "code": "UNAUTHORIZED_USER_AGENT",
                        "message": f"Se esperaba User-Agent: {expected_user_agent}"
                    }
                }), 403
            
            # Obtener datos del cuerpo de la petición
            contact_data = request.get_json()
            
            if not contact_data:
                return jsonify({
                    "success": False,
                    "error": "No se proporcionaron datos",
                    "details": {
                        "code": "MISSING_DATA",
                        "message": "El cuerpo de la petición está vacío"
                    }
                }), 400
            
            # Procesar contacto y enviar email
            result = self.contact_service.create_contact_and_send_email(contact_data)
            
            # Determinar código de respuesta HTTP
            status_code = 200 if result["success"] else 400
            
            # Si es un error de validación, devolver 422
            if not result["success"] and result.get("details", {}).get("code") == "VALIDATION_ERROR":
                status_code = 422
            
            # Si es un error interno, devolver 500
            if not result["success"] and result.get("details", {}).get("code") == "INTERNAL_SERVER_ERROR":
                status_code = 500
            
            return jsonify(result), status_code
            
        except Exception as e:
            print(f"Error in send_contact_email: {e}")
            return jsonify({
                "success": False,
                "error": "Error interno del servidor",
                "details": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Ha ocurrido un error inesperado"
                }
            }), 500
    
    def get_contacts(self):
        """
        GET /api/contact
        Obtener lista de contactos (para administración)
        """
        try:
            # Obtener parámetros de paginación
            limit = int(request.args.get('limit', 100))
            skip = int(request.args.get('skip', 0))
            
            # Limitar el límite máximo
            if limit > 500:
                limit = 500
            
            contacts = self.contact_service.get_all_contacts(limit, skip)
            
            # Convertir a diccionario para JSON
            contacts_dict = []
            for contact in contacts:
                contact_dict = contact.to_dict()
                # Convertir datetime a string para JSON
                if contact_dict.get('created_at'):
                    contact_dict['created_at'] = contact.created_at.isoformat() + 'Z'
                contacts_dict.append(contact_dict)
            
            return jsonify({
                "success": True,
                "data": contacts_dict,
                "pagination": {
                    "limit": limit,
                    "skip": skip,
                    "count": len(contacts_dict)
                }
            }), 200
            
        except Exception as e:
            print(f"Error in get_contacts: {e}")
            return jsonify({
                "success": False,
                "error": "Error interno del servidor"
            }), 500
    
    def get_contact_by_id(self, contact_id):
        """
        GET /api/contact/<contact_id>
        Obtener contacto específico por ID
        """
        try:
            contact = self.contact_service.get_contact_by_id(contact_id)
            
            if not contact:
                return jsonify({
                    "success": False,
                    "error": "Contacto no encontrado"
                }), 404
            
            contact_dict = contact.to_dict()
            # Convertir datetime a string para JSON
            if contact_dict.get('created_at'):
                contact_dict['created_at'] = contact.created_at.isoformat() + 'Z'
            
            return jsonify({
                "success": True,
                "data": contact_dict
            }), 200
            
        except Exception as e:
            print(f"Error in get_contact_by_id: {e}")
            return jsonify({
                "success": False,
                "error": "Error interno del servidor"
            }), 500
    
    def get_contacts_by_status(self, status):
        """
        GET /api/contact/status/<status>
        Obtener contactos por status
        """
        try:
            valid_statuses = ['pending', 'sent', 'failed']
            if status not in valid_statuses:
                return jsonify({
                    "success": False,
                    "error": "Status inválido",
                    "details": {
                        "valid_statuses": valid_statuses
                    }
                }), 400
            
            contacts = self.contact_service.get_contacts_by_status(status)
            
            # Convertir a diccionario para JSON
            contacts_dict = []
            for contact in contacts:
                contact_dict = contact.to_dict()
                # Convertir datetime a string para JSON
                if contact_dict.get('created_at'):
                    contact_dict['created_at'] = contact.created_at.isoformat() + 'Z'
                contacts_dict.append(contact_dict)
            
            return jsonify({
                "success": True,
                "data": contacts_dict,
                "count": len(contacts_dict)
            }), 200
            
        except Exception as e:
            print(f"Error in get_contacts_by_status: {e}")
            return jsonify({
                "success": False,
                "error": "Error interno del servidor"
            }), 500
