#!/bin/bash
# Script de inicialización para ejecutar scripts y luego iniciar la aplicación

echo "🔧 Inicializando aplicación Rescue Backend..."
echo "=" * 50

# Función para esperar a que MongoDB esté disponible
wait_for_mongo() {
    echo "⏳ Esperando a que MongoDB esté disponible..."
    while ! python -c "from core.database import Database; db = Database(); exit(0 if db.test_connection() else 1)" 2>/dev/null; do
        echo "   MongoDB no está listo, esperando 2 segundos..."
        sleep 2
    done
    echo "✅ MongoDB está disponible"
}

# Esperar a MongoDB
wait_for_mongo

# Ejecutar script de tipos de alarma
echo "🎯 Ejecutando script de tipos de alarma..."
python /app/scripts/create_default_tipos_alarma.py
if [ $? -eq 0 ]; then
    echo "✅ Script de tipos de alarma completado"
else
    echo "⚠️  Error en script de tipos de alarma, continuando..."
fi

# Ejecutar script de administrador
echo "👤 Ejecutando script de administrador..."
python /app/scripts/init_admin.py
if [ $? -eq 0 ]; then
    echo "✅ Script de administrador completado"
else
    echo "⚠️  Error en script de administrador, continuando..."
fi

echo "🚀 Iniciando aplicación Flask..."
echo "=" * 50

# Iniciar la aplicación Flask
exec flask run --host=0.0.0.0 --port=5002
