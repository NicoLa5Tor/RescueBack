from datetime import datetime
from bson import ObjectId

class TipoAlarma:
    """Modelo para tipos de alarma con colores, imágenes y recomendaciones"""
    
    # Enum para tipos de alerta
    TIPOS_ALERTA = {
        'ROJO': 'ROJO',
        'AZUL': 'AZUL',
        'AMARILLO': 'AMARILLO',
        'VERDE': 'VERDE',
        'NARANJA': 'NARANJA'
    }
    
    def __init__(self, nombre=None, descripcion=None, tipo_alerta=None, color_alerta=None, 
                 imagen_base64=None, sonido_link=None, recomendaciones=None, implementos_necesarios=None, 
                 empresa_id=None, activo=True, _id=None):
        self._id = _id or ObjectId()
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo_alerta = tipo_alerta
        self.color_alerta = color_alerta
        self.imagen_base64 = imagen_base64
        self.sonido_link = sonido_link
        self.recomendaciones = recomendaciones or []
        self.implementos_necesarios = implementos_necesarios or []
        self.empresa_id = ObjectId(empresa_id) if empresa_id else None
        self.activo = activo
        self.fecha_creacion = datetime.utcnow()
        self.fecha_actualizacion = datetime.utcnow()
    
    def to_dict(self):
        """Convierte el objeto a diccionario para MongoDB"""
        tipo_alarma_dict = {
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'tipo_alerta': self.tipo_alerta,
            'color_alerta': self.color_alerta,
            'imagen_base64': self.imagen_base64,
            'sonido_link': self.sonido_link,
            'recomendaciones': self.recomendaciones,
            'implementos_necesarios': self.implementos_necesarios,
            'empresa_id': self.empresa_id,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion
        }
        if self._id:
            tipo_alarma_dict['_id'] = self._id
        return tipo_alarma_dict
    
    @classmethod
    def from_dict(cls, data):
        """Crea un objeto TipoAlarma desde un diccionario de MongoDB"""
        tipo_alarma = cls()
        tipo_alarma._id = data.get('_id')
        tipo_alarma.nombre = data.get('nombre')
        tipo_alarma.descripcion = data.get('descripcion')
        tipo_alarma.tipo_alerta = data.get('tipo_alerta')
        tipo_alarma.color_alerta = data.get('color_alerta')
        tipo_alarma.imagen_base64 = data.get('imagen_base64')
        tipo_alarma.sonido_link = data.get('sonido_link')
        tipo_alarma.recomendaciones = data.get('recomendaciones', [])
        tipo_alarma.implementos_necesarios = data.get('implementos_necesarios', [])
        tipo_alarma.empresa_id = data.get('empresa_id')
        tipo_alarma.activo = data.get('activo', True)
        tipo_alarma.fecha_creacion = data.get('fecha_creacion')
        tipo_alarma.fecha_actualizacion = data.get('fecha_actualizacion')
        return tipo_alarma
    
    def to_json(self):
        """Convierte a JSON serializable"""
        return {
            '_id': str(self._id) if self._id else None,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'tipo_alerta': self.tipo_alerta,
            'color_alerta': self.color_alerta,
            'imagen_base64': self.imagen_base64,
            'sonido_link': self.sonido_link,
            'recomendaciones': self.recomendaciones,
            'implementos_necesarios': self.implementos_necesarios,
            'empresa_id': str(self.empresa_id) if self.empresa_id else None,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
    
    def validate(self):
        """Valida los datos del tipo de alarma"""
        errors = []
        
        if not self.nombre or len(self.nombre.strip()) == 0:
            errors.append("El nombre del tipo de alarma es obligatorio")
        
        if len(self.nombre.strip()) < 2:
            errors.append("El nombre debe tener al menos 2 caracteres")
        
        if len(self.nombre.strip()) > 100:
            errors.append("El nombre no puede exceder 100 caracteres")
        
        if not self.descripcion or len(self.descripcion.strip()) == 0:
            errors.append("La descripción es obligatoria")
        
        if len(self.descripcion.strip()) < 5:
            errors.append("La descripción debe tener al menos 5 caracteres")
        
        if len(self.descripcion.strip()) > 500:
            errors.append("La descripción no puede exceder 500 caracteres")
        
        if not self.tipo_alerta or self.tipo_alerta not in self.TIPOS_ALERTA.values():
            errors.append(f"El tipo de alerta debe ser uno de: {', '.join(self.TIPOS_ALERTA.values())}")
        
        if not self.color_alerta or len(self.color_alerta.strip()) == 0:
            errors.append("El color de alerta es obligatorio")

        if self.imagen_base64 and not isinstance(self.imagen_base64, str):
            errors.append("La imagen debe ser una cadena de texto")
        elif isinstance(self.imagen_base64, str) and len(self.imagen_base64.strip()) == 0:
            errors.append("La imagen no puede estar vacía si se proporciona")
        elif isinstance(self.imagen_base64, str) and len(self.imagen_base64) > 2048:
            errors.append("La imagen no puede exceder 2048 caracteres")

        if self.sonido_link and not isinstance(self.sonido_link, str):
            errors.append("El enlace de sonido debe ser una cadena")
        elif self.sonido_link and len(self.sonido_link.strip()) == 0:
            errors.append("El enlace de sonido no puede estar vacío si se proporciona")

        if self.recomendaciones and not isinstance(self.recomendaciones, list):
            errors.append("Las recomendaciones deben ser una lista")

        if self.implementos_necesarios and not isinstance(self.implementos_necesarios, list):
            errors.append("Los implementos necesarios deben ser una lista")
        
        if self.empresa_id and not isinstance(self.empresa_id, ObjectId):
            errors.append("El ID de empresa debe ser un ObjectId válido")
        
        return errors
    
    def deactivate(self):
        """Desactiva el tipo de alarma"""
        self.activo = False
        self.update_timestamp()
    
    def activate(self):
        """Activa el tipo de alarma"""
        self.activo = True
        self.update_timestamp()
    
    def toggle_status(self):
        """Alterna el estado activo/inactivo"""
        if self.activo:
            self.deactivate()
        else:
            self.activate()
    
    def update_timestamp(self):
        """Actualiza el timestamp de modificación"""
        self.fecha_actualizacion = datetime.utcnow()
    
    def normalize_data(self):
        """Normaliza los datos antes de guardar"""
        if self.nombre:
            self.nombre = self.nombre.strip()
        if self.descripcion:
            self.descripcion = self.descripcion.strip()
        if self.tipo_alerta:
            self.tipo_alerta = self.tipo_alerta.upper().strip()
        if self.color_alerta:
            self.color_alerta = self.color_alerta.strip().upper()
        if self.imagen_base64 and isinstance(self.imagen_base64, str):
            self.imagen_base64 = self.imagen_base64.strip()
        if self.sonido_link and isinstance(self.sonido_link, str):
            self.sonido_link = self.sonido_link.strip()
        if self.recomendaciones and isinstance(self.recomendaciones, list):
            self.recomendaciones = [rec.strip() for rec in self.recomendaciones if isinstance(rec, str) and rec.strip()]
        if self.implementos_necesarios and isinstance(self.implementos_necesarios, list):
            self.implementos_necesarios = [imp.strip() for imp in self.implementos_necesarios if isinstance(imp, str) and imp.strip()]
    
    def add_recomendacion(self, recomendacion):
        """Agrega una recomendación"""
        if recomendacion and isinstance(recomendacion, str) and recomendacion.strip():
            self.recomendaciones.append(recomendacion.strip())
            self.update_timestamp()
    
    def remove_recomendacion(self, recomendacion):
        """Elimina una recomendación"""
        if recomendacion in self.recomendaciones:
            self.recomendaciones.remove(recomendacion)
            self.update_timestamp()
    
    def add_implemento(self, implemento):
        """Agrega un implemento necesario"""
        if implemento and isinstance(implemento, str) and implemento.strip():
            self.implementos_necesarios.append(implemento.strip())
            self.update_timestamp()
    
    def remove_implemento(self, implemento):
        """Elimina un implemento necesario"""
        if implemento in self.implementos_necesarios:
            self.implementos_necesarios.remove(implemento)
            self.update_timestamp()
