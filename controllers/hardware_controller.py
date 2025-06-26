from flask import request, jsonify
from services.hardware_service import HardwareService
from utils.permissions import require_empresa_or_admin_token

class HardwareController:
    def __init__(self):
        self.service = HardwareService()

    @require_empresa_or_admin_token
    def create_hardware(self):
        try:
            data = request.get_json() or {}
            result = self.service.create_hardware(data)
            status = 201 if result.get('success') else 400
            return jsonify(result), status
        except Exception as exc:
            return jsonify({'success': False, 'errors': [str(exc)]}), 500

    @require_empresa_or_admin_token
    def get_hardware_list(self):
        try:
            result = self.service.get_all_hardware()
            status = 200 if result.get('success') else 500
            return jsonify(result), status
        except Exception as exc:
            return jsonify({'success': False, 'errors': [str(exc)]}), 500

    @require_empresa_or_admin_token
    def get_hardware(self, hardware_id):
        try:
            result = self.service.get_hardware(hardware_id)
            status = 200 if result.get('success') else 404
            return jsonify(result), status
        except Exception as exc:
            return jsonify({'success': False, 'errors': [str(exc)]}), 500

    @require_empresa_or_admin_token
    def update_hardware(self, hardware_id):
        try:
            data = request.get_json() or {}
            result = self.service.update_hardware(hardware_id, data)
            status = 200 if result.get('success') else 400
            return jsonify(result), status
        except Exception as exc:
            return jsonify({'success': False, 'errors': [str(exc)]}), 500

    @require_empresa_or_admin_token
    def delete_hardware(self, hardware_id):
        try:
            result = self.service.delete_hardware(hardware_id)
            status = 200 if result.get('success') else 404
            return jsonify(result), status
        except Exception as exc:
            return jsonify({'success': False, 'errors': [str(exc)]}), 500

    @require_empresa_or_admin_token
    def get_hardware_by_empresa(self, empresa_id):
        try:
            result = self.service.get_hardware_by_empresa(empresa_id)
            status = 200 if result.get('success') else 404
            return jsonify(result), status
        except Exception as exc:
            return jsonify({'success': False, 'errors': [str(exc)]}), 500
