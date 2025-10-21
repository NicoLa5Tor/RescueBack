from datetime import datetime
from bson import ObjectId

class Usuario:
    def __init__(self, nombre=None, cedula=None, rol=None, empresa_id=None, 
                 especialidades=None, certificaciones=None, tipo_turno=None, 
                 telefono=None, email=None, sede=None, _id=None):
        self._id = _id
        self.nombre = nombre
        self.cedula = cedula
        self.rol = rol
        self.empresa_id = empresa_id
        self.especialidades = especialidades or []  # lista de especialidades
        self.certificaciones = certificaciones or []  # lista de certificaciones
        self.tipo_turno = tipo_turno  # medio_dia, dia_completo, nocturno, 24_horas
        self.telefono = telefono  # contacto directo
        self.email = email  # email de contacto
        self.sede = sede  # sede de la empresa a la que pertenece
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
            'especialidades': self.especialidades,
            'certificaciones': self.certificaciones,
            'tipo_turno': self.tipo_turno,
            'telefono': self.telefono,
            'email': self.email,
            'sede': self.sede,
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
        usuario.especialidades = data.get('especialidades', [])
        usuario.certificaciones = data.get('certificaciones', [])
        usuario.tipo_turno = data.get('tipo_turno')
        usuario.telefono = data.get('telefono')
        usuario.email = data.get('email')
        usuario.sede = data.get('sede')
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
            'especialidades': self.especialidades,
            'certificaciones': self.certificaciones,
            'tipo_turno': self.tipo_turno,
            'telefono': self.telefono,
            'email': self.email,
            'sede': self.sede,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'activo': self.activo
        }
    
    def validate(self):
        """Valida los datos del usuario"""
        errors = []
        
        if not self.nombre or len(self.nombre.strip()) == 0:
            errors.append("El nombre es obligatorio")
        elif len(self.nombre.strip()) < 2:
            errors.append("El nombre debe tener al menos 2 caracteres")
        elif len(self.nombre.strip()) > 100:
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
        
        # El rol ya no se valida con lista fija, viene de la empresa
        
        if not self.empresa_id:
            errors.append("El ID de la empresa es obligatorio")
        
        # Validar sede si se proporciona
        if self.sede:
            if not isinstance(self.sede, str) or len(self.sede.strip()) == 0:
                errors.append("La sede debe ser una cadena no vacía")
            elif len(self.sede.strip()) > 100:
                errors.append("La sede no puede exceder 100 caracteres")
        
        # Validar especialidades si se proporcionan
        if self.especialidades is not None:
            if not isinstance(self.especialidades, list):
                errors.append("Las especialidades deben ser una lista")
            else:
                for especialidad in self.especialidades:
                    if not isinstance(especialidad, str) or len(especialidad.strip()) == 0:
                        errors.append("Cada especialidad debe ser una cadena no vacía")
                        break
        
        # Validar tipo_turno si se proporciona
        if self.tipo_turno:
            tipos_turno_validos = ['medio_dia', 'dia_completo', 'nocturno', '24_horas']
            if self.tipo_turno.lower() not in tipos_turno_validos:
                errors.append(f"El tipo de turno debe ser uno de: {', '.join(tipos_turno_validos)}")
        
        # Validar teléfono si se proporciona
        if self.telefono:
            telefono_str = str(self.telefono).strip()
            if not telefono_str.isdigit():
                errors.append("El teléfono debe contener solo números")
            elif len(telefono_str) < 7 or len(telefono_str) > 15:
                errors.append("El teléfono debe tener entre 7 y 15 dígitos")
        
        # Validar email si se proporciona
        if self.email:
            if '@' not in self.email or '.' not in self.email:
                errors.append("El email debe tener un formato válido")
        
        # Validar certificaciones si se proporcionan
        if self.certificaciones:
            if not isinstance(self.certificaciones, list):
                errors.append("Las certificaciones deben ser una lista")
            else:
                for cert in self.certificaciones:
                    if not isinstance(cert, str) or len(cert.strip()) == 0:
                        errors.append("Cada certificación debe ser una cadena no vacía")
                        break
        
        return errors
    
    def normalize_data(self):
        """Normaliza los datos antes de guardar"""
        if self.nombre:
            self.nombre = self.nombre.strip()
        if self.cedula:
            self.cedula = str(self.cedula).strip()
        if self.rol:
            self.rol = self.rol.strip().lower()
        if self.sede:
            self.sede = self.sede.strip()
        if self.especialidades and isinstance(self.especialidades, list):
            self.especialidades = [esp.strip() for esp in self.especialidades if isinstance(esp, str)]
        if self.tipo_turno:
            self.tipo_turno = self.tipo_turno.strip().lower()
    
    def update_timestamp(self):
        """Actualiza el timestamp de modificación"""
        self.fecha_actualizacion = datetime.utcnow()
