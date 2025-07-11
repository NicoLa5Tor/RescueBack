import requests
import time
from typing import Tuple, Optional

def obtener_lat_lon(direccion: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Devuelve la latitud y longitud de una dirección usando Nominatim (OpenStreetMap).
    Retorna una tupla (latitud, longitud) como cadenas. Si no encuentra, retorna (None, None).
    
    Args:
        direccion (str): La dirección a geocodificar
        
    Returns:
        Tuple[Optional[str], Optional[str]]: (latitud, longitud) o (None, None)
    """
    if not direccion or direccion.strip() == '':
        return None, None
        
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": direccion.strip(),
        "format": "json",
        "limit": 1,
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "RescueSystem/1.0 (rescue@ecoes.com)"  # Identificador del proyecto
    }
    
    try:
        # Respetar el rate limit de Nominatim (máximo 1 request por segundo)
        time.sleep(1)
        
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if data and len(data) > 0:
                lat = data[0].get('lat')
                lon = data[0].get('lon')
                
                if lat and lon:
                    print(f"✅ Geocodificación exitosa para '{direccion}': {lat}, {lon}")
                    return str(lat), str(lon)
            else:
                print(f"⚠️ No se encontraron coordenadas para: {direccion}")
                return None, None
        elif resp.status_code == 429:
            print(f"⏰ Rate limit excedido para geocodificación de '{direccion}'")
            return None, None
        elif resp.status_code == 403:
            print(f"🚫 Acceso denegado al servicio de geocodificación para '{direccion}'")
            return None, None
        else:
            print(f"❌ Error del servidor de geocodificación ({resp.status_code}) para '{direccion}'")
            return None, None
        
    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout en geocodificación para '{direccion}'")
        return None, None
    except requests.exceptions.ConnectionError:
        print(f"🌐 Error de conexión en geocodificación para '{direccion}'")
        return None, None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en geocodificación para '{direccion}': {e}")
        return None, None
    except Exception as e:
        print(f"❌ Error inesperado en geocodificación: {e}")
        return None, None

def generar_url_google_maps(lat: str, lon: str, zoom: int = 15) -> str:
    """
    Genera una URL de Google Maps para las coordenadas dadas.
    
    Args:
        lat (str): Latitud
        lon (str): Longitud  
        zoom (int): Nivel de zoom (default: 15)
        
    Returns:
        str: URL de Google Maps
    """
    return f"https://www.google.com/maps/@{lat},{lon},{zoom}z"

def procesar_direccion_para_hardware(direccion: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Procesa una dirección y devuelve las coordenadas, URL de Google Maps y posible error.
    
    Args:
        direccion (str): La dirección a procesar
        
    Returns:
        Tuple[Optional[str], Optional[str], Optional[str]]: (direccion_url, coordenadas_string, error_msg)
    """
    if not direccion or direccion.strip() == '':
        return None, None, "La dirección no puede estar vacía"
        
    lat, lon = obtener_lat_lon(direccion)
    
    if lat and lon:
        # Generar URL de Google Maps
        direccion_url = generar_url_google_maps(lat, lon)
        # Guardar coordenadas como string para referencia
        coordenadas = f"{lat},{lon}"
        return direccion_url, coordenadas, None
    
    return None, None, f"No se pudo geocodificar la dirección: '{direccion}'. Verifica que la dirección esté bien escrita e incluya ciudad/región."

# Función de ejemplo/test
if __name__ == "__main__":
    # Ejemplo de uso
    direccion = "Universidad de Cundinamarca, Facatativá"
    lat, lon = obtener_lat_lon(direccion)
    print(f"Latitud: {lat}, Longitud: {lon}")
    
    if lat and lon:
        url = generar_url_google_maps(lat, lon)
        print(f"URL: {url}")
