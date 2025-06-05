from datetime import datetime
from bson import ObjectId

class User:
    def __init__(self, name=None, email=None, age=None, _id=None):
        self._id = _id
        self.name = name
        self.email = email
        self.age = age
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convierte el objeto User a diccionario para MongoDB"""
        user_dict = {
            'name': self.name,
            'email': self.email,
            'age': self.age,
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
        
        return errors
    
    def update_timestamp(self):
        """Actualiza el timestamp de modificación"""
        self.updated_at = datetime.utcnow()