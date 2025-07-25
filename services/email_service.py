import resend
import os
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Cargar variables de entorno FORZANDO la ruta específica
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path, override=True)

print(f"🔧 Cargando .env desde: {env_path}")

class EmailService:
    """Servicio para manejar el envío de emails via Resend API"""
    
    def __init__(self):
        # SOLO usar variables del .env, sin fallbacks
        api_key = os.getenv('RESEND_API_KEY')
        if not api_key:
            raise ValueError("RESEND_API_KEY falta en el .env")
        
        self.domain = os.getenv('RESEND_DOMAIN')
        if not self.domain:
            raise ValueError("RESEND_DOMAIN falta en el .env")
            
        self.contact_email = os.getenv('CONTACT_EMAIL')
        if not self.contact_email:
            raise ValueError("CONTACT_EMAIL falta en el .env")
        
        # Configurar resend SOLO con la API key del .env
        resend.api_key = api_key
        
        print(f"📧 EmailService configurado:")
        print(f"   API Key: {api_key[:10]}...")
        print(f"   Domain: {self.domain}")
        print(f"   Contact Email: {self.contact_email}")
    
    def send_contact_email(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enviar email de contacto usando Resend API
        
        Args:
            contact_data: Diccionario con los datos del contacto
            
        Returns:
            Dict con el resultado del envío
        """
        # FORZAR reconfiguración de resend con valores del .env
        api_key = os.getenv('RESEND_API_KEY')
        contact_email = os.getenv('CONTACT_EMAIL')
        domain = os.getenv('RESEND_DOMAIN')
        
        print(f"🔧 FORZANDO configuración desde .env:")
        print(f"   API Key: {api_key[:10]}...")
        print(f"   Contact Email: {contact_email}")
        print(f"   Domain: {domain}")
        
        # Reconfigurar resend forzadamente
        resend.api_key = api_key
        self.contact_email = contact_email
        self.domain = domain
        
        # Generar el HTML del email
        html_content = self._generate_email_html(contact_data)
        text_content = self._generate_email_text(contact_data)
        
        print(f"📄 HTML Content (primeros 200 chars): {html_content[:200]}...")
        print(f"📝 Text Content (primeros 100 chars): {text_content[:100]}...")
        
        # Lista de dominios para intentar (primero el personalizado, luego el de prueba)
        domains_to_try = [
            f"RESCUE System <noreply@{self.domain}>",  # Tu dominio personalizado
            "RESCUE System <onboarding@resend.dev>"    # Dominio de prueba como fallback
        ]
        
        for i, from_email in enumerate(domains_to_try):
            try:
                print(f"📧 Intento {i+1}: Enviando email desde {from_email}...")
                print(f"API Key configurada: {resend.api_key[:10]}...")
                
                # HTML profesional y bonito
                project_types = {
                    "emergency-alerts": "🚨 Alertas de Emergencia",
                    "security-monitoring": "🛡️ Monitoreo de Seguridad", 
                    "industrial-safety": "🏭 Seguridad Industrial",
                    "healthcare-emergency": "🏥 Emergencias Médicas",
                    "educational-safety": "🎓 Seguridad Educativa",
                    "government-alerts": "🏛️ Alertas Gubernamentales",
                    "other": "📋 Otro"
                }
                project_display = project_types.get(contact_data.get('projectType', ''), f"📋 {contact_data.get('projectType', '')}")
                
                simple_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nueva Consulta RESCUE</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f7fa;
        }}
        .email-container {{
            max-width: 650px;
            margin: 20px auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 25px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px 25px;
        }}
        .client-info {{
            background: #f8fafc;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 25px;
            border-left: 4px solid #667eea;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .info-item {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
        }}
        .info-label {{
            font-weight: 600;
            color: #4a5568;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }}
        .info-value {{
            color: #2d3748;
            font-size: 16px;
            font-weight: 500;
        }}
        .message-section {{
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .message-label {{
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 10px;
            font-size: 14px;
        }}
        .message-text {{
            color: #2d3748;
            font-size: 15px;
            line-height: 1.7;
            white-space: pre-wrap;
        }}
        .contact-actions {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 8px;
            padding: 25px;
            text-align: center;
            margin: 25px 0;
        }}
        .contact-title {{
            color: white;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
        }}
        .button-group {{
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        .contact-button {{
            background: rgba(255,255,255,0.2);
            color: white;
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: 600;
            font-size: 14px;
            border: 2px solid rgba(255,255,255,0.3);
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        .contact-button:hover {{
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }}
        .footer {{
            background: #2d3748;
            color: #a0aec0;
            padding: 20px 25px;
            text-align: center;
            font-size: 12px;
        }}
        .footer-logo {{
            font-weight: 700;
            color: #667eea;
            font-size: 16px;
            margin-bottom: 5px;
        }}
        .timestamp {{
            background: #edf2f7;
            color: #4a5568;
            padding: 10px 15px;
            border-radius: 6px;
            font-size: 12px;
            text-align: center;
            margin: 20px 0;
        }}
        @media (max-width: 600px) {{
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            .button-group {{
                flex-direction: column;
                align-items: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>🚨 Nueva Consulta RESCUE</h1>
            <p>Se ha recibido una nueva consulta en el sistema</p>
        </div>
        
        <div class="content">
            <div class="client-info">
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">👤 Cliente</div>
                        <div class="info-value">{contact_data.get('firstName', '')} {contact_data.get('lastName', '')}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">🏢 Empresa</div>
                        <div class="info-value">{contact_data.get('company', '')}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">📧 Email</div>
                        <div class="info-value">{contact_data.get('email', '')}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">📱 Teléfono</div>
                        <div class="info-value">{contact_data.get('phone', 'No proporcionado')}</div>
                    </div>
                </div>
                <div class="info-item">
                    <div class="info-label">🎯 Tipo de Proyecto</div>
                    <div class="info-value">{project_display}</div>
                </div>
            </div>
            
            {f'''<div class="message-section">
                <div class="message-label">💬 Mensaje del Cliente:</div>
                <div class="message-text">{contact_data.get('message', '')}</div>
            </div>''' if contact_data.get('message') else ''}
            
            <div class="contact-actions">
                <div class="contact-title">🚀 Acciones Rápidas</div>
                <div class="button-group">
                    <a href="mailto:{contact_data.get('email', '')}?subject=Re: Consulta RESCUE - {contact_data.get('company', '')}" class="contact-button">
                        📧 Responder Email
                    </a>
                    {f'''<a href="tel:{contact_data.get('phone', '').replace(' ', '').replace('-', '')}" class="contact-button">
                        📞 Llamar Ahora
                    </a>''' if contact_data.get('phone') else ''}
                    {f'''<a href="https://wa.me/{contact_data.get('phone', '').replace(' ', '').replace('-', '').replace('+', '')}?text=Hola {contact_data.get('firstName', '')}, recibimos tu consulta sobre RESCUE. ¿Podemos coordinar una llamada?" class="contact-button">
                        💬 WhatsApp
                    </a>''' if contact_data.get('phone') else ''}
                </div>
            </div>
            
            <div class="timestamp">
                📅 Recibido el {datetime.now().strftime('%d de %B de %Y a las %H:%M:%S')}
            </div>
        </div>
        
        <div class="footer">
            <div class="footer-logo">RESCUE SYSTEM</div>
            <div>Este email fue generado automáticamente por el sistema de contacto</div>
        </div>
    </div>
</body>
</html>"""
                
                simple_text = f"""
Nueva Consulta RESCUE

Nombre: {contact_data.get('firstName', '')} {contact_data.get('lastName', '')}
Email: {contact_data.get('email', '')}
Empresa: {contact_data.get('company', '')}
Teléfono: {contact_data.get('phone', 'No proporcionado')}
Tipo de Proyecto: {contact_data.get('projectType', '')}
{f'Mensaje: {contact_data.get("message", "")}' if contact_data.get('message') else ''}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

---
Este email fue generado por el sistema RESCUE
                """
                
                email_params = {
                    "from": from_email,
                    "to": [self.contact_email],
                    "subject": f"Nueva Consulta RESCUE - {contact_data.get('company', 'Sin empresa')}",  # Sin emoji
                    "html": simple_html,  # HTML más simple
                    "text": simple_text,
                    "reply_to": contact_data.get('email')
                }
                
                print(f"📤 Parámetros del email: {email_params['from']} -> {email_params['to']}")
                
                # Enviar el email
                response = resend.Emails.send(email_params)
                
                print(f"📬 Respuesta de Resend: {response}")
                print(f"📬 Tipo de respuesta: {type(response)}")
                
                # Procesar la respuesta
                if response:
                    # La respuesta de Resend puede ser un dict o un objeto
                    if isinstance(response, dict):
                        email_id = response.get('id')
                    elif hasattr(response, 'id'):
                        email_id = response.id
                    else:
                        email_id = str(response)
                    
                    if email_id:
                        print(f"✅ Email enviado exitosamente con {from_email}")
                        return {
                            "success": True,
                            "email_id": email_id,
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }
                    else:
                        raise Exception(f"Respuesta sin ID: {response}")
                else:
                    raise Exception("Respuesta vacía del servicio de email")
                    
            except Exception as e:
                print(f"❌ Error con {from_email}: {e}")
                
                # Si es el último intento, propagar el error
                if i == len(domains_to_try) - 1:
                    print(f"❌ Todos los dominios fallaron. Último error: {e}")
                    raise e
                
                # Si no es el último intento, continúar con el siguiente dominio
                print(f"🔄 Intentando con el siguiente dominio...")
                continue
        
        # Si llegamos aquí, todos los dominios fallaron
        return {
            "success": False,
            "error": "Error desconocido de Resend API"
        }
    
    def _generate_email_html(self, contact_data: Dict[str, Any]) -> str:
        """Generar contenido HTML del email"""
        project_types = {
            "emergency-alerts": "Alertas de Emergencia",
            "security-monitoring": "Monitoreo de Seguridad",
            "industrial-safety": "Seguridad Industrial",
            "healthcare-emergency": "Emergencias Médicas",
            "educational-safety": "Seguridad Educativa",
            "government-alerts": "Alertas Gubernamentales",
            "other": "Otro"
        }
        
        project_type_display = project_types.get(contact_data.get('projectType', ''), contact_data.get('projectType', ''))
        
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Nueva Consulta RESCUE</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #555; }}
                .value {{ color: #333; }}
                .message-box {{ background: white; padding: 15px; border-left: 4px solid #667eea; margin: 15px 0; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Nueva Consulta RESCUE</h1>
                    <p>Se ha recibido una nueva consulta en el sistema</p>
                </div>
                <div class="content">
                    <div class="field">
                        <span class="label">Nombre:</span>
                        <span class="value">{contact_data.get('firstName', '')} {contact_data.get('lastName', '')}</span>
                    </div>
                    <div class="field">
                        <span class="label">Email:</span>
                        <span class="value">{contact_data.get('email', '')}</span>
                    </div>
                    <div class="field">
                        <span class="label">Empresa:</span>
                        <span class="value">{contact_data.get('company', '')}</span>
                    </div>
                    <div class="field">
                        <span class="label">Teléfono:</span>
                        <span class="value">{contact_data.get('phone', 'No proporcionado')}</span>
                    </div>
                    <div class="field">
                        <span class="label">Tipo de Proyecto:</span>
                        <span class="value">{project_type_display}</span>
                    </div>
                    {f'<div class="message-box"><span class="label">Mensaje:</span><br><span class="value">{contact_data.get("message", "")}</span></div>' if contact_data.get('message') else ''}
                    <div class="field">
                        <span class="label">Fecha:</span>
                        <span class="value">{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</span>
                    </div>
                </div>
                <div class="footer">
                    <p>Este email fue generado automáticamente por el sistema RESCUE</p>
                </div>
            </div>
        </body>
        </html>
        '''
        return html
    
    def _generate_email_text(self, contact_data: Dict[str, Any]) -> str:
        """Generar contenido de texto plano del email"""
        project_types = {
            "emergency-alerts": "Alertas de Emergencia",
            "security-monitoring": "Monitoreo de Seguridad",
            "industrial-safety": "Seguridad Industrial",
            "healthcare-emergency": "Emergencias Médicas",
            "educational-safety": "Seguridad Educativa",
            "government-alerts": "Alertas Gubernamentales",
            "other": "Otro"
        }
        
        project_type_display = project_types.get(contact_data.get('projectType', ''), contact_data.get('projectType', ''))
        
        text = f'''
🚨 NUEVA CONSULTA RESCUE

Nombre: {contact_data.get('firstName', '')} {contact_data.get('lastName', '')}
Email: {contact_data.get('email', '')}
Empresa: {contact_data.get('company', '')}
Teléfono: {contact_data.get('phone', 'No proporcionado')}
Tipo de Proyecto: {project_type_display}

'''
        
        if contact_data.get('message'):
            text += f'''Mensaje:
{contact_data.get('message', '')}

'''
        
        text += f'''Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

---
Este email fue generado automáticamente por el sistema RESCUE
        '''
        
        return text.strip()
