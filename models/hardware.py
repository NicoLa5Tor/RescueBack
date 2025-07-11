from datetime import datetime
from bson import ObjectId

class Hardware:
    """Modelo generico para cualquier hardware"""
    def __init__(self, nombre=None, tipo=None, empresa_id=None, sede=None, datos=None, _id=None, activa=True, topic=None):
        self._id = _id or ObjectId()
        self.nombre = nombre
        self.tipo = tipo
        self.empresa_id = ObjectId(empresa_id) if empresa_id else None
        self.sede = sede
        self.datos = datos or {}
        self.direccion = None  # Nueva propiedad de dirección
        self.direccion_url = None  # Nueva propiedad de URL de dirección
        self.topic = topic  # Campo topic generado automáticamente
        self.fecha_creacion = datetime.utcnow()
        self.fecha_actualizacion = datetime.utcnow()
        self.activa = activa

    def to_dict(self):
        hardware_dict = {
            'nombre': self.nombre,
            'tipo': self.tipo,
            'empresa_id': self.empresa_id,
            'sede': self.sede,
            'datos': self.datos,
            'direccion': self.direccion,  # Nueva dirección
            'direccion_url': self.direccion_url,  # Nueva URL de dirección
            'topic': self.topic,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion,
            'activa': self.activa
        }
        if self._id:
            hardware_dict['_id'] = self._id
        return hardware_dict

    @classmethod
    def from_dict(cls, data):
        hw = cls()
        hw._id = data.get('_id')
        hw.nombre = data.get('nombre')
        hw.tipo = data.get('tipo')
        hw.empresa_id = data.get('empresa_id')
        hw.sede = data.get('sede')
        hw.datos = data.get('datos', {})
        hw.direccion = data.get('direccion')  # Nueva dirección
        hw.direccion_url = data.get('direccion_url')  # Nueva URL de dirección
        hw.topic = data.get('topic')
        hw.fecha_creacion = data.get('fecha_creacion')
        hw.fecha_actualizacion = data.get('fecha_actualizacion')
        hw.activa = data.get('activa', True)
        return hw

    def to_json(self):
        return {
            '_id': str(self._id) if self._id else None,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'empresa_id': str(self.empresa_id) if self.empresa_id else None,
            'sede': self.sede,
            'datos': self.datos,
            'direccion': self.direccion,  # Nueva dirección
            'direccion_url': self.direccion_url,  # Nueva URL de dirección
            'topic': self.topic,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'activa': self.activa
        }

    def update_timestamp(self):
        self.fecha_actualizacion = datetime.utcnow()
    
    def generate_topic(self, empresa_nombre, sede, tipo, nombre_hardware):
        """Genera el topic automáticamente con formato: empresaNombre/sede/TIPO/nombreHardware"""
        # Limpiar caracteres especiales y espacios
        empresa_clean = self._clean_topic_part(empresa_nombre)
        sede_clean = self._clean_topic_part(sede)
        tipo_clean = tipo.upper().replace(' ', '')
        hardware_clean = self._clean_topic_part(nombre_hardware)
        
        return f"{empresa_clean}/{sede_clean}/{tipo_clean}/{hardware_clean}"
    
    def _clean_topic_part(self, part):
        """Limpia una parte del topic removiendo espacios y caracteres especiales"""
        if not part:
            return ""
        # Remover espacios, caracteres especiales y convertir a formato apropiado
        import re
        cleaned = re.sub(r'[^a-zA-Z0-9_-]', '', part.replace(' ', ''))
        return cleaned
