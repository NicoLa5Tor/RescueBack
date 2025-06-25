from datetime import datetime
from bson import ObjectId

class Botonera:
    """Modelo flexible para las botoneras"""
    def __init__(self, empresa_id=None, datos=None, _id=None, activa=True):
        self._id = _id or ObjectId()
        self.empresa_id = empresa_id
        self.datos = datos or {}
        self.fecha_creacion = datetime.utcnow()
        self.fecha_actualizacion = datetime.utcnow()
        self.activa = activa

    def to_dict(self):
        botonera_dict = {
            'empresa_id': self.empresa_id,
            'datos': self.datos,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion,
            'activa': self.activa
        }
        if self._id:
            botonera_dict['_id'] = self._id
        return botonera_dict

    @classmethod
    def from_dict(cls, data):
        botonera = cls()
        botonera._id = data.get('_id')
        botonera.empresa_id = data.get('empresa_id')
        botonera.datos = data.get('datos', {})
        botonera.fecha_creacion = data.get('fecha_creacion')
        botonera.fecha_actualizacion = data.get('fecha_actualizacion')
        botonera.activa = data.get('activa', True)
        return botonera

    def to_json(self):
        return {
            '_id': str(self._id) if self._id else None,
            'empresa_id': str(self.empresa_id) if self.empresa_id else None,
            'datos': self.datos,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'activa': self.activa
        }

    def update_timestamp(self):
        self.fecha_actualizacion = datetime.utcnow()
