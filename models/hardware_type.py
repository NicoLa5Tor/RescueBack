from datetime import datetime
from bson import ObjectId

class HardwareType:
    """Modelo para tipos de hardware soportados"""
    def __init__(self, nombre=None, descripcion=None, _id=None, activa=True):
        self._id = _id or ObjectId()
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_creacion = datetime.utcnow()
        self.fecha_actualizacion = datetime.utcnow()
        self.activa = activa

    def to_dict(self):
        data = {
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion,
            'activa': self.activa
        }
        if self._id:
            data['_id'] = self._id
        return data

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj._id = data.get('_id')
        obj.nombre = data.get('nombre')
        obj.descripcion = data.get('descripcion')
        obj.fecha_creacion = data.get('fecha_creacion')
        obj.fecha_actualizacion = data.get('fecha_actualizacion')
        obj.activa = data.get('activa', True)
        return obj

    def to_json(self):
        return {
            '_id': str(self._id) if self._id else None,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'activa': self.activa
        }

    def update_timestamp(self):
        self.fecha_actualizacion = datetime.utcnow()
