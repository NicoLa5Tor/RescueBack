from datetime import datetime
from bson import ObjectId

class TipoEmpresa:
    def __init__(
        self,
        nombre=None,
        descripcion=None,
        caracteristicas=None,
        activo=True,
        creado_por=None,
        _id=None,
    ):
        self._id = _id or ObjectId()
        self.nombre = nombre
        self.descripcion = descripcion
        self.caracteristicas = caracteristicas or []  # Lista de características
        self.activo = activo
        self.creado_por = creado_por
        self.fecha_creacion = datetime.utcnow()
        self.fecha_actualizacion = datetime.utcnow()
    
    def to_dict(self):
        """Convierte el objeto TipoEmpresa a diccionario para MongoDB"""
        tipo_empresa_dict = {
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'caracteristicas': self.caracteristicas,
            'activo': self.activo,
            'creado_por': self.creado_por,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion
        }
        if self._id:
            tipo_empresa_dict['_id'] = self._id
        return tipo_empresa_dict
    
    @classmethod
    def from_dict(cls, data):
        """Crea un objeto TipoEmpresa desde un diccionario de MongoDB"""
        tipo_empresa = cls()
        tipo_empresa._id = data.get('_id')
        tipo_empresa.nombre = data.get('nombre')
        tipo_empresa.descripcion = data.get('descripcion')
        tipo_empresa.caracteristicas = data.get('caracteristicas', [])
        tipo_empresa.activo = data.get('activo', True)
        tipo_empresa.creado_por = data.get('creado_por')
        tipo_empresa.fecha_creacion = data.get('fecha_creacion')
        tipo_empresa.fecha_actualizacion = data.get('fecha_actualizacion')
        return tipo_empresa
    
    def to_json(self, include_empresas=False, empresas_data=None):
        """Convierte a JSON serializable"""
        result = {
            '_id': str(self._id) if self._id else None,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'caracteristicas': self.caracteristicas,
            'activo': self.activo,
            'creado_por': str(self.creado_por) if self.creado_por else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
        
        # Incluir información de empresas si se solicita
        if include_empresas and empresas_data is not None:
            result['empresas_asociadas'] = empresas_data
            result['empresas_count'] = len(empresas_data)
        
        return result
    
    def validate(self):
        """Valida los datos del tipo de empresa"""
        errors = []
        
        if not self.nombre or (isinstance(self.nombre, str) and len(self.nombre.strip()) == 0):
            errors.append("El nombre del tipo de empresa es obligatorio")
        elif isinstance(self.nombre, str):
            if len(self.nombre.strip()) < 2:
                errors.append("El nombre debe tener al menos 2 caracteres")
            elif len(self.nombre.strip()) > 50:
                errors.append("El nombre no puede exceder 50 caracteres")
        
        if self.descripcion and len(self.descripcion.strip()) > 200:
            errors.append("La descripción no puede exceder 200 caracteres")
        
        # Validaciones para características
        if self.caracteristicas is not None:
            if not isinstance(self.caracteristicas, list):
                errors.append("Las características deben ser una lista")
            else:
                if len(self.caracteristicas) > 20:
                    errors.append("No se pueden tener más de 20 características")
                
                for i, caracteristica in enumerate(self.caracteristicas):
                    if not isinstance(caracteristica, str):
                        errors.append(f"La característica {i+1} debe ser una cadena de texto")
                    elif len(caracteristica.strip()) == 0:
                        errors.append(f"La característica {i+1} no puede estar vacía")
                    elif len(caracteristica.strip()) > 100:
                        errors.append(f"La característica {i+1} no puede exceder 100 caracteres")
        
        if not self.creado_por:
            errors.append("El ID del creador es obligatorio")

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
        # Normalizar características
        if self.caracteristicas:
            self.caracteristicas = [car.strip() for car in self.caracteristicas if car and car.strip()]
