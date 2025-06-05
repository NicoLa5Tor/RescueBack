from bson import ObjectId
from datetime import datetime
from database import Database
from models.usuario import Usuario

class UsuarioRepository:
    def __init__(self):
        self.db = Database().get_database()
        self.collection = self.db.usuarios
        # Crear índices necesarios
        self._create_indexes()
    
    def _create_indexes(self):
        """Crea los índices necesarios para la colección"""
        try:
            # Índice único compuesto para cédula + empresa_id
            self.collection.create_index([
                ("cedula", 1), 
                ("empresa_id", 1)
            ], unique=True)
            
            # Índice para búsquedas por empresa
            self.collection.create_index([("empresa_id", 1)])
            
            # Índice para usuarios activos
            self.collection.create_index([("activo", 1)])
            
            # Índice para búsquedas por rol
            self.collection.create_index([("rol", 1)])
            
            print("Índices de usuarios creados correctamente")
        except Exception as e:
            print(f"Error creando índices de usuarios: {e}")
    
    def create(self, usuario):
        """Crea un nuevo usuario en la base de datos"""
        try:
            usuario.normalize_data()
            usuario_dict = usuario.to_dict()
            result = self.collection.insert_one(usuario_dict)
            usuario._id = result.inserted_id
            return usuario
        except Exception as e:
            # Verificar si es error de duplicado
            if "duplicate key error" in str(e).lower() or "11000" in str(e):
                raise Exception("Ya existe un usuario con esa cédula en esta empresa")
            raise Exception(f"Error creando usuario: {str(e)}")
    
    def find_by_id(self, usuario_id):
        """Busca un usuario por ID"""
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)
            
            usuario_data = self.collection.find_one({"_id": usuario_id, "activo": True})
            if usuario_data:
                return Usuario.from_dict(usuario_data)
            return None
        except Exception as e:
            raise Exception(f"Error buscando usuario por ID: {str(e)}")
    
    def find_by_empresa(self, empresa_id):
        """Obtiene todos los usuarios de una empresa"""
        try:
            if isinstance(empresa_id, str):
                empresa_id = ObjectId(empresa_id)
            
            usuarios_data = self.collection.find({
                "empresa_id": empresa_id,
                "activo": True
            }).sort("fecha_creacion", -1)
            
            usuarios = []
            for usuario_data in usuarios_data:
                usuarios.append(Usuario.from_dict(usuario_data))
            return usuarios
        except Exception as e:
            raise Exception(f"Error obteniendo usuarios por empresa: {str(e)}")
    
    def find_by_cedula_and_empresa(self, cedula, empresa_id):
        """Busca un usuario por cédula dentro de una empresa específica"""
        try:
            if isinstance(empresa_id, str):
                empresa_id = ObjectId(empresa_id)
            
            usuario_data = self.collection.find_one({
                "cedula": str(cedula).strip(),
                "empresa_id": empresa_id,
                "activo": True
            })
            
            if usuario_data:
                return Usuario.from_dict(usuario_data)
            return None
        except Exception as e:
            raise Exception(f"Error buscando usuario por cédula: {str(e)}")
    
    def update(self, usuario_id, usuario):
        """Actualiza un usuario existente"""
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)
            
            usuario.normalize_data()
            usuario.update_timestamp()
            usuario_dict = usuario.to_dict()
            usuario_dict.pop('_id', None)
            
            result = self.collection.update_one(
                {"_id": usuario_id, "activo": True},
                {"$set": usuario_dict}
            )
            
            if result.matched_count > 0:
                return self.find_by_id(usuario_id)
            return None
        except Exception as e:
            if "duplicate key error" in str(e).lower() or "11000" in str(e):
                raise Exception("Ya existe un usuario con esa cédula en esta empresa")
            raise Exception(f"Error actualizando usuario: {str(e)}")
    
    def soft_delete(self, usuario_id):
        """Realiza un soft delete de un usuario"""
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)
            
            result = self.collection.update_one(
                {"_id": usuario_id, "activo": True},
                {
                    "$set": {
                        "activo": False,
                        "fecha_actualizacion": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Error eliminando usuario: {str(e)}")
    
    def count_by_empresa(self, empresa_id):
        """Cuenta los usuarios activos de una empresa"""
        try:
            if isinstance(empresa_id, str):
                empresa_id = ObjectId(empresa_id)
            
            return self.collection.count_documents({
                "empresa_id": empresa_id,
                "activo": True
            })
        except Exception as e:
            raise Exception(f"Error contando usuarios: {str(e)}")
    
    def find_by_rol_and_empresa(self, rol, empresa_id):
        """Busca usuarios por rol dentro de una empresa"""
        try:
            if isinstance(empresa_id, str):
                empresa_id = ObjectId(empresa_id)
            
            usuarios_data = self.collection.find({
                "rol": rol.lower(),
                "empresa_id": empresa_id,
                "activo": True
            }).sort("nombre", 1)
            
            usuarios = []
            for usuario_data in usuarios_data:
                usuarios.append(Usuario.from_dict(usuario_data))
            return usuarios
        except Exception as e:
            raise Exception(f"Error buscando usuarios por rol: {str(e)}")