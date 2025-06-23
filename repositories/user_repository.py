from bson import ObjectId
from datetime import datetime
from database import Database
from models.user import User

class UserRepository:
    def __init__(self):
        self.db = Database().get_database()
        self.collection = self.db.users
    
    def create(self, user):
        """Crea un nuevo usuario en la base de datos"""
        try:
            user_dict = user.to_dict()
            result = self.collection.insert_one(user_dict)
            user._id = result.inserted_id
            return user
        except Exception as e:
            raise Exception(f"Error creando usuario: {str(e)}")
    
    def find_by_id(self, user_id):
        """Busca un usuario por ID"""
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            user_data = self.collection.find_one({"_id": user_id})
            if user_data:
                return User.from_dict(user_data)
            return None
        except Exception as e:
            raise Exception(f"Error buscando usuario por ID: {str(e)}")
    
    def find_all(self):
        """Obtiene todos los usuarios"""
        try:
            users_data = self.collection.find()
            users = []
            for user_data in users_data:
                users.append(User.from_dict(user_data))
            return users
        except Exception as e:
            raise Exception(f"Error obteniendo usuarios: {str(e)}")
    
    def find_by_email(self, email):
        """Busca un usuario por email"""
        try:
            user_data = self.collection.find_one({"email": email})
            if user_data:
                return User.from_dict(user_data)
            return None
        except Exception as e:
            raise Exception(f"Error buscando usuario por email: {str(e)}")
    
    def update(self, user_id, user):
        """Actualiza un usuario existente"""
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            user.update_timestamp()
            user_dict = user.to_dict()
            user_dict.pop('_id', None)  # Remover _id del dict para actualización
            
            result = self.collection.update_one(
                {"_id": user_id},
                {"$set": user_dict}
            )
            
            if result.matched_count > 0:
                return self.find_by_id(user_id)
            return None
        except Exception as e:
            raise Exception(f"Error actualizando usuario: {str(e)}")
    
    def delete(self, user_id):
        """Elimina un usuario por ID"""
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            result = self.collection.delete_one({"_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            raise Exception(f"Error eliminando usuario: {str(e)}")
    
    def count(self):
        """Cuenta el total de usuarios"""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            raise Exception(f"Error contando usuarios: {str(e)}")
    
    def find_by_age_range(self, min_age, max_age):
        """Busca usuarios por rango de edad"""
        try:
            users_data = self.collection.find({
                "age": {"$gte": min_age, "$lte": max_age}
            })
            users = []
            for user_data in users_data:
                users.append(User.from_dict(user_data))
            return users
        except Exception as e:
            raise Exception(f"Error buscando usuarios por edad: {str(e)}")

    def find_by_telefono(self, telefono):
        """Busca un usuario por número de teléfono"""
        try:
            user_data = self.collection.find_one({"telefono": telefono})
            if user_data:
                return User.from_dict(user_data)
            return None
        except Exception as e:
            raise Exception(f"Error buscando usuario por telefono: {str(e)}")
