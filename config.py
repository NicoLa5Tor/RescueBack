import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'rescue')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'ya-que-el-amor')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_DELTA = timedelta(hours=8)
    
    ROLES = {
        'SUPER_ADMIN': 'super_admin',
        'EMPRESA': 'empresa'
    }
    
    PERMISSIONS = {
        'super_admin': [
            'crear_empresas',
            'editar_empresas', 
            'eliminar_empresas',
            'ver_todas_empresas',
            'ver_estadisticas_globales',
            'gestionar_administradores'
        ],
        'empresa': [
            'crear_usuarios',
            'editar_usuarios_propios',
            'eliminar_usuarios_propios',
            'ver_usuarios_propios',
            'editar_perfil_empresa'
        ]
    }