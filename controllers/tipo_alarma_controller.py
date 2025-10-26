from flask import Blueprint, jsonify, request
from services.tipo_alarma_service import TipoAlarmaService
from utils.permissions import require_super_admin_token, require_empresa_or_admin_token

# Blueprint para gestionar tipos de alarma
tipo_alarma_bp = Blueprint('tipo_alarma', __name__)

# Servicio asociado a las rutas
tipo_alarma_service = TipoAlarmaService()


def _get_pagination_params():
    """Obtiene parámetros de paginación asegurando valores enteros"""
    try:
        page = int(request.args.get('page', 1))
    except (TypeError, ValueError):
        page = 1
    try:
        limit = int(request.args.get('limit', 50))
    except (TypeError, ValueError):
        limit = 50
    return max(page, 1), max(limit, 1)


def _should_exclude_globales():
    """Determina si se deben excluir los tipos globales según query param."""
    raw_value = (request.args.get('excluir_globales') or '').strip().lower()
    return raw_value in ('true', '1', 'yes', 'on')


def _status_from_result(result, success_code=200, not_found_code=404):
    """Determina el código de estado HTTP según el resultado del servicio"""
    if result.get('success'):
        return success_code
    error_message = (result.get('error') or '').lower()
    if 'no encontrado' in error_message or 'no existe' in error_message:
        return not_found_code
    return 400


@tipo_alarma_bp.route('/tipos-alarma', methods=['POST'])
@require_super_admin_token
def create_tipo_alarma():
    """Crea un nuevo tipo de alarma"""
    payload = request.get_json(silent=True) or {}
    result = tipo_alarma_service.create_tipo_alarma(payload)
    status = 201 if result.get('success') else 400
    return jsonify(result), status


@tipo_alarma_bp.route('/tipos-alarma', methods=['GET'])
@require_empresa_or_admin_token
def list_tipos_alarma():
    """Obtiene todos los tipos de alarma con paginación"""
    page, limit = _get_pagination_params()
    exclude_globales = _should_exclude_globales()
    result = tipo_alarma_service.get_all_tipos_alarma(
        page=page,
        limit=limit,
        exclude_globales=exclude_globales
    )
    return jsonify(result), _status_from_result(result)


@tipo_alarma_bp.route('/tipos-alarma/<tipo_alarma_id>', methods=['GET'])
@require_empresa_or_admin_token
def get_tipo_alarma(tipo_alarma_id):
    """Obtiene un tipo de alarma por su identificador"""
    result = tipo_alarma_service.get_tipo_alarma_by_id(tipo_alarma_id)
    return jsonify(result), _status_from_result(result)


@tipo_alarma_bp.route('/tipos-alarma/<tipo_alarma_id>', methods=['PUT'])
@require_super_admin_token
def update_tipo_alarma(tipo_alarma_id):
    """Actualiza los datos de un tipo de alarma existente"""
    payload = request.get_json(silent=True) or {}
    result = tipo_alarma_service.update_tipo_alarma(tipo_alarma_id, payload)
    return jsonify(result), _status_from_result(result)


@tipo_alarma_bp.route('/tipos-alarma/<tipo_alarma_id>', methods=['DELETE'])
@require_super_admin_token
def delete_tipo_alarma(tipo_alarma_id):
    """Elimina un tipo de alarma"""
    result = tipo_alarma_service.delete_tipo_alarma(tipo_alarma_id)
    return jsonify(result), _status_from_result(result, success_code=200)


@tipo_alarma_bp.route('/tipos-alarma/<tipo_alarma_id>/toggle-status', methods=['PATCH'])
@require_super_admin_token
def toggle_tipo_alarma_status(tipo_alarma_id):
    """Alterna el estado activo/inactivo de un tipo de alarma"""
    result = tipo_alarma_service.toggle_tipo_alarma_status(tipo_alarma_id)
    return jsonify(result), _status_from_result(result)


@tipo_alarma_bp.route('/tipos-alarma/empresa/<empresa_id>', methods=['GET'])
@require_empresa_or_admin_token
def list_tipos_alarma_by_empresa(empresa_id):
    """Obtiene tipos de alarma asociados a una empresa específica"""
    page, limit = _get_pagination_params()
    exclude_globales = _should_exclude_globales()
    result = tipo_alarma_service.get_tipos_alarma_by_empresa(
        empresa_id,
        page=page,
        limit=limit,
        exclude_globales=exclude_globales
    )
    return jsonify(result), _status_from_result(result)


@tipo_alarma_bp.route('/tipos-alarma/empresa/<empresa_id>/todos', methods=['GET'])
def list_tipos_alarma_by_empresa_full(empresa_id):
    """GET /api/tipos-alarma/empresa/<empresa_id>/todos - Lista sin paginación (SIN AUTENTICACIÓN)"""
    solo_activos_raw = (request.args.get('solo_activos') or '').strip().lower()
    solo_activos = solo_activos_raw in ('true', '1', 'yes', 'on')
    exclude_globales = _should_exclude_globales()
    result = tipo_alarma_service.get_tipos_alarma_by_empresa_full(
        empresa_id,
        solo_activos=solo_activos,
        exclude_globales=exclude_globales
    )
    return jsonify(result), _status_from_result(result)


@tipo_alarma_bp.route('/tipos-alarma/tipo-alerta/<tipo_alerta>', methods=['GET'])
@require_empresa_or_admin_token
def list_tipos_alarma_by_tipo_alerta(tipo_alerta):
    """Obtiene tipos de alarma filtrados por tipo de alerta"""
    page, limit = _get_pagination_params()
    exclude_globales = _should_exclude_globales()
    result = tipo_alarma_service.get_tipos_alarma_by_tipo_alerta(
        tipo_alerta.upper(),
        page=page,
        limit=limit,
        exclude_globales=exclude_globales
    )
    return jsonify(result), _status_from_result(result)


@tipo_alarma_bp.route('/tipos-alarma/activos', methods=['GET'])
@require_empresa_or_admin_token
def list_tipos_alarma_activos():
    """Obtiene únicamente tipos de alarma activos"""
    page, limit = _get_pagination_params()
    exclude_globales = _should_exclude_globales()
    result = tipo_alarma_service.get_active_tipos_alarma(
        page=page,
        limit=limit,
        exclude_globales=exclude_globales
    )
    return jsonify(result), _status_from_result(result)


@tipo_alarma_bp.route('/tipos-alarma/inactivos', methods=['GET'])
@require_empresa_or_admin_token
def list_tipos_alarma_inactivos():
    """Obtiene únicamente tipos de alarma inactivos"""
    page, limit = _get_pagination_params()
    exclude_globales = _should_exclude_globales()
    result = tipo_alarma_service.get_inactive_tipos_alarma(
        page=page,
        limit=limit,
        exclude_globales=exclude_globales
    )
    return jsonify(result), _status_from_result(result)


@tipo_alarma_bp.route('/tipos-alarma/search', methods=['GET'])
@require_empresa_or_admin_token
def search_tipos_alarma():
    """Busca tipos de alarma por nombre o descripción"""
    query = request.args.get('query', '')
    page, limit = _get_pagination_params()
    exclude_globales = _should_exclude_globales()
    result = tipo_alarma_service.search_tipos_alarma(
        query,
        page=page,
        limit=limit,
        exclude_globales=exclude_globales
    )
    return jsonify(result), _status_from_result(result)


@tipo_alarma_bp.route('/tipos-alarma/stats', methods=['GET'])
@require_super_admin_token
def get_tipos_alarma_stats():
    """Obtiene estadísticas de los tipos de alarma registrados"""
    result = tipo_alarma_service.get_tipos_alarma_stats()
    return jsonify(result), _status_from_result(result)


@tipo_alarma_bp.route('/tipos-alarma/tipos-alerta', methods=['GET'])
@require_empresa_or_admin_token
def get_tipos_alerta_disponibles():
    """Devuelve la lista de valores permitidos para tipo_alerta"""
    result = tipo_alarma_service.get_tipos_alerta_disponibles()
    return jsonify(result), _status_from_result(result)
