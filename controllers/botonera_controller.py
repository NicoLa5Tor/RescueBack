from flask import request, jsonify
from services.botonera_service import BotoneraService
from utils.permissions import require_empresa_or_admin_token

class BotoneraController:
    def __init__(self):
        self.service = BotoneraService()

    @require_empresa_or_admin_token
    def create_botonera(self):
        try:
            data = request.get_json() or {}
            result = self.service.create_botonera(data)
            status = 201 if result.get('success') else 400
            return jsonify(result), status
        except Exception as exc:
            return jsonify({'success': False, 'errors': [str(exc)]}), 500
    
    

    @require_empresa_or_admin_token
    def get_botoneras(self):
        try:
            result = self.service.get_all_botoneras()
            status = 200 if result.get('success') else 500
            return jsonify(result), status
        except Exception as exc:
            return jsonify({'success': False, 'errors': [str(exc)]}), 500

    @require_empresa_or_admin_token
    def get_botonera(self, botonera_id):
        try:
            result = self.service.get_botonera(botonera_id)
            status = 200 if result.get('success') else 404
            return jsonify(result), status
        except Exception as exc:
            return jsonify({'success': False, 'errors': [str(exc)]}), 500
    

    @require_empresa_or_admin_token
    def update_botonera(self, botonera_id):
        try:
            data = request.get_json() or {}
            result = self.service.update_botonera(botonera_id, data)
            status = 200 if result.get('success') else 400
            return jsonify(result), status
        except Exception as exc:
            return jsonify({'success': False, 'errors': [str(exc)]}), 500
    

    @require_empresa_or_admin_token
    def delete_botonera(self, botonera_id):
        try:
            result = self.service.delete_botonera(botonera_id)
            status = 200 if result.get('success') else 404
            return jsonify(result), status
        except Exception as exc:
            return jsonify({'success': False, 'errors': [str(exc)]}), 500

    @require_empresa_or_admin_token
    def get_botoneras_by_empresa(self, empresa_id):
        try:
            result = self.service.get_botoneras_by_empresa(empresa_id)
            status = 200 if result.get('success') else 404
            return jsonify(result), status
        except Exception as exc:
            return jsonify({'success': False, 'errors': [str(exc)]}), 500
