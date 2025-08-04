from pymongo import MongoClient
from .config import Config

class Database:
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        """Establece conexión con MongoDB"""
        try:
            if self._client is None:
                self._client = MongoClient(Config.MONGO_URI)
                self._db = self._client[Config.DATABASE_NAME]
                # print(f"Conectado a MongoDB: {Config.DATABASE_NAME}")
            return self._db
        except Exception as e:
            # print(f"Error conectando a MongoDB: {e}")
            raise e
    
    def get_database(self):
        """Retorna la instancia de la base de datos"""
        if self._db is None:
            self.connect()
        return self._db
    
    def close_connection(self):
        """Cierra la conexión a MongoDB"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            # print("Conexión a MongoDB cerrada")
    
    def test_connection(self):
        """Prueba la conexión a MongoDB"""
        try:
            if self._client is None:
                self.connect()
            # Usar el cliente para hacer ping al servidor
            self._client.admin.command('ping')
            return True
        except Exception as e:
            # print(f"Error en test de conexión: {e}")
            return False