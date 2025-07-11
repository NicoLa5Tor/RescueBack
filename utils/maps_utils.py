import urllib.parse

def direccion_google_maps(nombre_o_direccion):
    """
    Genera la URL de Google Maps para mostrar un punto o búsqueda
    basado en el nombre del lugar o la dirección dada.
    
    Args:
        nombre_o_direccion (str): Nombre del lugar o dirección a buscar
        
    Returns:
        str: URL de Google Maps para la búsqueda
    """
    if not nombre_o_direccion or not nombre_o_direccion.strip():
        return ""
    
    consulta_codificada = urllib.parse.quote_plus(nombre_o_direccion.strip())
    url = f"https://www.google.com/maps?q={consulta_codificada}"
    return url

def direccion_openstreetmap(direccion):
    """
    Devuelve la URL para buscar la dirección o lugar en OpenStreetMap.
    
    Args:
        direccion (str): Dirección o lugar a buscar
        
    Returns:
        str: URL de OpenStreetMap para la búsqueda
    """
    if not direccion or not direccion.strip():
        return ""
    
    direccion_codificada = urllib.parse.quote_plus(direccion.strip())
    url = f"https://www.openstreetmap.org/search?query={direccion_codificada}"
    return url

# Ejemplos de uso:
# print(direccion_google_maps("Universidad de Cundinamarca, Facatativá"))
# print(direccion_google_maps("Restaurante Donde Pablo, Facatativá"))  
# print(direccion_google_maps("Plaza Bolívar, Bogotá"))
