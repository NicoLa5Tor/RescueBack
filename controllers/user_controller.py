from flask import request, jsonify
from services.user_service import UserService

class UserController:
    def __init__(self):
        self.user_service = UserService()
    
    def create_user(self):
        """Endpoint para crear un usuario"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'errors': ['No se enviaron datos']
                }), 400
            
            result = self.user_service.create_user(data)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Usuario creado correctamente',
                    'data': result['data']
                }), 201
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500
    
    def get_user(self, user_id):
        """Endpoint para obtener un usuario por ID"""
        try:
            result = self.user_service.get_user_by_id(user_id)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'data': result['data']
                }), 200
            else:
                return jsonify(result), 404
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500
    
    def get_all_users(self):
        """Endpoint para obtener todos los usuarios"""
        try:
            result = self.user_service.get_all_users()
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'data': result['data'],
                    'count': result['count']
                }), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500

    def get_user_by_phone(self):
        """Endpoint para obtener un usuario por número de teléfono"""
        try:
            telefono = request.args.get('telefono')
            if not telefono:
                return jsonify({
                    'success': False,
                    'errors': ['El parámetro telefono es obligatorio']
                }), 400

            result = self.user_service.get_user_by_phone(telefono)

            if result['success']:
                return jsonify({
                    'success': True,
                    'data': result['data']
                }), 200
            else:
                return jsonify(result), 404

        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500
    
    def update_user(self, user_id):
        """Endpoint para actualizar un usuario"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'errors': ['No se enviaron datos']
                }), 400
            
            result = self.user_service.update_user(user_id, data)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Usuario actualizado correctamente',
                    'data': result['data']
                }), 200
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500
    
    def delete_user(self, user_id):
        """Endpoint para eliminar un usuario"""
        try:
            result = self.user_service.delete_user(user_id)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result['message']
                }), 200
            else:
                return jsonify(result), 404
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500
    
    def get_users_by_age(self):
        """Endpoint para obtener usuarios por rango de edad"""
        try:
            min_age = request.args.get('min_age', type=int)
            max_age = request.args.get('max_age', type=int)
            
            if min_age is None or max_age is None:
                return jsonify({
                    'success': False,
                    'errors': ['Los parámetros min_age y max_age son obligatorios']
                }), 400
            
            if min_age < 0 or max_age < 0 or min_age > max_age:
                return jsonify({
                    'success': False,
                    'errors': ['Los parámetros de edad deben ser válidos']
                }), 400
            
            result = self.user_service.get_users_by_age_range(min_age, max_age)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'data': result['data'],
                    'count': result['count']
                }), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [f'Error interno del servidor: {str(e)}']
            }), 500