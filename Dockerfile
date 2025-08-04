# ==========================================
# Dockerfile para RESCUE Backend
# Flask + MongoDB
# ==========================================

FROM python:3.11-slim

# Información del mantenedor
LABEL maintainer="RESCUE Team"
LABEL description="Backend Flask para sistema RESCUE con MongoDB"
LABEL version="1.0"

# Variables de entorno optimizadas
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear usuario no-root para seguridad
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-compile --upgrade pip \
    && pip install --no-compile -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios y ajustar permisos
RUN mkdir -p /app/logs /app/tmp \
    && chown -R appuser:appgroup /app \
    && chmod -R 755 /app \
    && find /app -name "*.py" -exec chmod 644 {} \;

# Cambiar a usuario no-root
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:5002/health || exit 1

# Exponer puerto
EXPOSE 5002

# Configuración optimizada de Gunicorn para producción
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5002", \
     "--workers", "3", \
     "--worker-class", "sync", \
     "--worker-connections", "1000", \
     "--timeout", "60", \
     "--keep-alive", "2", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50", \
     "--preload", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "app:create_app()"]
