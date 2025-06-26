from datetime import datetime
from bson import ObjectId

class Hardware:
    """Modelo generico para cualquier hardware"""
    def __init__(self, nombre=None, tipo=None, empresa_id=None, sede=None, datos=None, _id=None, activa=True):
        self._id = _id or ObjectId()
        self.nombre = nombre
        self.tipo = tipo
        self.empresa_id = ObjectId(empresa_id) if empresa_id else None
        self.sede = sede
        self.datos = datos or {}
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
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'activa': self.activa
        }

    def update_timestamp(self):
        self.fecha_actualizacion = datetime.utcnow()
