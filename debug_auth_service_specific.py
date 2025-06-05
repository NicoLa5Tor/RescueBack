"""
Debug específico para AuthService
"""

from services.auth_service import AuthService
from repositories.auth_repository import AuthRepository

def debug_auth_service_step_by_step():
    """Debug paso a paso del AuthService"""
    print("🔧 DEBUGGING AuthService paso a paso...")
    
    try:
        auth_service = AuthService()
        
        print("\n1. Probando _authenticate_admin directamente...")
        
        # Llamar directamente al método privado para ver qué pasa
        admin_result = auth_service._authenticate_admin("superadmin", "admin123")
        print(f"Resultado _authenticate_admin: {admin_result}")
        
        if not admin_result.get('success'):
            print("❌ Falló en _authenticate_admin")
            
            # Vamos más profundo
            print("\n2. Debugging dentro de _authenticate_admin...")
            
            auth_repo = AuthRepository()
            admin = auth_repo.find_admin_by_usuario("superadmin")
            
            if admin:
                print(f"✅ Admin encontrado: {admin.usuario}")
                print(f"Hash en admin object: {admin.password_hash}")
                
                # Probar verificación de contraseña directamente
                password_check = admin.verify_password("admin123")
                print(f"Verificación directa de contraseña: {password_check}")
                
                if not password_check:
                    print("❌ La verificación de contraseña está fallando")
                    
                    # Verificar si el método verify_password está funcionando
                    import bcrypt
                    manual_check = bcrypt.checkpw("admin123".encode('utf-8'), admin.password_hash.encode('utf-8'))
                    print(f"Verificación manual con bcrypt: {manual_check}")
                    
                else:
                    print("✅ Verificación de contraseña OK")
                    print("El problema debe estar en otra parte del _authenticate_admin")
            else:
                print("❌ No se encontró el admin")
        else:
            print("✅ _authenticate_admin funcionó")
        
        print("\n3. Probando login completo...")
        login_result = auth_service.login("superadmin", "admin123")
        print(f"Resultado login completo: {login_result}")
        
    except Exception as e:
        print(f"❌ Error en debug: {e}")
        import traceback
        traceback.print_exc()

def test_direct_curl():
    """Test directo del endpoint"""
    print("\n🌐 Probando endpoint directamente...")
    
    import requests
    
    try:
        response = requests.post("http://localhost:5000/auth/login", 
                               json={"usuario": "superadmin", "password": "admin123"})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error haciendo request: {e}")

if __name__ == "__main__":
    debug_auth_service_step_by_step()
    test_direct_curl()