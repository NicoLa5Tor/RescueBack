#!/usr/bin/env python3
"""
Script para crear tipos de empresa por defecto en la base de datos
"""
import sys
import os

# Agregar el directorio padre al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.tipo_empresa import TipoEmpresa
from repositories.tipo_empresa_repository import TipoEmpresaRepository
from bson import ObjectId

def crear_tipos_empresa_por_defecto():
    """Crea tipos de empresa por defecto"""
    
    # Crear el repositorio
    repository = TipoEmpresaRepository()
    
    # ID de ejemplo para el usuario creador (deberías usar un ID válido de tu base de datos)
    usuario_admin_id = ObjectId("507f1f77bcf86cd799439011")  # Cambia esto por un ID válido
    
    # Tipos de empresa por defecto
    tipos_empresa = [
        {
            "nombre": "Manufactura",
            "descripcion": "Empresas dedicadas a la producción y fabricación de bienes y productos"
        },
        {
            "nombre": "Servicios",
            "descripcion": "Empresas que ofrecen servicios profesionales y técnicos"
        },
        {
            "nombre": "Tecnología",
            "descripcion": "Empresas de desarrollo de software, hardware y soluciones tecnológicas"
        },
        {
            "nombre": "Comercio",
            "descripcion": "Empresas dedicadas a la compra y venta de productos al por mayor o menor"
        },
        {
            "nombre": "Construcción",
            "descripcion": "Empresas de construcción, infraestructura y desarrollo inmobiliario"
        },
        {
            "nombre": "Salud",
            "descripcion": "Empresas del sector salud, hospitales, clínicas y servicios médicos"
        },
        {
            "nombre": "Educación",
            "descripcion": "Instituciones educativas, centros de formación y capacitación"
        },
        {
            "nombre": "Agricultura",
            "descripcion": "Empresas del sector agrícola, ganadero y agroalimentario"
        },
        {
            "nombre": "Transporte",
            "descripcion": "Empresas de transporte, logística y distribución"
        },
        {
            "nombre": "Energía",
            "descripcion": "Empresas del sector energético, petróleo, gas y energías renovables"
        }
    ]
    
    print("Creando tipos de empresa por defecto...")
    print("-" * 50)
    
    for tipo_data in tipos_empresa:
        # Verificar si ya existe
        existing = repository.get_by_nombre(tipo_data["nombre"])
        if existing["success"]:
            print(f"❌ '{tipo_data['nombre']}' ya existe, saltando...")
            continue
        
        # Crear nuevo tipo
        tipo_empresa = TipoEmpresa(
            nombre=tipo_data["nombre"],
            descripcion=tipo_data["descripcion"],
            creado_por=usuario_admin_id
        )
        
        result = repository.create(tipo_empresa)
        
        if result["success"]:
            print(f"✅ Tipo de empresa '{tipo_data['nombre']}' creado exitosamente")
        else:
            print(f"❌ Error al crear '{tipo_data['nombre']}': {result.get('errors', [])}")
    
    print("-" * 50)
    print("Proceso completado!")

if __name__ == "__main__":
    try:
        crear_tipos_empresa_por_defecto()
    except Exception as e:
        print(f"Error ejecutando el script: {str(e)}")
        sys.exit(1)
