"""
Script completo para testing de todos los endpoints de la API
Incluye pruebas para usuarios y empresas con casos de éxito y error
"""

import requests
import json
import time
from datetime import datetime

class APITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json"
        }
        self.created_ids = {"users": [], "empresas": []}
        
    def print_separator(self, title):
        """Imprime un separador visual"""
        print("\n" + "="*60)
        print(f"🧪 {title}")
        print("="*60)
    
    def print_test(self, test_name):
        """Imprime el nombre del test"""
        print(f"\n🔍 {test_name}")
        print("-" * 40)
    
    def make_request(self, method, endpoint, data=None, params=None, use_auth=False):
        """Hace una petición HTTP y maneja errores"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers if use_auth else {"Content-Type": "application/json"}
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            print(f"Status: {response.status_code}")
            
            try:
                json_response = response.json()
                print(f"Response: {json.dumps(json_response, indent=2, ensure_ascii=False)}")
                return response.status_code, json_response
            except:
                print(f"Response (text): {response.text}")
                return response.status_code, response.text
                
        except requests.exceptions.ConnectionError:
            print("❌ Error: No se pudo conectar al servidor")
            return None, None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None, None

    def test_health_endpoints(self):
        """Prueba los endpoints de salud"""
        self.print_separator("ENDPOINTS DE SALUD")
        
        self.print_test("Health Check")
        self.make_request("GET", "/health")
        
        self.print_test("Endpoint raíz")
        self.make_request("GET", "/")

    def test_user_endpoints(self):
        """Prueba todos los endpoints de usuarios"""
        self.print_separator("ENDPOINTS DE USUARIOS")
        
        # 1. Crear usuario válido
        self.print_test("Crear usuario válido")
        user_data = {
            "name": "Juan Pérez",
            "email": f"juan.perez.{int(time.time())}@email.com",
            "age": 30
        }
        status, response = self.make_request("POST", "/api/users", data=user_data)
        if status == 201 and response.get('success'):
            user_id = response['data']['_id']
            self.created_ids["users"].append(user_id)
            print(f"✅ Usuario creado con ID: {user_id}")
        
        # 2. Crear usuario con datos inválidos
        self.print_test("Crear usuario con datos inválidos")
        invalid_user = {
            "name": "",
            "email": "email-invalido",
            "age": -5
        }
        self.make_request("POST", "/api/users", data=invalid_user)
        
        # 3. Crear usuario con email duplicado
        self.print_test("Crear usuario con email duplicado")
        duplicate_user = {
            "name": "María González",
            "email": user_data["email"],  # Email duplicado
            "age": 25
        }
        self.make_request("POST", "/api/users", data=duplicate_user)
        
        # 4. Obtener todos los usuarios
        self.print_test("Obtener todos los usuarios")
        self.make_request("GET", "/api/users")
        
        # 5. Obtener usuario por ID (si se creó uno)
        if self.created_ids["users"]:
            user_id = self.created_ids["users"][0]
            self.print_test(f"Obtener usuario por ID: {user_id}")
            self.make_request("GET", f"/api/users/{user_id}")
            
            # 6. Actualizar usuario
            self.print_test("Actualizar usuario")
            update_data = {
                "name": "Juan Pérez Actualizado",
                "age": 31
            }
            self.make_request("PUT", f"/api/users/{user_id}", data=update_data)
        
        # 7. Obtener usuario inexistente
        self.print_test("Obtener usuario inexistente")
        fake_id = "507f1f77bcf86cd799439999"
        self.make_request("GET", f"/api/users/{fake_id}")
        
        # 8. Buscar usuarios por rango de edad
        self.print_test("Buscar usuarios por edad")
        self.make_request("GET", "/api/users/age-range", params={"min_age": 25, "max_age": 35})
        
        # 9. Buscar con parámetros inválidos
        self.print_test("Buscar con parámetros de edad inválidos")
        self.make_request("GET", "/api/users/age-range", params={"min_age": "abc", "max_age": "xyz"})

    def test_empresa_endpoints(self):
        """Prueba todos los endpoints de empresas"""
        self.print_separator("ENDPOINTS DE EMPRESAS")
        
        # 1. Crear empresa válida (con auth)
        self.print_test("Crear empresa válida")
        empresa_data = {
            "nombre": f"TechCorp {int(time.time())}",
            "descripcion": "Empresa de desarrollo de software y consultoría tecnológica especializada en soluciones empresariales innovadoras",
            "ubicacion": "Bogotá, Colombia"
        }
        status, response = self.make_request("POST", "/api/empresas", data=empresa_data, use_auth=True)
        if status == 201 and response.get('success'):
            empresa_id = response['data']['_id']
            self.created_ids["empresas"].append(empresa_id)
            print(f"✅ Empresa creada con ID: {empresa_id}")
        
        # 2. Crear empresa sin autenticación
        self.print_test("Crear empresa sin autenticación")
        self.make_request("POST", "/api/empresas", data=empresa_data)
        
        # 3. Crear empresa con datos inválidos
        self.print_test("Crear empresa con datos inválidos")
        invalid_empresa = {
            "nombre": "",
            "descripcion": "Muy corta",
            "ubicacion": "X"
        }
        self.make_request("POST", "/api/empresas", data=invalid_empresa, use_auth=True)
        
        # 4. Crear empresa con nombre duplicado
        self.print_test("Crear empresa con nombre duplicado")
        duplicate_empresa = {
            "nombre": empresa_data["nombre"],
            "descripcion": "Otra descripción para empresa con nombre duplicado",
            "ubicacion": "Medellín, Colombia"
        }
        self.make_request("POST", "/api/empresas", data=duplicate_empresa, use_auth=True)
        
        # 5. Obtener todas las empresas
        self.print_test("Obtener todas las empresas")
        self.make_request("GET", "/api/empresas")
        
        # 6. Obtener todas las empresas incluyendo inactivas (con auth)
        self.print_test("Obtener empresas incluyendo inactivas")
        self.make_request("GET", "/api/empresas", params={"include_inactive": "true"}, use_auth=True)
        
        # 7. Obtener empresa por ID (si se creó una)
        if self.created_ids["empresas"]:
            empresa_id = self.created_ids["empresas"][0]
            self.print_test(f"Obtener empresa por ID: {empresa_id}")
            self.make_request("GET", f"/api/empresas/{empresa_id}")
            
            # 8. Actualizar empresa
            self.print_test("Actualizar empresa")
            update_data = {
                "descripcion": "Descripción actualizada de la empresa con más detalles sobre sus servicios",
                "ubicacion": "Bogotá D.C., Colombia"
            }
            self.make_request("PUT", f"/api/empresas/{empresa_id}", data=update_data, use_auth=True)
            
            # 9. Actualizar empresa sin autenticación
            self.print_test("Actualizar empresa sin autenticación")
            self.make_request("PUT", f"/api/empresas/{empresa_id}", data=update_data)
        
        # 10. Obtener empresa inexistente
        self.print_test("Obtener empresa inexistente")
        fake_id = "507f1f77bcf86cd799439999"
        self.make_request("GET", f"/api/empresas/{fake_id}")
        
        # 11. Obtener mis empresas
        self.print_test("Obtener mis empresas")
        self.make_request("GET", "/api/empresas/mis-empresas", use_auth=True)
        
        # 12. Obtener mis empresas sin autenticación
        self.print_test("Obtener mis empresas sin autenticación")
        self.make_request("GET", "/api/empresas/mis-empresas")
        
        # 13. Buscar empresas por ubicación
        self.print_test("Buscar empresas por ubicación")
        self.make_request("GET", "/api/empresas/buscar-por-ubicacion", params={"ubicacion": "Bogotá"})
        
        # 14. Buscar sin parámetro ubicación
        self.print_test("Buscar sin parámetro ubicación")
        self.make_request("GET", "/api/empresas/buscar-por-ubicacion")
        
        # 15. Obtener estadísticas
        self.print_test("Obtener estadísticas")
        self.make_request("GET", "/api/empresas/estadisticas", use_auth=True)
        
        # 16. Obtener estadísticas sin autenticación
        self.print_test("Obtener estadísticas sin autenticación")
        self.make_request("GET", "/api/empresas/estadisticas")

    def test_error_endpoints(self):
        """Prueba endpoints que no existen"""
        self.print_separator("ENDPOINTS DE ERROR")
        
        self.print_test("Endpoint inexistente")
        self.make_request("GET", "/api/inexistente")
        
        self.print_test("Método no permitido")
        self.make_request("PATCH", "/api/users")

    def cleanup_test_data(self):
        """Limpia los datos de prueba creados (opcional)"""
        self.print_separator("LIMPIEZA DE DATOS DE PRUEBA")
        
        # Eliminar usuarios creados
        for user_id in self.created_ids["users"]:
            self.print_test(f"Eliminando usuario: {user_id}")
            self.make_request("DELETE", f"/api/users/{user_id}")
        
        # Eliminar empresas creadas
        for empresa_id in self.created_ids["empresas"]:
            self.print_test(f"Eliminando empresa: {empresa_id}")
            self.make_request("DELETE", f"/api/empresas/{empresa_id}", use_auth=True)

    def run_all_tests(self, cleanup=False):
        """Ejecuta todas las pruebas"""
        print("🚀 INICIANDO TESTING COMPLETO DE LA API")
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 URL Base: {self.base_url}")
        
        # Verificar que el servidor esté disponible
        status, _ = self.make_request("GET", "/health")
        if status is None:
            print("❌ El servidor no está disponible. Asegúrate de ejecutar 'python app.py'")
            return
        
        # Ejecutar todas las pruebas
        self.test_health_endpoints()
        self.test_user_endpoints()
        self.test_empresa_endpoints()
        self.test_error_endpoints()
        
        # Limpieza opcional
        if cleanup:
            self.cleanup_test_data()
        
        # Resumen final
        self.print_separator("RESUMEN FINAL")
        print(f"✅ Tests completados exitosamente")
        print(f"📊 Usuarios creados: {len(self.created_ids['users'])}")
        print(f"🏢 Empresas creadas: {len(self.created_ids['empresas'])}")
        
        if not cleanup:
            print("\n💡 Tip: Ejecuta con cleanup=True para eliminar los datos de prueba:")
            print("   tester.run_all_tests(cleanup=True)")

def main():
    """Función principal"""
    print("🎯 API Testing Tool")
    print("Selecciona una opción:")
    print("1. Ejecutar todas las pruebas")
    print("2. Ejecutar todas las pruebas + limpiar datos")
    print("3. Solo endpoints de usuarios")
    print("4. Solo endpoints de empresas")
    print("5. Solo endpoints de salud")
    
    choice = input("\nIngresa tu opción (1-5): ").strip()
    
    tester = APITester()
    
    if choice == "1":
        tester.run_all_tests(cleanup=False)
    elif choice == "2":
        tester.run_all_tests(cleanup=True)
    elif choice == "3":
        tester.test_health_endpoints()
        tester.test_user_endpoints()
    elif choice == "4":
        tester.test_health_endpoints()
        tester.test_empresa_endpoints()
    elif choice == "5":
        tester.test_health_endpoints()
    else:
        print("❌ Opción inválida")
        return
    
    print("\n🎉 ¡Testing completado!")

if __name__ == "__main__":
    # Ejecutar directamente todas las pruebas
    tester = APITester()
    tester.run_all_tests(cleanup=False)
    
    # O ejecutar el menú interactivo
    # main()