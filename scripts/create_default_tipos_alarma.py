#!/usr/bin/env python3
"""
Script para crear tipos de alarma por defecto en la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.tipo_alarma import TipoAlarma
from repositories.tipo_alarma_repository import TipoAlarmaRepository
from repositories.empresa_repository import EmpresaRepository
from datetime import datetime
import base64

def create_default_tipos_alarma():
    """Crea tipos de alarma por defecto para el sistema"""
    
    # Inicializar repositorios
    tipo_alarma_repo = TipoAlarmaRepository()
    empresa_repo = EmpresaRepository()
    
    # Obtener todas las empresas activas
    empresas = empresa_repo.find_all()
    
    # Definir tipos de alarma por defecto
    tipos_alarma_default = [
        {
            'nombre': 'Incendio',
            'descripcion': 'Alerta de incendio detectado en las instalaciones',
            'tipo_alerta': 'ROJO',
            'color_alerta': '#FF0000',
            'recomendaciones': [
                'Evacuar inmediatamente la zona afectada',
                'Activar el sistema de extinción automática',
                'Llamar a los bomberos (911)',
                'Dirigirse al punto de encuentro designado',
                'No usar ascensores',
                'Seguir las rutas de evacuación señalizadas'
            ],
            'implementos_necesarios': [
                'Extintores tipo ABC',
                'Mangueras contra incendios',
                'Equipos de respiración autónoma',
                'Hachas contra incendios',
                'Detectores de humo',
                'Alarmas sonoras',
                'Señalización de evacuación'
            ],
            'imagen_base64': 'https://assets.codeium.com/9e/6e/9e6e5a1f-9b8d-4c1f-9b8d-4c1f9b8d4c1f.png'  # URL de incendio
        },
        {
            'nombre': 'Intrusión',
            'descripcion': 'Alerta de intrusión o acceso no autorizado',
            'tipo_alerta': 'AMARILLO',
            'color_alerta': '#FFFF00',
            'recomendaciones': [
                'Verificar identidad del personal',
                'Revisar cámaras de seguridad',
                'Notificar a seguridad inmediatamente',
                'Activar protocolos de seguridad',
                'Documentar el incidente',
                'Contactar a las autoridades si es necesario'
            ],
            'implementos_necesarios': [
                'Cámaras de seguridad',
                'Sensores de movimiento',
                'Tarjetas de acceso',
                'Walkie-talkies',
                'Llaves maestras',
                'Sistemas de alarma',
                'Iluminación de emergencia'
            ],
            'imagen_base64': 'https://assets.codeium.com/2a/3b/2a3b4c5d-6e7f-8g9h-0i1j-2k3l4m5n6o7p.png'  # URL de intrusión
        },
        {
            'nombre': 'Fuga de Gas',
            'descripcion': 'Alerta de detección de fuga de gas peligroso',
            'tipo_alerta': 'NARANJA',
            'color_alerta': '#FFA500',
            'recomendaciones': [
                'Ventilar el área inmediatamente',
                'Cerrar válvulas de gas',
                'Evacuar la zona de peligro',
                'No encender llamas ni equipos eléctricos',
                'Usar detectores de gas',
                'Llamar a especialistas en gas'
            ],
            'implementos_necesarios': [
                'Detectores de gas',
                'Válvulas de cierre de emergencia',
                'Equipos de ventilación',
                'Máscaras de gas',
                'Herramientas antichispa',
                'Medidores de concentración de gas'
            ],
            'imagen_base64': 'https://assets.codeium.com/4c/5d/4c5d6e7f-8g9h-0i1j-2k3l-4m5n6o7p8q9r.png'  # URL de fuga de gas
        },
        {
            'nombre': 'Emergencia Médica',
            'descripcion': 'Alerta de emergencia médica que requiere atención inmediata',
            'tipo_alerta': 'AZUL',
            'color_alerta': '#0000FF',
            'recomendaciones': [
                'Llamar inmediatamente al servicio médico (911)',
                'Aplicar primeros auxilios básicos',
                'Mantener a la persona consciente si es posible',
                'No mover a la persona lesionada',
                'Controlar hemorragias si las hay',
                'Preparar el acceso para paramédicos'
            ],
            'implementos_necesarios': [
                'Botiquín de primeros auxilios',
                'Desfibrilador externo automático (DEA)',
                'Camilla',
                'Oxígeno portátil',
                'Vendajes y gasas',
                'Medicamentos básicos',
                'Teléfono directo con servicios médicos'
            ],
            'imagen_base64': 'https://assets.codeium.com/6e/7f/6e7f8g9h-0i1j-2k3l-4m5n-6o7p8q9r0s1t.png'  # URL de emergencia médica
        },
        {
            'nombre': 'Todo Despejado',
            'descripcion': 'Señal de que la situación ha sido controlada y es segura',
            'tipo_alerta': 'VERDE',
            'color_alerta': '#00FF00',
            'recomendaciones': [
                'Verificar que todas las áreas estén seguras',
                'Confirmar que el personal esté completo',
                'Documentar el incidente resuelto',
                'Realizar inspección post-emergencia',
                'Reactivar sistemas normales',
                'Comunicar estado seguro a todo el personal'
            ],
            'implementos_necesarios': [
                'Lista de verificación de seguridad',
                'Equipos de comunicación',
                'Formularios de reporte',
                'Herramientas de inspección',
                'Sistemas de monitoreo'
            ],
            'imagen_base64': 'https://assets.codeium.com/8g/9h/8g9h0i1j-2k3l-4m5n-6o7p-8q9r0s1t2u3v.png'  # URL de todo despejado
        }
    ]
    
    tipos_creados = 0

    print("Creando tipos de alarma globales...")
    # Crear tipos de alarma sin empresa específica (globales)
    for tipo_data in tipos_alarma_default:
        try:
            tipo_alarma = TipoAlarma(
                nombre=tipo_data['nombre'],
                descripcion=tipo_data['descripcion'],
                tipo_alerta=tipo_data['tipo_alerta'],
                color_alerta=tipo_data['color_alerta'],
                recomendaciones=tipo_data['recomendaciones'],
                implementos_necesarios=tipo_data['implementos_necesarios'],
                imagen_base64=tipo_data['imagen_base64'],
                empresa_id=None  # Tipo de alarma global
            )
            
            # Validar antes de crear
            errors = tipo_alarma.validate()
            if errors:
                print(f"Error validando tipo de alarma '{tipo_data['nombre']}': {errors}")
                continue
            
            # Crear en la base de datos
            tipo_creado = tipo_alarma_repo.create_tipo_alarma(tipo_alarma)
            if tipo_creado:
                tipos_creados += 1
                print(f"Tipo de alarma creado: {tipo_data['nombre']} ({tipo_data['tipo_alerta']})")
            else:
                print(f"Error creando tipo de alarma: {tipo_data['nombre']}")
                
        except Exception as e:
            print(f"Error creando tipo de alarma '{tipo_data['nombre']}': {e}")
    
    print(f"\n✅ Proceso completado. Se crearon {tipos_creados} tipos de alarma.")
    
    # Mostrar estadísticas
    stats = tipo_alarma_repo.get_tipos_alarma_stats()
    print(f"\nEstadísticas de tipos de alarma:")
    print(f"Total: {stats['total']}")
    print(f"Activos: {stats['active']}")
    print(f"Inactivos: {stats['inactive']}")
    print(f"Por tipo de alerta: {stats['por_tipo']}")

def main():
    """Función principal"""
    print("🚀 Iniciando creación de tipos de alarma por defecto...")
    print("=" * 60)
    
    try:
        create_default_tipos_alarma()
        print("\n✅ Script ejecutado exitosamente!")
    except Exception as e:
        print(f"\n❌ Error ejecutando script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
