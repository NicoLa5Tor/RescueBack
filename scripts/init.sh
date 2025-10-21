#!/bin/sh
# Script de inicialización: espera la base y crea el admin antes de iniciar la app
# Usa /bin/sh para mayor compatibilidad en contenedores Alpine/slim

echo "🔧 Inicializando aplicación Rescue Backend..."
echo "========================================"
echo "📍 MONGO_URI: ${MONGO_URI}"
echo "📍 DATABASE_NAME: ${DATABASE_NAME}"
echo "========================================"

# Función para esperar a que MongoDB esté disponible
wait_for_mongo() {
    echo "⏳ Esperando a que MongoDB esté disponible..."
    max_attempts=60  # Aumentamos a 60 intentos (2 minutos)
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        # Intentar conectar usando pymongo directamente
        if python -c "
import sys
from pymongo import MongoClient
import os

try:
    uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
    client = MongoClient(uri, serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    print('✅ MongoDB conectado exitosamente')
    sys.exit(0)
except Exception as e:
    print(f'⏳ Esperando MongoDB... Error: {e}')
    sys.exit(1)
" 2>&1; then
            echo "✅ MongoDB está disponible y respondiendo"
            return 0
        fi
        echo "   MongoDB no está listo, intento $((attempt + 1))/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ MongoDB no pudo conectarse después de $max_attempts intentos"
    echo "   Verifica que el servicio mongodb esté corriendo"
    exit 1
}

# Esperar a MongoDB
wait_for_mongo

# Ejecutar script de administrador
echo "👤 Verificando administrador por defecto..."
cd /app && python -c "
import sys
sys.path.append('/app')
from scripts.init_admin import init_admin
try:
    init_admin()
    print('✅ Administrador inicializado correctamente')
except Exception as e:
    print(f'⚠️ Error inicializando administrador: {e}')
"
if [ $? -eq 0 ]; then
    echo "✅ Administrador listo"
else
    echo "⚠️  Error al preparar el administrador, continuando..."
fi

echo "🚀 Iniciando aplicación con Gunicorn..."
echo "========================================"

# Iniciar la aplicación con Gunicorn (configuración de producción)
exec gunicorn \
    --bind 0.0.0.0:5002 \
    --workers 3 \
    --worker-class sync \
    --timeout 60 \
    --keep-alive 2 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    "app:create_app()"
