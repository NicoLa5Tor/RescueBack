from flask import request, jsonify
from services.hardware_type_service import HardwareTypeService
from utils.permissions import require_empresa_or_admin_token

class HardwareTypeController:
    def __init__(self):
        self.service = HardwareTypeService()

    @require_empresa_or_admin_token
    def create_type(self):
        data = request.get_json() or {}
        result = self.service.create_type(data)
        status = 201 if result.get('success') else 400
        return jsonify(result), status

    @require_empresa_or_admin_token
    def get_types(self):
        result = self.service.get_all_types()
        status = 200 if result.get('success') else 500
        return jsonify(result), status

    @require_empresa_or_admin_token
    def get_type(self, type_id):
        result = self.service.get_type(type_id)
        status = 200 if result.get('success') else 404
        return jsonify(result), status

    @require_empresa_or_admin_token
    def update_type(self, type_id):
        data = request.get_json() or {}
        result = self.service.update_type(type_id, data)
        status = 200 if result.get('success') else 400
        return jsonify(result), status

    @require_empresa_or_admin_token
    def delete_type(self, type_id):
        result = self.service.delete_type(type_id)
        status = 200 if result.get('success') else 404
        return jsonify(result), status
