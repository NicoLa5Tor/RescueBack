#!/usr/bin/env python3
"""
Script de prueba para demostrar el sistema de autenticación de hardware.
Muestra el flujo completo desde la autenticación hasta el envío de alertas.
"""

import requests
import json
import time
from datetime import datetime


class HardwareAuthTester:
    """Clase para probar el sistema de autenticación de hardware"""
    
    def __init__(self, base_url="http://localhost:5002"):
        self.base_url = base_url
        self.token = None
        self.token_expires_at = None
        
    def test_authentication(self, hardware_nombre, empresa_nombre, sede):
        """Prueba la autenticación de hardware"""
        print(f"\n=== PRUEBA DE AUTENTICACIÓN ===")
        print(f"Hardware: {hardware_nombre}")
        print(f"Empresa: {empresa_nombre}")
        print(f"Sede: {sede}")
        
        url = f"{self.base_url}/api/hardware-auth/authenticate"
        payload = {
            "hardware_nombre": hardware_nombre,
            "empresa_nombre": empresa_nombre,
            "sede": sede
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Autenticación exitosa")
                print(f"Token: {data['data']['token'][:50]}...")
                print(f"Hardware ID: {data['data']['hardware_id']}")
                print(f"Empresa ID: {data['data']['empresa_id']}")
                print(f"Válido por: {data['data']['valid_for_minutes']} minutos")
                print(f"Expira en: {data['data']['expires_at']}")
                
                # Guardar token para uso posterior
                self.token = data['data']['token']
                self.token_expires_at = data['data']['expires_at']
                
                return True
            else:
                data = response.json()
                print(f"❌ Error en autenticación: {data.get('message', 'Error desconocido')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def test_token_verification(self):
        """Prueba la verificación del token"""
        if not self.token:
            print("❌ No hay token disponible para verificar")
            return False
        
        print(f"\n=== PRUEBA DE VERIFICACIÓN DE TOKEN ===")
        
        url = f"{self.base_url}/api/hardware-auth/verify-token"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Token válido")
                print(f"Hardware: {data['payload']['hardware_nombre']}")
                print(f"Empresa: {data['payload']['empresa_nombre']}")
                print(f"Sede: {data['payload']['sede']}")
                return True
            else:
                data = response.json()
                print(f"❌ Token inválido: {data.get('message', 'Error desconocido')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def test_mqtt_message_with_auth(self):
        """Prueba el envío de mensaje MQTT con autenticación"""
        if not self.token:
            print("❌ No hay token disponible para enviar mensaje")
            return False
        
        print(f"\n=== PRUEBA DE ENVÍO DE MENSAJE MQTT ===")
        
        url = f"{self.base_url}/api/mqtt-alerts/process"
        payload = {
            "empresa1": {
                "semaforo": {
                    "sede": "principal",
                    "alerta": "roja",
                    "ubicacion": "Cruce principal",
                    "hardware_id": "SEM001",
                    "nombre": "Semaforo001",
                    "coordenadas": {"lat": 4.6097, "lng": -74.0817},
                    "timestamp": datetime.now().isoformat()
                }
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Mensaje MQTT procesado exitosamente")
                print(f"Alerta ID: {data.get('alert_id', 'N/A')}")
                print(f"Autorizado: {data.get('autorizado', 'N/A')}")
                print(f"Estado activo: {data.get('estado_activo', 'N/A')}")
                return True
            else:
                data = response.json()
                print(f"❌ Error procesando mensaje: {data.get('message', 'Error desconocido')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def test_active_sessions(self):
        """Prueba la obtención de sesiones activas"""
        print(f"\n=== PRUEBA DE SESIONES ACTIVAS ===")
        
        url = f"{self.base_url}/api/hardware-auth/sessions"
        
        try:
            response = requests.get(url)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sesiones activas obtenidas: {data['total']}")
                
                for session in data['data']:
                    print(f"  - Hardware: {session['hardware_nombre']}")
                    print(f"    Empresa: {session['empresa_nombre']}")
                    print(f"    Sede: {session['sede']}")
                    print(f"    Autenticado: {session['authenticated_at']}")
                    print(f"    Expira: {session['expires_at']}")
                    print()
                
                return True
            else:
                data = response.json()
                print(f"❌ Error obteniendo sesiones: {data.get('message', 'Error desconocido')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def test_system_info(self):
        """Prueba la obtención de información del sistema"""
        print(f"\n=== INFORMACIÓN DEL SISTEMA ===")
        
        url = f"{self.base_url}/api/hardware-auth/info"
        
        try:
            response = requests.get(url)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Información del sistema obtenida")
                print(f"Nombre: {data['system_info']['name']}")
                print(f"Versión: {data['system_info']['version']}")
                print(f"Tiempo de expiración: {data['system_info']['token_expiry_minutes']} minutos")
                
                print("\nEndpoints disponibles:")
                for endpoint, path in data['system_info']['endpoints'].items():
                    print(f"  - {endpoint}: {path}")
                
                print("\nFlujo de autenticación:")
                for step in data['system_info']['authentication_flow']:
                    print(f"  {step}")
                
                return True
            else:
                data = response.json()
                print(f"❌ Error obteniendo información: {data.get('message', 'Error desconocido')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def test_expired_token(self):
        """Prueba qué sucede cuando el token expira"""
        print(f"\n=== PRUEBA DE TOKEN EXPIRADO ===")
        print("Esperando a que el token expire...")
        
        if self.token_expires_at:
            # Nota: En un entorno real, esperarías 5 minutos
            # Para pruebas, puedes usar un token manualmente expirado
            print("(En un entorno real, espere 5 minutos para que expire)")
            
            # Simular el uso de un token expirado
            time.sleep(2)  # Pequeña pausa para simular
            print("Intentando usar token (simulación de expiración)")
            
            # Intentar verificar el token
            return self.test_token_verification()
        
        return False
    
    def run_full_test(self):
        """Ejecuta todas las pruebas del sistema"""
        print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE AUTENTICACIÓN DE HARDWARE")
        print("=" * 70)
        
        # Test 1: Información del sistema
        self.test_system_info()
        
        # Test 2: Autenticación exitosa
        auth_success = self.test_authentication(
            hardware_nombre="Semaforo001",
            empresa_nombre="empresa1",
            sede="principal"
        )
        
        if auth_success:
            # Test 3: Verificación de token
            self.test_token_verification()
            
            # Test 4: Envío de mensaje MQTT
            self.test_mqtt_message_with_auth()
            
            # Test 5: Sesiones activas
            self.test_active_sessions()
        
        # Test 6: Autenticación fallida
        print(f"\n=== PRUEBA DE AUTENTICACIÓN FALLIDA ===")
        self.test_authentication(
            hardware_nombre="HardwareInexistente",
            empresa_nombre="EmpresaInexistente",
            sede="SedeInexistente"
        )
        
        print("\n" + "=" * 70)
        print("🏁 PRUEBAS COMPLETADAS")


def main():
    """Función principal para ejecutar las pruebas"""
    print("Sistema de Autenticación de Hardware - Pruebas")
    print("Asegúrate de que el servidor esté ejecutándose en http://localhost:5002")
    print()
    
    tester = HardwareAuthTester()
    tester.run_full_test()


if __name__ == "__main__":
    main()
