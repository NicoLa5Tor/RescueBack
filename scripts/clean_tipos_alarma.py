#!/usr/bin/env python3
"""
Script para limpiar todos los tipos de alarma existentes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.tipo_alarma_repository import TipoAlarmaRepository

def clean_tipos_alarma():
    """Elimina todos los tipos de alarma existentes"""
    
    # print("🧹 Limpiando tipos de alarma existentes...")
    
    repo = TipoAlarmaRepository()
    
    # Obtener estadísticas antes de limpiar
    stats_antes = repo.get_tipos_alarma_stats()
    # print(f"📊 Antes de limpiar: {stats_antes['total']} tipos de alarma")
    
    # Eliminar todos los tipos de alarma
    try:
        result = repo.collection.delete_many({})
    # print(f"🗑️ Eliminados: {result.deleted_count} tipos de alarma")
        
        # Verificar que se eliminaron todos
        stats_despues = repo.get_tipos_alarma_stats()
    # print(f"📊 Después de limpiar: {stats_despues['total']} tipos de alarma")
        
        if stats_despues['total'] == 0:
    # print("✅ Limpieza completada exitosamente")
            return True
        else:
    # print("❌ Error: Aún quedan tipos de alarma")
            return False
            
    except Exception as e:
    # print(f"❌ Error limpiando tipos de alarma: {e}")
        return False

def main():
    """Función principal"""
    # print("🚀 Iniciando limpieza de tipos de alarma...")
    # print("=" * 50)
    
    try:
        if clean_tipos_alarma():
    # print("\n✅ Limpieza ejecutada exitosamente!")
        else:
    # print("\n❌ Error durante la limpieza")
            sys.exit(1)
    except Exception as e:
    # print(f"\n❌ Error ejecutando limpieza: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
