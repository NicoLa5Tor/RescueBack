import re
from datetime import datetime
from typing import Dict, Any, List
from models.contact import Contact
from repositories.contact_repository import ContactRepository
from services.email_service import EmailService

class ContactService:
    """Servicio para manejar la lógica de negocio de contactos"""
    
    def __init__(self):
        self.contact_repository = ContactRepository()
        self.email_service = EmailService()
        
        # Validaciones
        self.validations = {
            "firstName": {
                "required": True,
                "type": "string",
                "minLength": 2,
                "maxLength": 50
            },
            "lastName": {
                "required": True,
                "type": "string", 
                "minLength": 2,
                "maxLength": 50
            },
            "email": {
                "required": True,
                "type": "email",
                "pattern": r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
            },
            "company": {
                "required": True,
                "type": "string",
                "minLength": 2,
                "maxLength": 100
            },
            "phone": {
                "required": False,
                "type": "string",
                "pattern": r"^[\+]?[0-9\s\-\(\)]{10,}$"
            },
            "projectType": {
                "required": True,
                "type": "string",
                "enum": ["emergency-alerts", "security-monitoring", "industrial-safety", 
                        "healthcare-emergency", "educational-safety", "government-alerts", "other"]
            },
            "message": {
                "required": False,
                "type": "string",
                "maxLength": 1000
            },
            "privacy": {
                "required": True,
                "type": "boolean",
                "value": True
            }
        }
    
    def validate_contact_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar los datos del contacto según las reglas definidas
        
        Returns:
            Dict con 'valid': bool y 'errors': List[str]
        """
        errors = []
        
        for field, rules in self.validations.items():
            value = data.get(field)
            
            # Validar campos requeridos
            if rules.get("required", False):
                if value is None or (isinstance(value, str) and not value.strip()):
                    errors.append(f"El campo '{field}' es requerido")
                    continue
            
            # Si el campo no es requerido y está vacío, continuar
            if not rules.get("required", False) and (value is None or value == ""):
                continue
            
            # Validar tipo string
            if rules.get("type") == "string" and value is not None:
                if not isinstance(value, str):
                    errors.append(f"El campo '{field}' debe ser una cadena de texto")
                    continue
                
                # Validar longitud mínima
                if "minLength" in rules and len(value.strip()) < rules["minLength"]:
                    errors.append(f"El campo '{field}' debe tener al menos {rules['minLength']} caracteres")
                
                # Validar longitud máxima
                if "maxLength" in rules and len(value.strip()) > rules["maxLength"]:
                    errors.append(f"El campo '{field}' no puede tener más de {rules['maxLength']} caracteres")
            
            # Validar email
            if rules.get("type") == "email" and value is not None:
                if not isinstance(value, str) or not re.match(rules["pattern"], value):
                    errors.append(f"El campo '{field}' debe ser un email válido")
            
            # Validar boolean
            if rules.get("type") == "boolean" and value is not None:
                if not isinstance(value, bool):
                    errors.append(f"El campo '{field}' debe ser verdadero o falso")
                    continue
                
                # Validar valor específico
                if "value" in rules and value != rules["value"]:
                    errors.append(f"Debe aceptar los términos de privacidad")
            
            # Validar patrones (para teléfono)
            if "pattern" in rules and value is not None and isinstance(value, str):
                if not re.match(rules["pattern"], value):
                    if field == "phone":
                        errors.append("El teléfono debe tener un formato válido (mínimo 10 dígitos)")
                    else:
                        errors.append(f"El campo '{field}' no cumple con el formato requerido")
            
            # Validar enum
            if "enum" in rules and value is not None:
                if value not in rules["enum"]:
                    errors.append(f"El campo '{field}' debe ser uno de: {', '.join(rules['enum'])}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def create_contact_and_send_email(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crear contacto y enviar email
        
        Returns:
            Dict con el resultado de la operación
        """
        try:
            # Validar datos
            validation_result = self.validate_contact_data(contact_data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Datos de contacto inválidos",
                    "details": {
                        "code": "VALIDATION_ERROR",
                        "message": "Los datos proporcionados no son válidos",
                        "errors": validation_result["errors"]
                    }
                }
            
            # Crear objeto Contact
            contact = Contact(
                firstName=contact_data["firstName"].strip(),
                lastName=contact_data["lastName"].strip(),
                email=contact_data["email"].strip().lower(),
                company=contact_data["company"].strip(),
                phone=contact_data.get("phone", "").strip() if contact_data.get("phone") else None,
                projectType=contact_data["projectType"],
                message=contact_data.get("message", "").strip() if contact_data.get("message") else None,
                privacy=contact_data["privacy"],
                created_at=datetime.utcnow()
            )
            
            # Guardar en base de datos
            contact_id = self.contact_repository.create_contact(contact)
            
            # Enviar email
            email_result = self.email_service.send_contact_email(contact_data)
            
            if email_result["success"]:
                # Actualizar status del contacto
                self.contact_repository.update_contact_status(
                    contact_id, 
                    "sent", 
                    email_result["email_id"]
                )
                
                return {
                    "success": True,
                    "message": "Email enviado correctamente",
                    "data": {
                        "emailId": email_result["email_id"],
                        "timestamp": email_result["timestamp"],
                        "recipient": self.email_service.contact_email
                    }
                }
            else:
                # Actualizar status del contacto como fallido
                self.contact_repository.update_contact_status(contact_id, "failed")
                
                return {
                    "success": False,
                    "error": "Error al enviar el email",
                    "details": {
                        "code": "EMAIL_SERVICE_ERROR",
                        "message": email_result.get("error", "No se pudo conectar con el servicio de email")
                    }
                }
                
        except Exception as e:
            # print(f"Error in create_contact_and_send_email: {e}")
            return {
                "success": False,
                "error": "Error interno del servidor",
                "details": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Ha ocurrido un error inesperado al procesar la solicitud"
                }
            }
    
    def get_all_contacts(self, limit: int = 100, skip: int = 0) -> List[Contact]:
        """Obtener todos los contactos"""
        return self.contact_repository.get_all_contacts(limit, skip)
    
    def get_contact_by_id(self, contact_id: str) -> Contact:
        """Obtener contacto por ID"""
        return self.contact_repository.get_contact_by_id(contact_id)
    
    def get_contacts_by_status(self, status: str) -> List[Contact]:
        """Obtener contactos por status"""
        return self.contact_repository.get_contacts_by_status(status)
