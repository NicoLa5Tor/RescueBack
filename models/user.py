from datetime import datetime
from bson import ObjectId

class User:
    def __init__(self, name=None, email=None, age=None, empresa_id=None,
                 telefono=None, whatsapp_verify=False, _id=None):
        self._id = _id or ObjectId()
        self.name = name
        self.email = email
        self.age = age
        self.empresa_id = ObjectId(empresa_id) if empresa_id else None
        self.telefono = telefono
        self.whatsapp_verify = whatsapp_verify
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convierte el objeto User a diccionario para MongoDB"""
        user_dict = {
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'empresa_id': self.empresa_id,
            'telefono': self.telefono,
            'whatsapp_verify': self.whatsapp_verify,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        if self._id:
            user_dict['_id'] = self._id
        return user_dict
    
    @classmethod
    def from_dict(cls, data):
        """Crea un objeto User desde un diccionario de MongoDB"""
        user = cls()
        user._id = data.get('_id')
        user.name = data.get('name')
        user.email = data.get('email')
        user.age = data.get('age')
        user.empresa_id = data.get('empresa_id')
        user.telefono = data.get('telefono')
        user.whatsapp_verify = data.get('whatsapp_verify', False)
        user.created_at = data.get('created_at')
        user.updated_at = data.get('updated_at')
        return user
    
    def to_json(self):
        """Convierte a JSON serializable"""
        return {
            '_id': str(self._id) if self._id else None,
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'empresa_id': str(self.empresa_id) if self.empresa_id else None,
            'telefono': self.telefono,
            'whatsapp_verify': self.whatsapp_verify,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def validate(self):
        """Valida los datos del usuario"""
        errors = []
        
        if not self.name or len(self.name.strip()) == 0:
            errors.append("El nombre es obligatorio")
        
        if not self.email or len(self.email.strip()) == 0:
            errors.append("El email es obligatorio")
        
        if '@' not in self.email:
            errors.append("El email debe tener un formato válido")

        if not isinstance(self.age, int) or self.age < 0:
            errors.append("La edad debe ser un número positivo")

        if not self.empresa_id:
            errors.append("El ID de la empresa es obligatorio")

        if not self.telefono or len(str(self.telefono).strip()) == 0:
            errors.append("El teléfono es obligatorio")
        elif not str(self.telefono).isdigit():
            errors.append("El teléfono debe contener solo números")

        return errors
    
    def update_timestamp(self):
        """Actualiza el timestamp de modificación"""
        self.updated_at = datetime.utcnow()
