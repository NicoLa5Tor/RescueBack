#!/usr/bin/env python3
"""
Script para crear un usuario super administrador por defecto
"""
import sys
import os
import bcrypt
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio padre al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import Database

def crear_super_admin():
    """Crea el usuario super administrador por defecto"""
    
    # Conectar a la base de datos
    db = Database().get_database()
    
    # Datos del super admin por defecto
    username = os.getenv('ADMIN_USERNAME', 'superadmin')
    email = os.getenv('ADMIN_EMAIL', 'admin@sistema.com')
    password = os.getenv('ADMIN_PASSWORD')
    
    # Validar que la contraseña esté configurada
    if not password:
        print("❌ Error: ADMIN_PASSWORD no está configurada en el archivo .env")
        print("💡 Agrega la línea: ADMIN_PASSWORD=tu_contraseña_segura")
        return False
    
    # Verificar si ya existe
    existing_admin = db.administradores.find_one({
        '$or': [
            {'username': username},
            {'email': email},
            {'usuario': username}
        ]
    })
    
    if existing_admin:
        print(f"❌ Usuario '{username}' ya existe. No se creará duplicado.")
        return False
    
    # Hash de la contraseña
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Crear el documento del administrador
    admin_doc = {
        '_id': ObjectId(),
        'username': username,
        'usuario': username,  # Alias para compatibilidad
        'email': email,
        'password_hash': password_hash,
        'role': 'super_admin',
        'rol': 'super_admin',  # Alias para compatibilidad
        'activo': True,
        'is_active': True,
        'permisos': [
            '/api/users',
            '/api/empresas', 
            '/api/admin',
            '/empresas',
            '/api/hardware',
            '/api/hardware-types',
            '/api/dashboard',
            '/api/tipos-empresa'
        ],
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'last_login': None
    }
    
    try:
        # Insertar en la base de datos
        result = db.administradores.insert_one(admin_doc)
        
        if result.inserted_id:
            print("✅ Usuario super administrador creado exitosamente!")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
            print(f"   ID: {result.inserted_id}")
            print("⚠️  IMPORTANTE: Cambia la contraseña después del primer login!")
            return True
        else:
            print("❌ Error: No se pudo insertar el usuario")
            return False
            
    except Exception as e:
        print(f"❌ Error al crear el usuario administrador: {str(e)}")
        return False

def verificar_admin():
    """Verifica si existe al menos un administrador"""
    db = Database().get_database()
    
    count = db.administradores.count_documents({'activo': True})
    print(f"📊 Administradores activos en la base de datos: {count}")
    
    if count > 0:
        admins = db.administradores.find({'activo': True}, {'username': 1, 'email': 1, 'role': 1})
        print("👥 Administradores existentes:")
        for admin in admins:
            print(f"   - {admin.get('username', 'N/A')} ({admin.get('email', 'N/A')}) - {admin.get('role', 'N/A')}")
    
    return count > 0

if __name__ == "__main__":
    print("🔧 Inicializando usuario administrador...")
    print("=" * 50)
    
    try:
        # Verificar conexión a la base de datos
        db = Database()
        if not db.test_connection():
            print("❌ Error: No se pudo conectar a MongoDB")
            print("💡 Verifica que MongoDB esté corriendo y las variables de entorno estén configuradas")
            sys.exit(1)
        
        print("✅ Conexión a MongoDB exitosa")
        
        # Verificar administradores existentes
        if verificar_admin():
            print("\n¿Deseas crear otro administrador? (y/N): ", end="")
            respuesta = input().strip().lower()
            if respuesta not in ['y', 'yes', 'sí', 'si']:
                print("👋 Saliendo sin cambios...")
                sys.exit(0)
        
        # Crear super admin
        print("\n🚀 Creando super administrador...")
        if crear_super_admin():
            print("\n🎉 Proceso completado exitosamente!")
            print("\nPuedes hacer login con:")
            print(f"  Usuario: {os.getenv('ADMIN_USERNAME', 'superadmin')}")
            print(f"  Contraseña: [configurada en .env]")
        else:
            print("\n❌ Error en la creación del administrador")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
        sys.exit(1)
