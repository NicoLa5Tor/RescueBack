from pymongo import MongoClient
from bson import ObjectId
from models.tipo_empresa import TipoEmpresa
from database import Database

class TipoEmpresaRepository:
    def __init__(self):
        db_instance = Database()
        self.db = db_instance.get_database()
        self.collection = self.db.tipos_empresa
    
    def create(self, tipo_empresa):
        """Crea un nuevo tipo de empresa"""
        try:
            # Normalizar datos antes de guardar
            tipo_empresa.normalize_data()
            
            # Validar datos
            errors = tipo_empresa.validate()
            if errors:
                return {"success": False, "errors": errors}
            
            # Verificar si ya existe un tipo con el mismo nombre
            existing = self.collection.find_one({"nombre": tipo_empresa.nombre, "activo": True})
            if existing:
                return {"success": False, "errors": ["Ya existe un tipo de empresa con este nombre"]}
            
            # Insertar en la base de datos
            result = self.collection.insert_one(tipo_empresa.to_dict())
            
            if result.inserted_id:
                tipo_empresa._id = result.inserted_id
                return {"success": True, "data": tipo_empresa.to_json()}
            else:
                return {"success": False, "errors": ["Error al crear el tipo de empresa"]}
                
        except Exception as e:
            return {"success": False, "errors": [f"Error interno: {str(e)}"]}
    
    def get_by_id(self, tipo_empresa_id):
        """Obtiene un tipo de empresa por su ID"""
        try:
            if not ObjectId.is_valid(tipo_empresa_id):
                return {"success": False, "errors": ["ID de tipo de empresa inválido"]}
            
            data = self.collection.find_one({"_id": ObjectId(tipo_empresa_id), "activo": True})
            
            if data:
                tipo_empresa = TipoEmpresa.from_dict(data)
                return {"success": True, "data": tipo_empresa.to_json()}
            else:
                return {"success": False, "errors": ["Tipo de empresa no encontrado"]}
                
        except Exception as e:
            return {"success": False, "errors": [f"Error interno: {str(e)}"]}
    
    def get_all(self, skip=0, limit=100):
        """Obtiene todos los tipos de empresa activos con conteo de empresas"""
        try:
            cursor = self.collection.find({"activo": True}).skip(skip).limit(limit).sort("nombre", 1)
            tipos_empresa = []
            
            # Obtener collection de empresas para contar
            empresas_collection = self.db.empresas
            
            for data in cursor:
                tipo_empresa = TipoEmpresa.from_dict(data)
                tipo_json = tipo_empresa.to_json()
                
                # Agregar conteo de empresas asociadas
                empresas_count = empresas_collection.count_documents({
                    "tipo_empresa_id": data.get('_id'),
                    "activa": True
                })
                tipo_json['empresas_count'] = empresas_count
                
                tipos_empresa.append(tipo_json)
            
            # Contar total de documentos
            total = self.collection.count_documents({"activo": True})
            
            return {
                "success": True,
                "data": tipos_empresa,
                "total": total,
                "skip": skip,
                "limit": limit,
                "count": len(tipos_empresa)
            }
            
        except Exception as e:
            return {"success": False, "errors": [f"Error interno: {str(e)}"]}
    
    def update(self, tipo_empresa_id, update_data):
        """Actualiza un tipo de empresa"""
        try:
            if not ObjectId.is_valid(tipo_empresa_id):
                return {"success": False, "errors": ["ID de tipo de empresa inválido"]}
            
            # Obtener el tipo de empresa actual
            current_data = self.collection.find_one({"_id": ObjectId(tipo_empresa_id), "activo": True})
            if not current_data:
                return {"success": False, "errors": ["Tipo de empresa no encontrado"]}
            
            # Crear objeto temporal para validación
            temp_tipo = TipoEmpresa.from_dict(current_data)
            
            # Actualizar campos
            if 'nombre' in update_data:
                temp_tipo.nombre = update_data['nombre']
            if 'descripcion' in update_data:
                temp_tipo.descripcion = update_data['descripcion']
            if 'caracteristicas' in update_data:
                temp_tipo.caracteristicas = update_data['caracteristicas']
            if 'activo' in update_data:
                temp_tipo.activo = update_data['activo']
            
            # Normalizar y validar
            temp_tipo.normalize_data()
            errors = temp_tipo.validate()
            if errors:
                return {"success": False, "errors": errors}
            
            # Verificar nombre único (excepto el actual)
            if 'nombre' in update_data:
                existing = self.collection.find_one({
                    "nombre": temp_tipo.nombre,
                    "activo": True,
                    "_id": {"$ne": ObjectId(tipo_empresa_id)}
                })
                if existing:
                    return {"success": False, "errors": ["Ya existe un tipo de empresa con este nombre"]}
            
            # Actualizar timestamp
            temp_tipo.update_timestamp()
            
            # Actualizar en la base de datos
            result = self.collection.update_one(
                {"_id": ObjectId(tipo_empresa_id), "activo": True},
                {"$set": temp_tipo.to_dict()}
            )
            
            if result.modified_count > 0:
                return {"success": True, "data": temp_tipo.to_json()}
            else:
                return {"success": False, "errors": ["No se pudo actualizar el tipo de empresa"]}
                
        except Exception as e:
            return {"success": False, "errors": [f"Error interno: {str(e)}"]}
    
    def delete(self, tipo_empresa_id):
        """Elimina lógicamente un tipo de empresa"""
        try:
            if not ObjectId.is_valid(tipo_empresa_id):
                return {"success": False, "errors": ["ID de tipo de empresa inválido"]}
            
            # Verificar si existe
            existing = self.collection.find_one({"_id": ObjectId(tipo_empresa_id), "activo": True})
            if not existing:
                return {"success": False, "errors": ["Tipo de empresa no encontrado"]}
            
            # Soft delete
            from datetime import datetime
            result = self.collection.update_one(
                {"_id": ObjectId(tipo_empresa_id)},
                {"$set": {"activo": False, "fecha_actualizacion": datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                return {"success": True, "message": "Tipo de empresa eliminado correctamente"}
            else:
                return {"success": False, "errors": ["No se pudo eliminar el tipo de empresa"]}
                
        except Exception as e:
            return {"success": False, "errors": [f"Error interno: {str(e)}"]}
    
    def search(self, query, skip=0, limit=100):
        """Busca tipos de empresa por nombre o descripción"""
        try:
            search_filter = {
                "activo": True,
                "$or": [
                    {"nombre": {"$regex": query, "$options": "i"}},
                    {"descripcion": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = self.collection.find(search_filter).skip(skip).limit(limit).sort("nombre", 1)
            tipos_empresa = []
            
            for data in cursor:
                tipo_empresa = TipoEmpresa.from_dict(data)
                tipos_empresa.append(tipo_empresa.to_json())
            
            # Contar total de documentos que coinciden
            total = self.collection.count_documents(search_filter)
            
            return {
                "success": True,
                "data": tipos_empresa,
                "total": total,
                "skip": skip,
                "limit": limit,
                "query": query
            }
            
        except Exception as e:
            return {"success": False, "errors": [f"Error interno: {str(e)}"]}
    
    def get_by_nombre(self, nombre):
        """Obtiene un tipo de empresa por su nombre"""
        try:
            data = self.collection.find_one({"nombre": nombre, "activo": True})
            
            if data:
                tipo_empresa = TipoEmpresa.from_dict(data)
                return {"success": True, "data": tipo_empresa.to_json()}
            else:
                return {"success": False, "errors": ["Tipo de empresa no encontrado"]}
                
        except Exception as e:
            return {"success": False, "errors": [f"Error interno: {str(e)}"]}
    
    def get_estadisticas(self):
        """Obtiene estadísticas de tipos de empresa incluyendo promedio de características y conteo de empresas"""
        try:
            # Obtener todos los tipos activos
            tipos = list(self.collection.find({"activo": True}))
            
            # Obtener collection de empresas para contar
            empresas_collection = self.db.empresas
            
            total_tipos = len(tipos)
            tipos_activos = len(tipos)
            tipos_con_caracteristicas = 0
            total_caracteristicas = 0
            total_empresas = 0
            caracteristicas_por_tipo = []
            
            for tipo in tipos:
                caracteristicas = tipo.get('caracteristicas', [])
                num_caracteristicas = len(caracteristicas)
                
                if num_caracteristicas > 0:
                    tipos_con_caracteristicas += 1
                
                total_caracteristicas += num_caracteristicas
                
                # Contar empresas asociadas a este tipo
                empresas_count = empresas_collection.count_documents({
                    "tipo_empresa_id": tipo.get('_id'),
                    "activa": True
                })
                total_empresas += empresas_count
                
                caracteristicas_por_tipo.append({
                    'nombre': tipo.get('nombre'),
                    'cantidad_caracteristicas': num_caracteristicas,
                    'caracteristicas': caracteristicas,
                    'empresas_count': empresas_count
                })
            
            # Incluir tipos inactivos para estadísticas completas
            tipos_inactivos = self.collection.count_documents({"activo": False})
            total_tipos_completo = tipos_activos + tipos_inactivos
            
            # Calcular promedios
            promedio_caracteristicas_total = total_caracteristicas / total_tipos if total_tipos > 0 else 0
            promedio_caracteristicas_con_datos = total_caracteristicas / tipos_con_caracteristicas if tipos_con_caracteristicas > 0 else 0
            promedio_empresas_por_tipo = total_empresas / total_tipos if total_tipos > 0 else 0
            
            # Estadísticas adicionales
            max_caracteristicas = max([len(t.get('caracteristicas', [])) for t in tipos]) if tipos else 0
            min_caracteristicas = min([len(t.get('caracteristicas', [])) for t in tipos]) if tipos else 0
            
            return {
                "success": True,
                "data": {
                    "total_types": tipos_activos,
                    "active_types": tipos_activos,
                    "inactive_types": tipos_inactivos,
                    "total_companies": total_empresas,
                    "avg_companies_per_type": round(promedio_empresas_por_tipo, 1),
                    "tipos_con_caracteristicas": tipos_con_caracteristicas,
                    "tipos_sin_caracteristicas": total_tipos - tipos_con_caracteristicas,
                    "total_caracteristicas": total_caracteristicas,
                    "promedio_caracteristicas_total": round(promedio_caracteristicas_total, 2),
                    "promedio_caracteristicas_con_datos": round(promedio_caracteristicas_con_datos, 2),
                    "max_caracteristicas": max_caracteristicas,
                    "min_caracteristicas": min_caracteristicas,
                    "detalle_por_tipo": caracteristicas_por_tipo
                }
            }
            
        except Exception as e:
            return {"success": False, "errors": [f"Error interno: {str(e)}"]}
    
    def toggle_status(self, tipo_empresa_id):
        """Cambia el estado activo/inactivo de un tipo de empresa"""
        try:
            if not ObjectId.is_valid(tipo_empresa_id):
                return {"success": False, "errors": ["ID de tipo de empresa inválido"]}
            
            # Obtener el tipo actual
            current_data = self.collection.find_one({"_id": ObjectId(tipo_empresa_id)})
            if not current_data:
                return {"success": False, "errors": ["Tipo de empresa no encontrado"]}
            
            # Cambiar el estado
            new_status = not current_data.get('activo', True)
            
            # Actualizar en la base de datos
            from datetime import datetime
            result = self.collection.update_one(
                {"_id": ObjectId(tipo_empresa_id)},
                {
                    "$set": {
                        "activo": new_status,
                        "fecha_actualizacion": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                # Obtener el tipo actualizado para la respuesta
                updated_data = self.collection.find_one({"_id": ObjectId(tipo_empresa_id)})
                tipo_empresa = TipoEmpresa.from_dict(updated_data)
                
                action = "activado" if new_status else "desactivado"
                return {
                    "success": True, 
                    "message": f"Tipo de empresa {action} correctamente",
                    "data": tipo_empresa.to_json()
                }
            else:
                return {"success": False, "errors": ["No se pudo cambiar el estado del tipo de empresa"]}
                
        except Exception as e:
            return {"success": False, "errors": [f"Error interno: {str(e)}"]}
    
    def get_all_including_inactive(self, skip=0, limit=100):
        """Obtiene todos los tipos de empresa incluyendo inactivos con conteo de empresas"""
        try:
            cursor = self.collection.find({}).skip(skip).limit(limit).sort("nombre", 1)
            tipos_empresa = []
            
            # Obtener collection de empresas para contar
            empresas_collection = self.db.empresas
            
            for data in cursor:
                tipo_empresa = TipoEmpresa.from_dict(data)
                tipo_json = tipo_empresa.to_json()
                
                # Agregar conteo de empresas asociadas
                empresas_count = empresas_collection.count_documents({
                    "tipo_empresa_id": data.get('_id'),
                    "activa": True
                })
                tipo_json['empresas_count'] = empresas_count
                
                tipos_empresa.append(tipo_json)
            
            # Contar total de documentos (incluyendo inactivos)
            total = self.collection.count_documents({})
            
            return {
                "success": True,
                "data": tipos_empresa,
                "total": total,
                "skip": skip,
                "limit": limit,
                "count": len(tipos_empresa)
            }
            
        except Exception as e:
            return {"success": False, "errors": [f"Error interno: {str(e)}"]}
    
    def get_promedio_empresas_por_tipo(self):
        """Obtiene el promedio de empresas por tipo de empresa"""
        try:
            # Obtener todos los tipos activos
            tipos_activos = list(self.collection.find({"activo": True}))
            
            if not tipos_activos:
                return {
                    "success": True,
                    "data": {
                        "promedio": 0,
                        "total_tipos": 0,
                        "total_empresas": 0,
                        "mensaje": "No hay tipos de empresa activos"
                    }
                }
            
            # Obtener collection de empresas
            empresas_collection = self.db.empresas
            
            total_empresas = 0
            tipos_con_empresas = 0
            detalle_por_tipo = []
            
            for tipo in tipos_activos:
                # Contar empresas activas para este tipo
                empresas_count = empresas_collection.count_documents({
                    "tipo_empresa_id": tipo.get('_id'),
                    "activa": True
                })
                
                total_empresas += empresas_count
                
                if empresas_count > 0:
                    tipos_con_empresas += 1
                
                detalle_por_tipo.append({
                    "tipo_id": str(tipo.get('_id')),
                    "tipo_nombre": tipo.get('nombre'),
                    "empresas_count": empresas_count
                })
            
            # Calcular promedio
            promedio = total_empresas / len(tipos_activos) if len(tipos_activos) > 0 else 0
            promedio_solo_con_empresas = total_empresas / tipos_con_empresas if tipos_con_empresas > 0 else 0
            
            return {
                "success": True,
                "data": {
                    "promedio": round(promedio, 2),
                    "promedio_solo_con_empresas": round(promedio_solo_con_empresas, 2),
                    "total_tipos_activos": len(tipos_activos),
                    "tipos_con_empresas": tipos_con_empresas,
                    "tipos_sin_empresas": len(tipos_activos) - tipos_con_empresas,
                    "total_empresas": total_empresas,
                    "detalle_por_tipo": detalle_por_tipo
                }
            }
            
        except Exception as e:
            return {"success": False, "errors": [f"Error interno: {str(e)}"]}
    
    def get_total_empresas_categorizadas(self):
        """Obtiene el total de empresas que tienen tipo asignado"""
        try:
            # Obtener collection de empresas
            empresas_collection = self.db.empresas
            
            # Contar empresas activas con tipo asignado
            empresas_con_tipo = empresas_collection.count_documents({
                "activa": True,
                "tipo_empresa_id": {"$exists": True, "$ne": None}
            })
            
            # Contar empresas activas sin tipo asignado
            empresas_sin_tipo = empresas_collection.count_documents({
                "activa": True,
                "$or": [
                    {"tipo_empresa_id": {"$exists": False}},
                    {"tipo_empresa_id": None}
                ]
            })
            
            # Total de empresas activas
            total_empresas_activas = empresas_collection.count_documents({"activa": True})
            
            # Calcular porcentaje de categorización
            porcentaje_categorizadas = (empresas_con_tipo / total_empresas_activas * 100) if total_empresas_activas > 0 else 0
            
            # Obtener distribución por tipo
            pipeline = [
                {
                    "$match": {
                        "activa": True,
                        "tipo_empresa_id": {"$exists": True, "$ne": None}
                    }
                },
                {
                    "$group": {
                        "_id": "$tipo_empresa_id",
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$sort": {"count": -1}
                }
            ]
            
            distribucion_raw = list(empresas_collection.aggregate(pipeline))
            
            # Enriquecer con nombres de tipos
            distribucion_detallada = []
            for item in distribucion_raw:
                tipo_info = self.collection.find_one({"_id": item["_id"], "activo": True})
                if tipo_info:
                    distribucion_detallada.append({
                        "tipo_id": str(item["_id"]),
                        "tipo_nombre": tipo_info.get("nombre", "Tipo no encontrado"),
                        "empresas_count": item["count"]
                    })
            
            return {
                "success": True,
                "data": {
                    "total_categorizadas": empresas_con_tipo,
                    "total_sin_categorizar": empresas_sin_tipo,
                    "total_empresas_activas": total_empresas_activas,
                    "porcentaje_categorizadas": round(porcentaje_categorizadas, 1),
                    "distribucion_por_tipo": distribucion_detallada
                }
            }
            
        except Exception as e:
            return {"success": False, "errors": [f"Error interno: {str(e)}"]}
