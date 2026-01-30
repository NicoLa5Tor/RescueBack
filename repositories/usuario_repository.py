from bson import ObjectId
from datetime import datetime
from core.database import Database
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
            # Índice para búsquedas por empresa
            self.collection.create_index([("empresa_id", 1)])
            
            # Índice para usuarios activos
            self.collection.create_index([("activo", 1)])
            
            # Índice para búsquedas por rol
            self.collection.create_index([("rol", 1)])
            
            # Índices para búsquedas por cédula y teléfono (no únicos para permitir validación personalizada)
            self.collection.create_index([("cedula", 1)])
            self.collection.create_index([("telefono", 1)])
            
            # print("Índices de usuarios creados correctamente")
        except Exception as e:
            # print(f"Error creando índices de usuarios: {e}")
            pass
    
    def create(self, usuario):
        """Crea un nuevo usuario en la base de datos"""
        try:
            usuario.normalize_data()
            
            # Validar unicidad global de cédula y teléfono
            validation_errors = self.validate_unique_global_fields(
                usuario.cedula, 
                usuario.telefono
            )
            
            if validation_errors:
                raise Exception("; ".join(validation_errors))
            
            usuario_dict = usuario.to_dict()
            result = self.collection.insert_one(usuario_dict)
            usuario._id = result.inserted_id
            return usuario
        except Exception as e:
            # Si el error ya es de validación, lo re-lanzamos
            if "ya está en uso" in str(e):
                raise e
            # Verificar si es error de duplicado de MongoDB
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
    
    def find_by_id_including_inactive(self, usuario_id):
        """Busca un usuario por ID incluyendo inactivos"""
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)
            
            usuario_data = self.collection.find_one({"_id": usuario_id})
            if usuario_data:
                return Usuario.from_dict(usuario_data)
            return None
        except Exception as e:
            raise Exception(f"Error buscando usuario por ID (incluyendo inactivos): {str(e)}")
    
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
    
    def find_by_empresa_including_inactive(self, empresa_id):
        """Obtiene todos los usuarios de una empresa incluyendo inactivos"""
        try:
            if isinstance(empresa_id, str):
                empresa_id = ObjectId(empresa_id)
            
            usuarios_data = self.collection.find({
                "empresa_id": empresa_id
            }).sort("fecha_creacion", -1)
            
            usuarios = []
            for usuario_data in usuarios_data:
                usuarios.append(Usuario.from_dict(usuario_data))
            return usuarios
        except Exception as e:
            raise Exception(f"Error obteniendo usuarios por empresa (incluyendo inactivos): {str(e)}")
    
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
    
    def find_by_cedula_and_empresa_excluding_id(self, cedula, empresa_id, exclude_id):
        """Busca un usuario por cédula dentro de una empresa específica excluyendo un ID"""
        try:
            if isinstance(empresa_id, str):
                empresa_id = ObjectId(empresa_id)
            if isinstance(exclude_id, str):
                exclude_id = ObjectId(exclude_id)
            
            usuario_data = self.collection.find_one({
                "cedula": str(cedula).strip(),
                "empresa_id": empresa_id,
                "activo": True,
                "_id": {"$ne": exclude_id}
            })
            
            if usuario_data:
                return Usuario.from_dict(usuario_data)
            return None
        except Exception as e:
            raise Exception(f"Error buscando usuario por cédula (excluyendo ID): {str(e)}")
    
    def update(self, usuario_id, usuario):
        """Actualiza un usuario existente"""
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)
            
            usuario.normalize_data()
            usuario.update_timestamp()
            
            # Validar unicidad global de cédula y teléfono (excluyendo el usuario actual)
            validation_errors = self.validate_unique_global_fields(
                usuario.cedula, 
                usuario.telefono,
                exclude_id=usuario_id
            )
            
            if validation_errors:
                raise Exception("; ".join(validation_errors))
            
            usuario_dict = usuario.to_dict()
            usuario_dict.pop('_id', None)
            
            # Removemos el filtro de activo para permitir actualizar usuarios inactivos
            result = self.collection.update_one(
                {"_id": usuario_id},
                {"$set": usuario_dict}
            )
            
            if result.matched_count > 0:
                return self.find_by_id_including_inactive(usuario_id)
            return None
        except Exception as e:
            # Si el error ya es de validación, lo re-lanzamos
            if "ya está en uso" in str(e):
                raise e
            if "duplicate key error" in str(e).lower() or "11000" in str(e):
                raise Exception("Ya existe un usuario con esa cédula en esta empresa")
            raise Exception(f"Error actualizando usuario: {str(e)}")
    
    def update_status_only(self, usuario_id, activo):
        """Actualiza solo el estado activo/inactivo de un usuario sin validaciones"""
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)
            
            result = self.collection.update_one(
                {"_id": usuario_id},
                {
                    "$set": {
                        "activo": activo,
                        "fecha_actualizacion": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count > 0:
                return self.find_by_id_including_inactive(usuario_id)
            return None
        except Exception as e:
            raise Exception(f"Error actualizando estado del usuario: {str(e)}")
    
    def soft_delete(self, usuario_id):
        """Realiza un soft delete de un usuario"""
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)
            
            # Removemos el filtro de activo para permitir eliminar cualquier usuario
            result = self.collection.update_one(
                {"_id": usuario_id},
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
    
    def find_by_cedula_global(self, cedula, exclude_id=None):
        """Busca un usuario por cédula a nivel global (todas las empresas)"""
        try:
            query = {
                "cedula": str(cedula).strip(),
                "activo": True
            }
            
            if exclude_id:
                if isinstance(exclude_id, str):
                    exclude_id = ObjectId(exclude_id)
                query["_id"] = {"$ne": exclude_id}
            
            usuario_data = self.collection.find_one(query)
            
            if usuario_data:
                return Usuario.from_dict(usuario_data)
            return None
        except Exception as e:
            raise Exception(f"Error buscando usuario por cédula global: {str(e)}")
    
    def find_by_telefono_global(self, telefono, exclude_id=None):
        """Busca un usuario por teléfono a nivel global (todas las empresas)"""
        try:
            query = {
                "telefono": str(telefono).strip(),
                "activo": True
            }
            
            if exclude_id:
                if isinstance(exclude_id, str):
                    exclude_id = ObjectId(exclude_id)
                query["_id"] = {"$ne": exclude_id}
            
            usuario_data = self.collection.find_one(query)
            
            if usuario_data:
                return Usuario.from_dict(usuario_data)
            return None
        except Exception as e:
            raise Exception(f"Error buscando usuario por teléfono global: {str(e)}")

    def find_inactive_by_cedula_global(self, cedula):
        """Busca un usuario inactivo por cédula a nivel global"""
        try:
            usuario_data = self.collection.find_one({
                "cedula": str(cedula).strip(),
                "activo": False
            })
            if usuario_data:
                return Usuario.from_dict(usuario_data)
            return None
        except Exception as e:
            raise Exception(f"Error buscando usuario inactivo por cédula global: {str(e)}")

    def find_inactive_by_telefono_global(self, telefono):
        """Busca un usuario inactivo por teléfono a nivel global"""
        try:
            usuario_data = self.collection.find_one({
                "telefono": str(telefono).strip(),
                "activo": False
            })
            if usuario_data:
                return Usuario.from_dict(usuario_data)
            return None
        except Exception as e:
            raise Exception(f"Error buscando usuario inactivo por teléfono global: {str(e)}")
    
    def validate_unique_global_fields(self, cedula, telefono, exclude_id=None):
        """Valida que cédula y teléfono sean únicos globalmente"""
        errors = []
        
        # Validar cédula
        if cedula:
            existing_cedula = self.find_by_cedula_global(cedula, exclude_id)
            if existing_cedula:
                errors.append(f"La cédula {cedula} ya está en uso por otro usuario")
        
        # Validar teléfono
        if telefono:
            existing_telefono = self.find_by_telefono_global(telefono, exclude_id)
            if existing_telefono:
                errors.append(f"El teléfono {telefono} ya está en uso por otro usuario")
        
        return errors
    
    def count_all(self):
        """Cuenta todos los usuarios (activos e inactivos)"""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            raise Exception(f"Error contando todos los usuarios: {str(e)}")
    
    def count_active(self):
        """Cuenta todos los usuarios activos"""
        try:
            return self.collection.count_documents({"activo": True})
        except Exception as e:
            raise Exception(f"Error contando usuarios activos: {str(e)}")
