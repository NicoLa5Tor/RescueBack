#!/usr/bin/env python3
"""
Script para descargar imagen y convertir a base64
"""

import requests
import base64
import sys
import os

def download_and_convert_to_base64(url, output_file=None):
    """
    Descarga una imagen desde una URL y la convierte a base64
    
    Args:
        url (str): URL de la imagen
        output_file (str): Archivo opcional para guardar el base64
        
    Returns:
        str: Imagen en formato base64
    """
    try:
        print(f"🔗 Descargando imagen desde: {url}")
        
        # Descargar la imagen
        response = requests.get(url)
        response.raise_for_status()
        
        # Determinar el tipo de contenido
        content_type = response.headers.get('content-type', 'image/jpeg')
        
        # Convertir a base64
        image_data = response.content
        base64_string = base64.b64encode(image_data).decode('utf-8')
        
        # Crear el data URI completo
        data_uri = f"data:{content_type};base64,{base64_string}"
        
        print(f"✅ Imagen convertida a base64")
        print(f"📏 Tamaño: {len(image_data)} bytes")
        print(f"🖼️ Tipo: {content_type}")
        
        # Guardar en archivo si se especifica
        if output_file:
            with open(output_file, 'w') as f:
                f.write(data_uri)
            print(f"💾 Guardado en: {output_file}")
        
        return data_uri
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error descargando imagen: {e}")
        return None
    except Exception as e:
        print(f"❌ Error convirtiendo imagen: {e}")
        return None

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python3 download_and_convert_image.py <URL> [archivo_salida]")
        sys.exit(1)
    
    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("🚀 Iniciando descarga y conversión de imagen...")
    print("=" * 60)
    
    base64_data = download_and_convert_to_base64(url, output_file)
    
    if base64_data:
        print("\n✅ Conversión completada exitosamente!")
        print(f"📋 Primeros 100 caracteres del base64:")
        print(base64_data[:100] + "...")
    else:
        print("\n❌ Error en la conversión")
        sys.exit(1)

if __name__ == "__main__":
    main()
