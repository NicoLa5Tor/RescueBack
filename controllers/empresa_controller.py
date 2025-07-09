from flask import request, jsonify, g
from services.empresa_service import EmpresaService
from utils.permissions import require_super_admin_token, require_empresa_or_admin_token
from flask_jwt_extended import verify_jwt_in_request, get_jwt
import logging

# Configurar logger
logger = logging.getLogger(__name__)


class EmpresaController:
    def __init__(self):
        self.empresa_service = EmpresaService()

    @require_super_admin_token
    def create_empresa(self):
        """Endpoint para crear una empresa (solo super admin)"""
        try:
            data = request.get_json()

            if not data:
                return (
                    jsonify({"success": False, "errors": ["No se enviaron datos"]}),
                    400,
                )

            # Obtener el ID del super admin del contexto
            super_admin_id = g.user_id

            result = self.empresa_service.create_empresa(data, super_admin_id)

            if result["success"]:
                return (
                    jsonify(
                        {
                            "success": True,
                            "message": result.get(
                                "message", "Empresa creada correctamente"
                            ),
                            "data": result["data"],
                        }
                    ),
                    201,
                )
            else:
                return jsonify(result), 400

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "errors": [f"Error interno del servidor: {str(e)}"],
                    }
                ),
                500,
            )

    def get_empresa(self, empresa_id):
        """Endpoint para obtener una empresa por ID"""
        try:
            result = self.empresa_service.get_empresa_by_id(empresa_id)

            if result["success"]:
                return jsonify({"success": True, "data": result["data"]}), 200
            else:
                return jsonify(result), 404

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "errors": [f"Error interno del servidor: {str(e)}"],
                    }
                ),
                500,
            )

    def get_all_empresas(self):
        """Endpoint para obtener todas las empresas activas (para formularios)"""
        try:
            logger.info("=== GET ALL EMPRESAS (SOLO ACTIVAS) ===")
            
            # Solo empresas activas para formularios
            result = self.empresa_service.get_all_empresas(include_inactive=False)
            
            logger.info(f"Empresas activas obtenidas: {result.get('count', 0)}")
            if result["success"] and result["data"]:
                logger.info(f"Primeras empresas: {[e.get('nombre', 'N/A') for e in result['data'][:3]]}")

            if result["success"]:
                return (
                    jsonify(
                        {
                            "success": True,
                            "data": result["data"],
                            "count": result["count"],
                        }
                    ),
                    200,
                )
            else:
                return jsonify(result), 500

        except Exception as e:
            logger.error(f"Error en get_all_empresas: {str(e)}")
            return (
                jsonify(
                    {
                        "success": False,
                        "errors": [f"Error interno del servidor: {str(e)}"],
                    }
                ),
                500,
            )

    def get_all_empresas_dashboard(self):
        """Endpoint para obtener TODAS las empresas (activas e inactivas) para dashboards"""
        try:
            logger.info("=== GET ALL EMPRESAS DASHBOARD (TODAS) ===")
            
            # Obtener TODAS las empresas (activas e inactivas) para dashboards
            result = self.empresa_service.get_all_empresas(include_inactive=True)
            print(f"Empresas son: {result}")
            logger.info(f"Total empresas (activas e inactivas): {result.get('count', 0)}")
            if result["success"] and result["data"]:
                activas = [e for e in result["data"] if e.get("activa", True)]
                inactivas = [e for e in result["data"] if not e.get("activa", True)]
                logger.info(f"Empresas activas: {len(activas)}, inactivas: {len(inactivas)}")
                logger.info(f"Primeras empresas: {[f'{e.get("nombre", "N/A")} (activa: {e.get("activa", True)})' for e in result['data'][:5]]}")

            if result["success"]:
                return (
                    jsonify(
                        {
                            "success": True,
                            "data": result["data"],
                            "count": result["count"],
                        }
                    ),
                    200,
                )
            else:
                logger.error(f"Error en servicio: {result}")
                return jsonify(result), 500

        except Exception as e:
            logger.error(f"Error en get_all_empresas_dashboard: {str(e)}")
            return (
                jsonify(
                    {
                        "success": False,
                        "errors": [f"Error interno del servidor: {str(e)}"],
                    }
                ),
                500,
            )

    @require_super_admin_token
    def get_my_empresas(self):
        """Endpoint para obtener empresas creadas por el super admin autenticado"""
        try:
            super_admin_id = g.user_id
            result = self.empresa_service.get_empresas_by_creador(super_admin_id)

            if result["success"]:
                return (
                    jsonify(
                        {
                            "success": True,
                            "data": result["data"],
                            "count": result["count"],
                        }
                    ),
                    200,
                )
            else:
                return jsonify(result), 500

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "errors": [f"Error interno del servidor: {str(e)}"],
                    }
                ),
                500,
            )

    @require_empresa_or_admin_token
    def update_empresa(self, empresa_id):
        """Endpoint para actualizar una empresa"""
        try:
            data = request.get_json()

            if not data:
                return (
                    jsonify({"success": False, "errors": ["No se enviaron datos"]}),
                    400,
                )

            super_admin_id = g.user_id if g.role == "super_admin" else None
            result = self.empresa_service.update_empresa(
                empresa_id, data, super_admin_id
            )

            if result["success"]:
                return (
                    jsonify(
                        {
                            "success": True,
                            "message": result.get(
                                "message", "Empresa actualizada correctamente"
                            ),
                            "data": result["data"],
                        }
                    ),
                    200,
                )
            else:
                return jsonify(result), 400

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "errors": [f"Error interno del servidor: {str(e)}"],
                    }
                ),
                500,
            )

    @require_super_admin_token
    def delete_empresa(self, empresa_id):
        """Endpoint para eliminar una empresa (solo el creador)"""
        try:
            super_admin_id = g.user_id
            result = self.empresa_service.delete_empresa(empresa_id, super_admin_id)

            if result["success"]:
                return jsonify({"success": True, "message": result["message"]}), 200
            else:
                return jsonify(result), 404

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "errors": [f"Error interno del servidor: {str(e)}"],
                    }
                ),
                500,
            )

    def search_empresas_by_ubicacion(self):
        """Endpoint para buscar empresas por ubicación"""
        try:
            ubicacion = request.args.get("ubicacion")

            if not ubicacion:
                return (
                    jsonify(
                        {
                            "success": False,
                            "errors": ["El parámetro ubicacion es obligatorio"],
                        }
                    ),
                    400,
                )

            result = self.empresa_service.search_empresas_by_ubicacion(ubicacion)

            if result["success"]:
                return (
                    jsonify(
                        {
                            "success": True,
                            "data": result["data"],
                            "count": result["count"],
                        }
                    ),
                    200,
                )
            else:
                return jsonify(result), 500

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "errors": [f"Error interno del servidor: {str(e)}"],
                    }
                ),
                500,
            )

    @require_super_admin_token
    def get_empresa_stats(self):
        """Endpoint para obtener estadísticas de empresas (solo super admin)"""
        try:
            result = self.empresa_service.get_empresa_stats()

            if result["success"]:
                return jsonify({"success": True, "data": result["data"]}), 200
            else:
                return jsonify(result), 500

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "errors": [f"Error interno del servidor: {str(e)}"],
                    }
                ),
                500,
            )
    
    @require_super_admin_token
    def get_empresa_including_inactive(self, empresa_id):
        """Endpoint para obtener una empresa por ID incluyendo inactivas (solo super admin)"""
        try:
            result = self.empresa_service.get_empresa_by_id_including_inactive(empresa_id)

            if result["success"]:
                return jsonify({"success": True, "data": result["data"]}), 200
            else:
                return jsonify(result), 404

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "errors": [f"Error interno del servidor: {str(e)}"],
                    }
                ),
                500,
            )
    
    @require_super_admin_token
    def toggle_empresa_status(self, empresa_id):
        """Endpoint para activar/desactivar empresa (solo super admin)"""
        try:
            data = request.get_json() or {}
            activa = data.get('activa', True)
            super_admin_id = g.user_id
            
            result = self.empresa_service.toggle_empresa_status(empresa_id, activa, super_admin_id)

            if result["success"]:
                return (
                    jsonify(
                        {
                            "success": True,
                            "message": result.get("message", "Estado de empresa actualizado"),
                            "data": result["data"],
                        }
                    ),
                    200,
                )
            else:
                return jsonify(result), 400

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "errors": [f"Error interno del servidor: {str(e)}"],
                    }
                ),
                500,
            )
