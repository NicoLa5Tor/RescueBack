#!/usr/bin/env python3
"""
Script para migrar datos existentes agregando el campo direccion_open_maps
a todos los registros de hardware que tengan una dirección.
"""

import sys
import os
from pymongo import MongoClient
from utils.maps_utils import direccion_openstreetmap

# Configuración de la base de datos
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'hardware_db')

def migrate_direccion_open_maps():
    """
    Migra los datos existentes para agregar el campo direccion_open_maps
    """
    try:
        # Conectar a la base de datos
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        hardware_collection = db['hardware']
        
        print("🔄 Iniciando migración de direccion_open_maps...")
        
        # Buscar todos los registros de hardware que tengan dirección pero no direccion_open_maps
        query = {
            'direccion': {'$exists': True, '$ne': None, '$ne': ''},
            'direccion_open_maps': {'$exists': False}
        }
        
        hardware_list = list(hardware_collection.find(query))
        
        if not hardware_list:
            print("✅ No se encontraron registros que necesiten migración.")
            return True
        
        print(f"📊 Se encontraron {len(hardware_list)} registros para migrar.")
        
        updated_count = 0
        error_count = 0
        
        for hardware in hardware_list:
            try:
                hardware_id = hardware['_id']
                direccion = hardware['direccion']
                
                # Generar la URL de OpenStreetMap
                direccion_open_maps = direccion_openstreetmap(direccion)
                
                # Actualizar el registro
                result = hardware_collection.update_one(
                    {'_id': hardware_id},
                    {'$set': {'direccion_open_maps': direccion_open_maps}}
                )
                
                if result.modified_count > 0:
                    updated_count += 1
                    print(f"✅ Migrado hardware: {hardware.get('nombre', 'Sin nombre')} - {direccion}")
                else:
                    error_count += 1
                    print(f"❌ Error al migrar hardware: {hardware.get('nombre', 'Sin nombre')}")
                    
            except Exception as e:
                error_count += 1
                print(f"💥 Error procesando hardware {hardware.get('nombre', 'Sin nombre')}: {str(e)}")
        
        print(f"\n📊 Migración completada:")
        print(f"✅ Registros migrados exitosamente: {updated_count}")
        print(f"❌ Registros con error: {error_count}")
        print(f"📈 Total procesados: {updated_count + error_count}")
        
        # Cerrar la conexión
        client.close()
        
    except Exception as e:
        print(f"💥 Error en la migración: {str(e)}")
        return False
    
    return True

def verify_migration():
    """
    Verifica que la migración se haya completado correctamente
    """
    try:
        # Conectar a la base de datos
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        hardware_collection = db['hardware']
        
        print("\n🔍 Verificando migración...")
        
        # Contar registros con dirección
        total_with_direccion = hardware_collection.count_documents({
            'direccion': {'$exists': True, '$ne': None, '$ne': ''}
        })
        
        # Contar registros con direccion_open_maps
        total_with_open_maps = hardware_collection.count_documents({
            'direccion_open_maps': {'$exists': True, '$ne': None, '$ne': ''}
        })
        
        print(f"📊 Registros con dirección: {total_with_direccion}")
        print(f"📊 Registros con direccion_open_maps: {total_with_open_maps}")
        
        if total_with_direccion == total_with_open_maps:
            print("✅ Migración verificada correctamente - todos los registros tienen ambos campos.")
        else:
            print("⚠️ Discrepancia encontrada - algunos registros pueden necesitar migración adicional.")
            
            # Mostrar algunos ejemplos de registros que faltan
            missing_open_maps = list(hardware_collection.find({
                'direccion': {'$exists': True, '$ne': None, '$ne': ''},
                'direccion_open_maps': {'$exists': False}
            }).limit(3))
            
            if missing_open_maps:
                print(f"\n📝 Ejemplos de registros que faltan migrar:")
                for hw in missing_open_maps:
                    print(f"  - {hw.get('nombre', 'Sin nombre')}: {hw.get('direccion', 'Sin dirección')}")
        
        # Cerrar la conexión
        client.close()
        
    except Exception as e:
        print(f"💥 Error en la verificación: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando migración de direccion_open_maps...")
    
    # Ejecutar migración
    success = migrate_direccion_open_maps()
    
    if success:
        # Verificar migración
        verify_migration()
        print("\n🎉 Migración completada exitosamente!")
    else:
        print("\n❌ La migración falló. Por favor revisa los errores.")
        sys.exit(1)
