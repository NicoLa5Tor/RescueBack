import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'rescue')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', 'admin-token')
    SUPER_ADMIN_TOKEN = os.getenv('SUPER_ADMIN_TOKEN', 'super-token')
    EMPRESA_TOKEN = os.getenv('EMPRESA_TOKEN', 'empresa-token')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
