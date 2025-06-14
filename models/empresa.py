from datetime import datetime
from bson import ObjectId

class Empresa:
    def __init__(self, nombre=None, descripcion=None, ubicacion=None, creado_por=None, _id=None,password=None):
        self._id = _id
        self.nombre = nombre
        self.descripcion = descripcion
        self.ubicacion = ubicacion
        self.creado_por = creado_por
        self.password = password
        self.fecha_creacion = datetime.utcnow()
        self.fecha_actualizacion = datetime.utcnow()
        self.activa = True  # Campo adicional para soft delete
    
    def to_dict(self):
        """Convierte el objeto Empresa a diccionario para MongoDB"""
        empresa_dict = {
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'ubicacion': self.ubicacion,
            'creado_por': self.creado_por,
            'fecha_creacion': self.fecha_creacion,
            'password' : self.password,
            'fecha_actualizacion': self.fecha_actualizacion,
            'activa': self.activa
        }
        if self._id:
            empresa_dict['_id'] = self._id
        return empresa_dict
    
    @classmethod
    def from_dict(cls, data):
        """Crea un objeto Empresa desde un diccionario de MongoDB"""
        empresa = cls()
        empresa._id = data.get('_id')
        empresa.nombre = data.get('nombre')
        empresa.descripcion = data.get('descripcion')
        empresa.ubicacion = data.get('ubicacion')
        empresa.creado_por = data.get('creado_por')
        empresa.fecha_creacion = data.get('fecha_creacion')
        empresa.fecha_actualizacion = data.get('fecha_actualizacion')
        empresa.activa = data.get('activa', True)
        return empresa
    
    def to_json(self):
        """Convierte a JSON serializable"""
        return {
            '_id': str(self._id) if self._id else None,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'ubicacion': self.ubicacion,
            'creado_por': str(self.creado_por) if self.creado_por else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'activa': self.activa
        }
    
    def validate(self):
        """Valida los datos de la empresa"""
        errors = []
        
        if not self.nombre or len(self.nombre.strip()) == 0:
            errors.append("El nombre de la empresa es obligatorio")
        
        if len(self.nombre.strip()) < 2:
            errors.append("El nombre debe tener al menos 2 caracteres")
        
        if len(self.nombre.strip()) > 100:
            errors.append("El nombre no puede exceder 100 caracteres")
        
        if not self.descripcion or len(self.descripcion.strip()) == 0:
            errors.append("La descripción de la empresa es obligatoria")
        
        if len(self.descripcion.strip()) < 10:
            errors.append("La descripción debe tener al menos 10 caracteres")
        
        if len(self.descripcion.strip()) > 500:
            errors.append("La descripción no puede exceder 500 caracteres")
        
        if not self.ubicacion or len(self.ubicacion.strip()) == 0:
            errors.append("La ubicación de la empresa es obligatoria")
        
        if len(self.ubicacion.strip()) < 3:
            errors.append("La ubicación debe tener al menos 3 caracteres")
        
        if len(self.ubicacion.strip()) > 200:
            errors.append("La ubicación no puede exceder 200 caracteres")
        
        if not self.creado_por:
            errors.append("El ID del super admin creador es obligatorio")
        
        return errors
    
    def update_timestamp(self):
        """Actualiza el timestamp de modificación"""
        self.fecha_actualizacion = datetime.utcnow()
    
    def normalize_data(self):
        """Normaliza los datos antes de guardar"""
        if self.nombre:
            self.nombre = self.nombre.strip()
        if self.descripcion:
            self.descripcion = self.descripcion.strip()
        if self.ubicacion:
            self.ubicacion = self.ubicacion.strip()