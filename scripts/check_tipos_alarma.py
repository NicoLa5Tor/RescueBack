#!/usr/bin/env python3
"""
Script para verificar los tipos de alarma creados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.tipo_alarma_repository import TipoAlarmaRepository

def check_tipos_alarma():
    """Verifica los tipos de alarma existentes"""
    
    print("🔍 Verificando tipos de alarma existentes...")
    
    repo = TipoAlarmaRepository()
    
    # Obtener estadísticas
    stats = repo.get_tipos_alarma_stats()
    print(f"\n📊 Estadísticas:")
    print(f"Total: {stats['total']}")
    print(f"Activos: {stats['active']}")
    print(f"Inactivos: {stats['inactive']}")
    print(f"Por tipo de alerta: {stats['por_tipo']}")
    
    # Obtener todos los tipos de alarma
    tipos_alarma, total = repo.get_all_tipos_alarma()
    
    print(f"\n📋 Tipos de alarma encontrados:")
    for i, tipo in enumerate(tipos_alarma, 1):
        print(f"{i}. {tipo.nombre} ({tipo.tipo_alerta})")
        print(f"   Color: {tipo.color_alerta}")
        print(f"   Empresa: {'Global' if not tipo.empresa_id else tipo.empresa_id}")
        print(f"   Activo: {'Sí' if tipo.activo else 'No'}")
        print(f"   Recomendaciones: {len(tipo.recomendaciones)} items")
        print(f"   Implementos: {len(tipo.implementos_necesarios)} items")
        print()
    
    # Verificar que tenemos exactamente 5 tipos
    if total == 5:
        print("✅ Correcto: Tenemos exactamente 5 tipos de alarma")
    else:
        print(f"❌ Error: Esperábamos 5 tipos de alarma, encontramos {total}")
    
    # Verificar que tenemos todos los colores
    colores_esperados = ['ROJO', 'AZUL', 'AMARILLO', 'VERDE', 'NARANJA']
    colores_encontrados = [tipo.tipo_alerta for tipo in tipos_alarma]
    
    print(f"\n🎨 Verificación de colores:")
    for color in colores_esperados:
        if color in colores_encontrados:
            print(f"✅ {color}: Encontrado")
        else:
            print(f"❌ {color}: Faltante")
    
    # Verificar que todos son globales (sin empresa_id)
    print(f"\n🌍 Verificación de tipos globales:")
    todos_globales = all(tipo.empresa_id is None for tipo in tipos_alarma)
    if todos_globales:
        print("✅ Todos los tipos de alarma son globales")
    else:
        print("❌ Algunos tipos de alarma tienen empresa asignada")
    
    return total == 5 and len(set(colores_encontrados)) == 5 and todos_globales

def main():
    """Función principal"""
    print("🚀 Iniciando verificación de tipos de alarma...")
    print("=" * 60)
    
    try:
        if check_tipos_alarma():
            print("\n✅ Verificación completada exitosamente!")
        else:
            print("\n❌ La verificación encontró problemas")
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
