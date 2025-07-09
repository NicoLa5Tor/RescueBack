from flask import Blueprint, request, jsonify, g
from services.tipo_empresa_service import TipoEmpresaService
from utils.permissions import require_super_admin_token
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Crear el Blueprint
tipo_empresa_controller = Blueprint('tipo_empresa', __name__)

# Crear el servicio
tipo_empresa_service = TipoEmpresaService()


@tipo_empresa_controller.route('/tipos_empresa', methods=['POST'])
@require_super_admin_token
def create_tipo_empresa():
    """Crea un nuevo tipo de empresa"""
    try:
        data = request.json
        usuario_id = g.user_id  # Obtener el usuario del token JWT
        result = tipo_empresa_service.create_tipo_empresa(data, usuario_id)
        return jsonify(result), (201 if result['success'] else 400)
        
    except Exception as e:
        return jsonify({"success": False, "errors": ["Error interno: {}".format(str(e))]}), 500


@tipo_empresa_controller.route('/tipos_empresa/<tipo_empresa_id>', methods=['GET'])
def get_tipo_empresa(tipo_empresa_id):
    """Obtiene un tipo de empresa por su ID"""
    result = tipo_empresa_service.get_tipo_empresa_by_id(tipo_empresa_id)
    return jsonify(result), (200 if result['success'] else 404)


@tipo_empresa_controller.route('/tipos_empresa', methods=['GET'])
def get_all_tipos_empresa():
    """Obtiene todos los tipos de empresa activos (para formularios)"""
    logger.info("=== GET ALL TIPOS EMPRESA (SOLO ACTIVOS) ===")
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 100))
    result = tipo_empresa_service.get_all_tipos_empresa(skip, limit)
    
    logger.info(f"Tipos de empresa activos obtenidos: {result.get('count', 0)}")
    if result.get("success") and result.get("data"):
        logger.info(f"Primeros tipos: {[t.get('nombre', 'N/A') for t in result['data'][:3]]}")
    
    return jsonify(result), 200


@tipo_empresa_controller.route('/tipos_empresa/<tipo_empresa_id>', methods=['PUT'])
@require_super_admin_token
def update_tipo_empresa(tipo_empresa_id):
    """Actualiza un tipo de empresa"""
    try:
        data = request.json
        result = tipo_empresa_service.update_tipo_empresa(tipo_empresa_id, data)
        return jsonify(result), (200 if result['success'] else 400)
        
    except Exception as e:
        return jsonify({"success": False, "errors": ["Error interno: {}".format(str(e))]}), 500


@tipo_empresa_controller.route('/tipos_empresa/<tipo_empresa_id>', methods=['DELETE'])
@require_super_admin_token
def delete_tipo_empresa(tipo_empresa_id):
    """Elimina lógicamente un tipo de empresa"""
    result = tipo_empresa_service.delete_tipo_empresa(tipo_empresa_id)
    return jsonify(result), (200 if result['success'] else 404)


@tipo_empresa_controller.route('/tipos_empresa/search', methods=['GET'])
def search_tipos_empresa():
    """Busca tipos de empresa por nombre o descripción"""
    query = request.args.get('query', '')
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 100))
    result = tipo_empresa_service.search_tipos_empresa(query, skip, limit)
    return jsonify(result), 200


@tipo_empresa_controller.route('/tipos_empresa/activos', methods=['GET'])
def get_tipos_empresa_activos():
    """Obtiene solo los tipos de empresa activos (para selects/dropdowns)"""
    result = tipo_empresa_service.get_tipos_empresa_activos()
    return jsonify(result), 200


@tipo_empresa_controller.route('/tipos_empresa/estadisticas', methods=['GET'])
def get_estadisticas_tipos_empresa():
    """Obtiene estadísticas de tipos de empresa incluyendo promedio de características"""
    result = tipo_empresa_service.get_estadisticas_tipos_empresa()
    return jsonify(result), (200 if result['success'] else 500)


@tipo_empresa_controller.route('/tipos_empresa/<tipo_empresa_id>/toggle-status', methods=['PATCH'])
@require_super_admin_token
def toggle_status_tipo_empresa(tipo_empresa_id):
    """Activa o desactiva un tipo de empresa"""
    try:
        result = tipo_empresa_service.toggle_status_tipo_empresa(tipo_empresa_id)
        return jsonify(result), (200 if result['success'] else 404)
        
    except Exception as e:
        return jsonify({"success": False, "errors": ["Error interno: {}".format(str(e))]}), 500


@tipo_empresa_controller.route('/tipos_empresa/admin/all', methods=['GET'])
@require_super_admin_token
def get_all_tipos_empresa_including_inactive():
    """Obtiene todos los tipos de empresa incluyendo inactivos (solo para administradores)"""
    logger.info("=== GET ALL TIPOS EMPRESA ADMIN (INCLUYENDO INACTIVOS) ===")
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 100))
    result = tipo_empresa_service.get_all_tipos_empresa_including_inactive(skip, limit)
    
    logger.info(f"Total tipos de empresa admin: {result.get('count', 0)}")
    if result.get("success") and result.get("data"):
        activos = [t for t in result["data"] if t.get("activo", True)]
        inactivos = [t for t in result["data"] if not t.get("activo", True)]
        logger.info(f"Tipos activos: {len(activos)}, inactivos: {len(inactivos)}")
        logger.info(f"Primeros tipos: {[t.get('nombre', 'N/A') for t in result['data'][:3]]}")

    return jsonify(result), 200


@tipo_empresa_controller.route('/tipos_empresa/dashboard/all', methods=['GET'])
def get_all_tipos_empresa_dashboard():
    """Obtiene TODOS los tipos de empresa (activos e inactivos) para dashboards"""
    logger.info("=== GET ALL TIPOS EMPRESA DASHBOARD (TODAS) ===")
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 100))
    result = tipo_empresa_service.get_all_tipos_empresa_including_inactive(skip, limit)
    
    logger.info(f"Total tipos de empresa dashboard: {result.get('count', 0)}")
    if result.get("success") and result.get("data"):
        activos = [t for t in result["data"] if t.get("activo", True)]
        inactivos = [t for t in result["data"] if not t.get("activo", True)]
        logger.info(f"Tipos activos: {len(activos)}, inactivos: {len(inactivos)}")
        logger.info(f"Primeros tipos dashboard: {[f'{t.get("nombre", "N/A")} (activo: {t.get("activo", True)})' for t in result['data'][:5]]}")

    return jsonify(result), 200


@tipo_empresa_controller.route('/tipos_empresa/stats/promedio-empresas', methods=['GET'])
@require_super_admin_token
def get_promedio_empresas_por_tipo():
    """Obtiene el promedio de empresas por tipo de empresa (solo super admin)"""
    try:
        logger.info("=== GET PROMEDIO EMPRESAS POR TIPO ===")
        result = tipo_empresa_service.get_promedio_empresas_por_tipo()
        logger.info(f"Promedio calculado: {result.get('data', {}).get('promedio', 0)} empresas por tipo")
        return jsonify(result), (200 if result['success'] else 500)
        
    except Exception as e:
        logger.error(f"Error al obtener promedio de empresas por tipo: {str(e)}")
        return jsonify({"success": False, "errors": ["Error interno: {}".format(str(e))]}), 500


@tipo_empresa_controller.route('/tipos_empresa/stats/total-categorizadas', methods=['GET'])
@require_super_admin_token
def get_total_empresas_categorizadas():
    """Obtiene el total de empresas que tienen tipo asignado (solo super admin)"""
    try:
        logger.info("=== GET TOTAL EMPRESAS CATEGORIZADAS ===")
        result = tipo_empresa_service.get_total_empresas_categorizadas()
        logger.info(f"Total empresas categorizadas: {result.get('data', {}).get('total_categorizadas', 0)}")
        return jsonify(result), (200 if result['success'] else 500)
        
    except Exception as e:
        logger.error(f"Error al obtener total de empresas categorizadas: {str(e)}")
        return jsonify({"success": False, "errors": ["Error interno: {}".format(str(e))]}), 500

