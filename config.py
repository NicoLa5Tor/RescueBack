import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'ECOES')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', 'admin-token')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
