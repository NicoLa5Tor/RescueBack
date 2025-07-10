#!/usr/bin/env python3
"""
Script para probar la creación de hardware con campo topic automático
"""
import requests
import json

BASE_URL = "http://localhost:5002"

def test_hardware_creation():
    """Probar la creación de hardware con topic automático"""
    
    # Datos de prueba para crear hardware
    hardware_data = {
        "nombre": "Botonera_Principal_001",
        "tipo": "BOTONERAS",
        "empresa_nombre": "EcoTransportes S.A.S",  # Debe existir en la DB
        "sede": "Sede Principal",  # Debe existir en las sedes de la empresa
        "datos": {
            "modelo": "BT-500",
            "ubicacion": "Entrada Principal",
            "estado": "activo"
        }
    }
    
    print("🔄 Creando hardware con topic automático...")
    print(f"📋 Datos: {json.dumps(hardware_data, indent=2)}")
    
    # Hacer petición POST para crear hardware
    try:
        response = requests.post(
            f"{BASE_URL}/api/hardware/",
            json=hardware_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📝 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                hardware_info = data.get('data', {})
                topic = hardware_info.get('topic')
                print(f"\n✅ Hardware creado exitosamente!")
                print(f"🎯 Topic generado: {topic}")
                print(f"📍 Formato esperado: empresa/sede/TIPO/nombre")
                return hardware_info.get('_id')
            else:
                print(f"❌ Error en respuesta: {data.get('errors', [])}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en petición: {e}")
    
    return None

def test_hardware_update(hardware_id):
    """Probar la actualización de hardware para verificar regeneración de topic"""
    
    update_data = {
        "nombre": "Botonera_Secundaria_002",
        "sede": "Sede Norte",
        "datos": {
            "modelo": "BT-600",
            "ubicacion": "Entrada Norte",
            "estado": "mantenimiento"
        }
    }
    
    print(f"\n🔄 Actualizando hardware {hardware_id}...")
    print(f"📋 Datos: {json.dumps(update_data, indent=2)}")
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/hardware/{hardware_id}",
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📝 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                hardware_info = data.get('data', {})
                topic = hardware_info.get('topic')
                print(f"\n✅ Hardware actualizado exitosamente!")
                print(f"🎯 Topic regenerado: {topic}")
            else:
                print(f"❌ Error en respuesta: {data.get('errors', [])}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en petición: {e}")

def test_hardware_get(hardware_id):
    """Probar obtener hardware para verificar campo topic"""
    
    print(f"\n🔄 Obteniendo hardware {hardware_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/hardware/{hardware_id}")
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📝 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                hardware_info = data.get('data', {})
                topic = hardware_info.get('topic')
                print(f"\n✅ Hardware obtenido exitosamente!")
                print(f"🎯 Topic actual: {topic}")
            else:
                print(f"❌ Error en respuesta: {data.get('errors', [])}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en petición: {e}")

def main():
    print("🧪 PRUEBA DE CAMPO TOPIC EN HARDWARE")
    print("=" * 50)
    
    # Probar creación
    hardware_id = test_hardware_creation()
    
    if hardware_id:
        # Probar obtención
        test_hardware_get(hardware_id)
        
        # Probar actualización
        test_hardware_update(hardware_id)
        
        # Verificar resultado final
        test_hardware_get(hardware_id)
    
    print("\n🏁 Pruebas completadas!")

if __name__ == "__main__":
    main()
