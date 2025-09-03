#!/usr/bin/env python3
"""
Script para limpiar sesiones expiradas del sistema de autenticación.

Este script puede ejecutarse como cron job para mantener la base de datos limpia.

Uso:
    python scripts/cleanup_sessions.py

Como cron job (ejecutar cada hora):
    0 * * * * cd /path/to/RescueBack && python scripts/cleanup_sessions.py
"""

import sys
import os
from datetime import datetime
import logging

# Añadir el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.session_service import SessionService
from core.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/session_cleanup.log') if os.path.exists('logs') else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

def cleanup_expired_sessions():
    """Limpiar sesiones expiradas de la base de datos"""
    try:
        logger.info("Iniciando limpieza de sesiones expiradas...")
        
        # Inicializar el servicio de sesiones
        session_service = SessionService()
        
        # Ejecutar limpieza
        result = session_service.cleanup_expired_sessions()
        
        if result['success']:
            deleted_count = result.get('deleted_count', 0)
            logger.info(f"✅ Limpieza completada exitosamente: {deleted_count} sesiones eliminadas")
            
            # Obtener estadísticas después de la limpieza
            stats_result = session_service.get_session_statistics()
            if stats_result['success']:
                stats = stats_result['data']
                logger.info(f"📊 Estadísticas después de la limpieza:")
                logger.info(f"   - Sesiones activas: {stats.get('active_sessions', 0)}")
                logger.info(f"   - Sesiones expiradas restantes: {stats.get('expired_sessions', 0)}")
                logger.info(f"   - Total de sesiones: {stats.get('total_sessions', 0)}")
            
            return True
        else:
            logger.error(f"❌ Error en la limpieza: {result.get('errors', ['Error desconocido'])}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Excepción durante la limpieza: {str(e)}")
        return False

def get_session_statistics():
    """Obtener estadísticas actuales del sistema de sesiones"""
    try:
        session_service = SessionService()
        result = session_service.get_session_statistics()
        
        if result['success']:
            stats = result['data']
            logger.info("📊 Estadísticas actuales del sistema de sesiones:")
            logger.info(f"   - Sesiones activas: {stats.get('active_sessions', 0)}")
            logger.info(f"   - Sesiones expiradas: {stats.get('expired_sessions', 0)}")
            logger.info(f"   - Total de sesiones: {stats.get('total_sessions', 0)}")
            return stats
        else:
            logger.error(f"Error obteniendo estadísticas: {result.get('errors', ['Error desconocido'])}")
            return None
            
    except Exception as e:
        logger.error(f"Excepción obteniendo estadísticas: {str(e)}")
        return None

def main():
    """Función principal del script"""
    logger.info("="*50)
    logger.info("🧹 INICIANDO LIMPIEZA DE SESIONES EXPIRADAS")
    logger.info(f"⏰ Fecha y hora: {datetime.now().isoformat()}")
    logger.info("="*50)
    
    # Mostrar estadísticas antes de la limpieza
    logger.info("📊 Estadísticas ANTES de la limpieza:")
    stats_before = get_session_statistics()
    
    # Ejecutar limpieza
    success = cleanup_expired_sessions()
    
    # Mostrar estadísticas después de la limpieza si fue exitosa
    if success:
        logger.info("📊 Estadísticas DESPUÉS de la limpieza:")
        stats_after = get_session_statistics()
        
        # Calcular diferencia si ambas estadísticas están disponibles
        if stats_before and stats_after:
            sessions_removed = stats_before.get('total_sessions', 0) - stats_after.get('total_sessions', 0)
            if sessions_removed > 0:
                logger.info(f"🗑️  Total de sesiones eliminadas: {sessions_removed}")
    
    logger.info("="*50)
    logger.info(f"✅ LIMPIEZA COMPLETADA {'EXITOSAMENTE' if success else 'CON ERRORES'}")
    logger.info("="*50)
    
    # Código de salida
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()