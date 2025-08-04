import requests
import json
from core.config import Config

class WhatsAppServiceClient:
    """
    Cliente para consumir el servicio de WhatsApp
    """
    
    def __init__(self):
        self.api_base_url = Config.WHATSAPP_SERVICE_URL
        self.broadcast_endpoint = f"{self.api_base_url}/send-broadcast-template"
        self.timeout = Config.WHATSAPP_SERVICE_TIMEOUT
    
    def enviar_broadcast_plantilla(self, phones, template_name, language="es_CO", parameters=None, use_queue=False):
        """
        Envía una plantilla de WhatsApp a múltiples números
        
        Args:
            phones (list): Lista de números de teléfono
            template_name (str): Nombre de la plantilla
            language (str): Código de idioma
            parameters (list): Parámetros de la plantilla
            use_queue (bool): Si usar cola para el envío
        
        Returns:
            dict: Respuesta de la API
        """
        
        payload = {
            "phones": phones,
            "template_name": template_name,
            "language": language,
            "parameters": parameters or [],
            "use_queue": use_queue
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                self.broadcast_endpoint, 
                headers=headers, 
                json=payload,
                timeout=self.timeout
            )
            
            try:
                result = response.json()
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": f"Respuesta no válida del servicio. Status: {response.status_code}",
                    "data": None
                }
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": result.get('data', result),
                    "debug_info": result.get('debug_info'),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', f'Error HTTP {response.status_code}'),
                    "data": None,
                    "debug_info": result.get('debug_info')
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": f"Timeout al conectar con el servicio de WhatsApp (>{self.timeout}s)",
                "data": None
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Error de conexión con el servicio de WhatsApp",
                "data": None
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Error en la petición: {str(e)}",
                "data": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error inesperado: {str(e)}",
                "data": None
            }


# Instancia global del cliente
whatsapp_client = WhatsAppServiceClient()
