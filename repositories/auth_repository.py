from bson import ObjectId
from datetime import datetime
from database import Database
from models.administrador import Administrador

class AuthRepository:
    def __init__(self):
        self.db = Database().get_database()
        self.admin_collection = self.db.administradores
        self.empresa_collection = self.db.empresas
        # Crear índices necesarios
        self._create_indexes()
    
    def _create_indexes(self):
        """Crea los índices necesarios para autenticación"""
        try:
            # Índice único para usuario de administrador
            self.admin_collection.create_index([("usuario", 1)], unique=True)
            
            # Índice único para email de administrador
            self.admin_collection.create_index([("email", 1)], unique=True)
            
            # Índice para administradores activos
            self.admin_collection.create_index([("activo", 1)])
            
            print("Índices de autenticación creados correctamente")
        except Exception as e:
            print(f"Error creando índices de autenticación: {e}")
    
    def find_admin_by_usuario(self, usuario):
        """Busca un administrador por nombre de usuario"""
        try:
            admin_data = self.admin_collection.find_one({
                "usuario": usuario,
                "activo": True
            })
            if admin_data:
                return Administrador.from_dict(admin_data)
            return None
        except Exception as e:
            raise Exception(f"Error buscando administrador: {str(e)}")
    
    def find_admin_by_email(self, email):
        """Busca un administrador por email"""
        try:
            admin_data = self.admin_collection.find_one({
                "email": email,
                "activo": True
            })
            if admin_data:
                return Administrador.from_dict(admin_data)
            return None
        except Exception as e:
            raise Exception(f"Error buscando administrador por email: {str(e)}")
    
    def find_admin_by_id(self, admin_id):
        """Busca un administrador por ID"""
        try:
            if isinstance(admin_id, str):
                admin_id = ObjectId(admin_id)
            
            admin_data = self.admin_collection.find_one({
                "_id": admin_id,
                "activo": True
            })
            if admin_data:
                return Administrador.from_dict(admin_data)
            return None
        except Exception as e:
            raise Exception(f"Error buscando administrador por ID: {str(e)}")
    
    def find_empresa_by_email(self, email):
        """Busca una empresa por email para login"""
        try:
            # Asumir que las empresas tienen un campo 'email' para login
            empresa_data = self.empresa_collection.find_one({
                "email": email,
                "activa": True
            })
            if empresa_data:
                return empresa_data
            return None
        except Exception as e:
            raise Exception(f"Error buscando empresa por email: {str(e)}")
    
    def find_empresa_by_id(self, empresa_id):
        """Busca una empresa por ID"""
        try:
            if isinstance(empresa_id, str):
                empresa_id = ObjectId(empresa_id)
            
            empresa_data = self.empresa_collection.find_one({
                "_id": empresa_id,
                "activa": True
            })
            return empresa_data
        except Exception as e:
            raise Exception(f"Error buscando empresa por ID: {str(e)}")
    
    def update_admin_login(self, admin_id):
        """Actualiza el timestamp del último login del administrador"""
        try:
            if isinstance(admin_id, str):
                admin_id = ObjectId(admin_id)
            
            result = self.admin_collection.update_one(
                {"_id": admin_id},
                {
                    "$set": {
                        "ultimo_login": datetime.utcnow(),
                        "fecha_actualizacion": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Error actualizando login de administrador: {str(e)}")
    
    def update_empresa_login(self, empresa_id):
        """Actualiza el timestamp del último login de la empresa"""
        try:
            if isinstance(empresa_id, str):
                empresa_id = ObjectId(empresa_id)
            
            result = self.empresa_collection.update_one(
                {"_id": empresa_id},
                {
                    "$set": {
                        "ultimo_login": datetime.utcnow(),
                        "fecha_actualizacion": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Error actualizando login de empresa: {str(e)}")