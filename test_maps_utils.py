#!/usr/bin/env python3
"""
Script para probar la funcionalidad de los URLs de mapas
"""

from utils.maps_utils import direccion_google_maps, direccion_openstreetmap

def test_maps_functions():
    """
    Prueba las funciones de mapas con diferentes direcciones
    """
    print("🧪 Probando funciones de mapas...")
    
    # Lista de direcciones de prueba
    test_addresses = [
        "Universidad de Cundinamarca, Facatativá",
        "Restaurante Donde Pablo, Facatativá",
        "Plaza Bolívar, Bogotá",
        "Carrera 7 # 40-50, Bogotá",
        "Calle 26 # 92-32, Bogotá",
        "Centro Comercial Andino, Zona Rosa, Bogotá",
        "",  # Dirección vacía
        None,  # Dirección nula
        "   ",  # Dirección con espacios
    ]
    
    print("📍 Probando direcciones:\n")
    
    for i, address in enumerate(test_addresses, 1):
        print(f"--- Prueba {i} ---")
        print(f"Dirección: {repr(address)}")
        
        # Probar Google Maps
        try:
            google_url = direccion_google_maps(address)
            print(f"Google Maps: {google_url}")
        except Exception as e:
            print(f"Error Google Maps: {e}")
        
        # Probar OpenStreetMap
        try:
            osm_url = direccion_openstreetmap(address)
            print(f"OpenStreetMap: {osm_url}")
        except Exception as e:
            print(f"Error OpenStreetMap: {e}")
        
        print()

if __name__ == "__main__":
    test_maps_functions()
    print("✅ Pruebas de funciones de mapas completadas")
