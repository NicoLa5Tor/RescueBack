"""
Script para debuggear problemas de autenticación
Ejecutar: python debug_auth_issues.py
"""

import bcrypt
from database import Database
from models.administrador import Administrador
from repositories.auth_repository import AuthRepository
from services.auth_service import AuthService

def test_password_hash():
    """Prueba si el hash de contraseña funciona correctamente"""
    print("🔐 Probando hash de contraseña...")
    
    password = "admin123"
    stored_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdVAT5iOnE.ZdaC"
    
    # Verificar si el hash coincide
    is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    print(f"Password: {password}")
    print(f"Hash stored: {stored_hash}")
    print(f"Hash válido: {is_valid}")
    
    if not is_valid:
        print("❌ El hash no coincide con la contraseña")
        # Generar un nuevo hash
        new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(f"Nuevo hash generado: {new_hash}")
    else:
        print("✅ El hash es válido")
    
    return is_valid

def test_database_connection():
    """Prueba la conexión a la base de datos"""
    print("\n📊 Probando conexión a base de datos...")
    
    try:
        db = Database()
        database = db.get_database()
        
        # Buscar el administrador directamente
        admin_data = database.administradores.find_one({"usuario": "superadmin"})
        
        if admin_data:
            print("✅ Administrador encontrado en la base de datos")
            print(f"Usuario: {admin_data.get('usuario')}")
            print(f"Email: {admin_data.get('email')}")
            print(f"Activo: {admin_data.get('activo')}")
            print(f"Hash en DB: {admin_data.get('password_hash')}")
            return admin_data
        else:
            print("❌ No se encontró el administrador en la base de datos")
            return None
            
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def test_auth_repository():
    """Prueba el repositorio de autenticación"""
    print("\n🔍 Probando AuthRepository...")
    
    try:
        auth_repo = AuthRepository()
        
        # Buscar por usuario
        admin = auth_repo.find_admin_by_usuario("superadmin")
        if admin:
            print("✅ AuthRepository encontró el administrador por usuario")
            print(f"Admin encontrado: {admin.usuario}")
            
            # Probar verificación de contraseña
            password_valid = admin.verify_password("admin123")
            print(f"Verificación de contraseña: {password_valid}")
            
            return admin
        else:
            print("❌ AuthRepository no encontró el administrador")
            return None
            
    except Exception as e:
        print(f"❌ Error en AuthRepository: {e}")
        return None

def test_auth_service():
    """Prueba el servicio de autenticación"""
    print("\n🔧 Probando AuthService...")
    
    try:
        auth_service = AuthService()
        
        # Intentar login
        result = auth_service.login("superadmin", "admin123")
        
        print(f"Resultado del login: {result}")
        
        if result['success']:
            print("✅ AuthService login exitoso")
        else:
            print(f"❌ AuthService login falló: {result.get('errors', [])}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error en AuthService: {e}")
        return None

def fix_password_hash():
    """Actualiza el hash de contraseña en la base de datos"""
    print("\n🛠️ Actualizando hash de contraseña...")
    
    try:
        password = "admin123"
        new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        db = Database()
        database = db.get_database()
        
        result = database.administradores.update_one(
            {"usuario": "superadmin"},
            {"$set": {"password_hash": new_hash}}
        )
        
        if result.modified_count > 0:
            print(f"✅ Hash actualizado exitosamente: {new_hash}")
            return True
        else:
            print("❌ No se pudo actualizar el hash")
            return False
            
    except Exception as e:
        print(f"❌ Error actualizando hash: {e}")
        return False

def main():
    """Función principal de debugging"""
    print("🚀 INICIANDO DEBUGGING DE AUTENTICACIÓN\n")
    
    # 1. Probar hash de contraseña
    hash_valid = test_password_hash()
    
    # 2. Probar conexión a base de datos
    admin_data = test_database_connection()
    
    # 3. Probar repositorio
    admin_repo = test_auth_repository()
    
    # 4. Probar servicio
    auth_result = test_auth_service()
    
    print("\n" + "="*50)
    print("📋 RESUMEN:")
    print(f"Hash válido: {'✅' if hash_valid else '❌'}")
    print(f"Admin en DB: {'✅' if admin_data else '❌'}")
    print(f"AuthRepo OK: {'✅' if admin_repo else '❌'}")
    print(f"AuthService OK: {'✅' if auth_result and auth_result.get('success') else '❌'}")
    
    # Si el hash no es válido, ofrecer arreglarlo
    if not hash_valid:
        response = input("\n¿Quieres actualizar el hash de contraseña? (y/n): ")
        if response.lower() == 'y':
            fix_password_hash()
            print("Hash actualizado. Ejecuta el script de nuevo para verificar.")

if __name__ == "__main__":
    main()