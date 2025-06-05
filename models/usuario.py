from datetime import datetime
from bson import ObjectId

class Usuario:
    def __init__(self, nombre=None, cedula=None, rol=None, empresa_id=None, _id=None):
        self._id = _id
        self.nombre = nombre
        self.cedula = cedula
        self.rol = rol
        self.empresa_id = empresa_id
        self.fecha_creacion = datetime.utcnow()
        self.fecha_actualizacion = datetime.utcnow()
        self.activo = True
    
    def to_dict(self):
        """Convierte el objeto Usuario a diccionario para MongoDB"""
        usuario_dict = {
            'nombre': self.nombre,
            'cedula': self.cedula,
            'rol': self.rol,
            'empresa_id': self.empresa_id,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion,
            'activo': self.activo
        }
        if self._id:
            usuario_dict['_id'] = self._id
        return usuario_dict
    
    @classmethod
    def from_dict(cls, data):
        """Crea un objeto Usuario desde un diccionario de MongoDB"""
        usuario = cls()
        usuario._id = data.get('_id')
        usuario.nombre = data.get('nombre')
        usuario.cedula = data.get('cedula')
        usuario.rol = data.get('rol')
        usuario.empresa_id = data.get('empresa_id')
        usuario.fecha_creacion = data.get('fecha_creacion')
        usuario.fecha_actualizacion = data.get('fecha_actualizacion')
        usuario.activo = data.get('activo', True)
        return usuario
    
    def to_json(self):
        """Convierte a JSON serializable"""
        return {
            '_id': str(self._id) if self._id else None,
            'nombre': self.nombre,
            'cedula': self.cedula,
            'rol': self.rol,
            'empresa_id': str(self.empresa_id) if self.empresa_id else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'activo': self.activo
        }
    
    def validate(self):
        """Valida los datos del usuario"""
        errors = []
        
        if not self.nombre or len(self.nombre.strip()) == 0:
            errors.append("El nombre es obligatorio")
        
        if len(self.nombre.strip()) < 2:
            errors.append("El nombre debe tener al menos 2 caracteres")
        
        if len(self.nombre.strip()) > 100:
            errors.append("El nombre no puede exceder 100 caracteres")
        
        if not self.cedula or len(str(self.cedula).strip()) == 0:
            errors.append("La cédula es obligatoria")
        
        # Validar que la cédula sea numérica
        try:
            cedula_str = str(self.cedula).strip()
            if not cedula_str.isdigit():
                errors.append("La cédula debe contener solo números")
            elif len(cedula_str) < 6 or len(cedula_str) > 15:
                errors.append("La cédula debe tener entre 6 y 15 dígitos")
        except:
            errors.append("La cédula debe ser un número válido")
        
        if not self.rol or len(self.rol.strip()) == 0:
            errors.append("El rol es obligatorio")
        
        # Validar roles permitidos
        roles_validos = ['admin', 'usuario', 'supervisor', 'operador', 'gerente']
        if self.rol and self.rol.lower() not in roles_validos:
            errors.append(f"El rol debe ser uno de: {', '.join(roles_validos)}")
        
        if not self.empresa_id:
            errors.append("El ID de la empresa es obligatorio")
        
        return errors
    
    def normalize_data(self):
        """Normaliza los datos antes de guardar"""
        if self.nombre:
            self.nombre = self.nombre.strip()
        if self.cedula:
            self.cedula = str(self.cedula).strip()
        if self.rol:
            self.rol = self.rol.strip().lower()
    
    def update_timestamp(self):
        """Actualiza el timestamp de modificación"""
        self.fecha_actualizacion = datetime.utcnow()