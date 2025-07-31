#!/usr/bin/env python3

import os
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

# print("🔍 LEYENDO DIRECTAMENTE DEL .env:")
# print(f"RESEND_API_KEY: {os.getenv('RESEND_API_KEY')}")
# print(f"CONTACT_EMAIL: {os.getenv('CONTACT_EMAIL')}")
# print(f"RESEND_DOMAIN: {os.getenv('RESEND_DOMAIN')}")

# Verificar contenido del archivo .env directamente
# print("\n📄 CONTENIDO DIRECTO DEL ARCHIVO .env:")
try:
    with open('.env', 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines, 1):
            if any(key in line for key in ['RESEND_API_KEY', 'CONTACT_EMAIL', 'RESEND_DOMAIN']):
                # print(f"   Línea {i}: {line.strip()}")
except Exception as e:
    # print(f"Error leyendo .env: {e}")
