from datetime import datetime
from bson import ObjectId
import bcrypt

class Administrador:
    def __init__(self, usuario=None, password_hash=None, nombre=None, email=None, 
                 rol='super_admin', activo=True, _id=None):
        self._id = _id
        self.usuario = usuario
        self.password_hash = password_hash
        self.nombre = nombre
        self.email = email
        self.rol = rol  # 'super_admin'
        self.activo = activo
        self.fecha_creacion = datetime.utcnow()
        self.fecha_actualizacion = datetime.utcnow()
        self.ultimo_login = None
    
    def to_dict(self):
        """Convierte el objeto Administrador a diccionario para MongoDB"""
        admin_dict = {
            'usuario': self.usuario,
            'password_hash': self.password_hash,
            'nombre': self.nombre,
            'email': self.email,
            'rol': self.rol,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion,
            'ultimo_login': self.ultimo_login
        }
        if self._id:
            admin_dict['_id'] = self._id
        return admin_dict
    
    @classmethod
    def from_dict(cls, data):
        """Crea un objeto Administrador desde un diccionario de MongoDB"""
        admin = cls()
        admin._id = data.get('_id')
        admin.usuario = data.get('usuario')
        admin.password_hash = data.get('password_hash')
        admin.nombre = data.get('nombre')
        admin.email = data.get('email')
        admin.rol = data.get('rol', 'super_admin')
        admin.activo = data.get('activo', True)
        admin.fecha_creacion = data.get('fecha_creacion')
        admin.fecha_actualizacion = data.get('fecha_actualizacion')
        admin.ultimo_login = data.get('ultimo_login')
        return admin
    
    def to_json(self):
        """Convierte a JSON serializable (SIN incluir password_hash)"""
        return {
            '_id': str(self._id) if self._id else None,
            'usuario': self.usuario,
            'nombre': self.nombre,
            'email': self.email,
            'rol': self.rol,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'ultimo_login': self.ultimo_login.isoformat() if self.ultimo_login else None
        }
    
    @staticmethod
    def hash_password(password):
        """Genera hash de contraseña"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password):
        """Verifica si la contraseña es correcta"""
        if not self.password_hash or not password:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def update_login_timestamp(self):
        """Actualiza el timestamp del último login"""
        self.ultimo_login = datetime.utcnow()
        self.fecha_actualizacion = datetime.utcnow()