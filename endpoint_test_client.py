# -*- coding: utf-8 -*-
"""Herramienta sencilla para probar los endpoints de la API.

Esta clase permite probar cada endpoint de manera individual enviando
peticiones HTTP a la aplicación Flask. El token de autenticación se
proporciona en el constructor y se incluye automáticamente en las
peticiones protegidas.
"""

from typing import Any, Dict, Optional
import json
import requests


class EndpointTestClient:
    """Cliente para realizar pruebas sobre los endpoints de la API.

    Parameters
    ----------
    base_url: str
        URL base donde se encuentra ejecutada la API.
    token: str, optional
        Token JWT de la empresa o del administrador a utilizar en las
        peticiones autenticadas.
    """

    def __init__(self, base_url: str = "http://localhost:5000", token: Optional[str] = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token

    # ------------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------------
    def _headers(self) -> Dict[str, str]:
        """Genera los encabezados para la petición HTTP."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method: str, endpoint: str, *, params: Optional[Dict[str, Any]] = None,
                 data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Realiza una petición HTTP y devuelve la respuesta cruda."""
        url = f"{self.base_url}{endpoint}"
        return requests.request(method, url, params=params, json=data, headers=self._headers())

    # ------------------------------------------------------------------
    # Endpoints de autenticación y salud
    # ------------------------------------------------------------------
    def login(self, usuario: str, password: str) -> requests.Response:
        """POST /auth/login

        Ejemplo de body
        ----------------
        ```json
        {
            "usuario": "superadmin",
            "password": "secreto"
        }
        ```
        """
        return self._request("POST", "/auth/login", data={"usuario": usuario, "password": password})

    def health(self) -> requests.Response:
        """GET /health"""
        return self._request("GET", "/health")

    def index(self) -> requests.Response:
        """GET /"""
        return self._request("GET", "/")

    # ------------------------------------------------------------------
    # Endpoints de usuarios
    # ------------------------------------------------------------------
    def create_user(self, data: Dict[str, Any]) -> requests.Response:
        """POST /api/users

        Ejemplo de body
        ----------------
        ```json
        {
            "name": "Juan",
            "email": "juan@example.com",
            "age": 25,
            "empresa_id": "<id_empresa>",
            "telefono": "3001234567"
        }
        ```
        """
        return self._request("POST", "/api/users", data=data)

    def get_users(self) -> requests.Response:
        """GET /api/users"""
        return self._request("GET", "/api/users")

    def get_user(self, user_id: str) -> requests.Response:
        """GET /api/users/<user_id>"""
        return self._request("GET", f"/api/users/{user_id}")

    def update_user(self, user_id: str, data: Dict[str, Any]) -> requests.Response:
        """PUT /api/users/<user_id>

        Ejemplo de body
        ----------------
        ```json
        {
            "name": "Nuevo Nombre",
            "email": "nuevo@email.com",
            "age": 30,
            "empresa_id": "<id_empresa>",
            "telefono": "3110000000",
            "whatsapp_verify": true
        }
        ```
        """
        return self._request("PUT", f"/api/users/{user_id}", data=data)

    def delete_user(self, user_id: str) -> requests.Response:
        """DELETE /api/users/<user_id>"""
        return self._request("DELETE", f"/api/users/{user_id}")

    def get_users_by_age(self, min_age: int, max_age: int) -> requests.Response:
        """GET /api/users/age-range"""
        params = {"min_age": min_age, "max_age": max_age}
        return self._request("GET", "/api/users/age-range", params=params)

    def get_user_by_phone(self, telefono: str) -> requests.Response:
        """GET /api/users/buscar-por-telefono"""
        return self._request("GET", "/api/users/buscar-por-telefono", params={"telefono": telefono})

    # ------------------------------------------------------------------
    # Endpoints de empresas
    # ------------------------------------------------------------------
    def create_empresa(self, data: Dict[str, Any]) -> requests.Response:
        """POST /api/empresas

        Ejemplo de body
        ----------------
        ```json
        {
            "nombre": "Mi Empresa",
            "descripcion": "Empresa de ejemplo",
            "ubicacion": "Bogotá",
            "sedes": ["Principal"],
            "username": "miempresa",
            "email": "empresa@example.com",
            "password": "secreto"
        }
        ```
        """
        return self._request("POST", "/api/empresas", data=data)

    def get_empresas(self, include_inactive: bool = False) -> requests.Response:
        """GET /api/empresas"""
        params = {"include_inactive": str(include_inactive).lower()} if include_inactive else None
        return self._request("GET", "/api/empresas", params=params)

    def get_empresa(self, empresa_id: str) -> requests.Response:
        """GET /api/empresas/<empresa_id>"""
        return self._request("GET", f"/api/empresas/{empresa_id}")

    def update_empresa(self, empresa_id: str, data: Dict[str, Any]) -> requests.Response:
        """PUT /api/empresas/<empresa_id>

        Ejemplo de body
        ----------------
        ```json
        {
            "nombre": "Nuevo Nombre",
            "descripcion": "Nueva descripcion",
            "ubicacion": "Medellín",
            "sedes": ["Sucursal 1"],
            "username": "miempresa",
            "email": "empresa@example.com",
            "password": "nuevo"
        }
        ```
        """
        return self._request("PUT", f"/api/empresas/{empresa_id}", data=data)

    def delete_empresa(self, empresa_id: str) -> requests.Response:
        """DELETE /api/empresas/<empresa_id>"""
        return self._request("DELETE", f"/api/empresas/{empresa_id}")

    def get_my_empresas(self) -> requests.Response:
        """GET /api/empresas/mis-empresas"""
        return self._request("GET", "/api/empresas/mis-empresas")

    def search_empresas_by_ubicacion(self, ubicacion: str) -> requests.Response:
        """GET /api/empresas/buscar-por-ubicacion"""
        return self._request("GET", "/api/empresas/buscar-por-ubicacion", params={"ubicacion": ubicacion})

    def get_empresa_stats(self) -> requests.Response:
        """GET /api/empresas/estadisticas"""
        return self._request("GET", "/api/empresas/estadisticas")

    def get_empresa_activity(self, empresa_id: str) -> requests.Response:
        """GET /api/empresas/<empresa_id>/activity - Ver logs de esa empresa"""
        return self._request("GET", f"/api/empresas/{empresa_id}/activity")

    # ------------------------------------------------------------------
    # Endpoints de administración
    # ------------------------------------------------------------------
    def get_admin_activity(self) -> requests.Response:
        """GET /api/admin/activity - Ver logs de todas las empresas"""
        return self._request("GET", "/api/admin/activity")

    def get_admin_activity_only(self) -> requests.Response:
        """GET /api/admin/activity-admin - Ver logs solo para admins"""
        return self._request("GET", "/api/admin/activity-admin")

    def get_admin_distribution(self) -> requests.Response:
        """GET /api/admin/distribution"""
        return self._request("GET", "/api/admin/distribution")

    # ------------------------------------------------------------------
    # Endpoints de hardware
    # ------------------------------------------------------------------
    def create_hardware(self, data: Dict[str, Any]) -> requests.Response:
        """POST /api/hardware

        Ejemplo de body
        ----------------
        ```json
        {
            "empresa_nombre": "Mi Empresa",
            "nombre": "HW1",
            "tipo": "botonera",
            "sede": "principal"
        }
        ```
        """
        return self._request("POST", "/api/hardware", data=data)

    def get_hardware_list(self) -> requests.Response:
        """GET /api/hardware"""
        return self._request("GET", "/api/hardware")

    def get_hardware_by_empresa(self, empresa_id: str) -> requests.Response:
        """GET /api/hardware/empresa/<empresa_id>"""
        return self._request("GET", f"/api/hardware/empresa/{empresa_id}")

    def get_hardware(self, hardware_id: str) -> requests.Response:
        """GET /api/hardware/<hardware_id>"""
        return self._request("GET", f"/api/hardware/{hardware_id}")

    def update_hardware(self, hardware_id: str, data: Dict[str, Any]) -> requests.Response:
        """PUT /api/hardware/<hardware_id>"""
        return self._request("PUT", f"/api/hardware/{hardware_id}", data=data)

    def delete_hardware(self, hardware_id: str) -> requests.Response:
        """DELETE /api/hardware/<hardware_id>"""
        return self._request("DELETE", f"/api/hardware/{hardware_id}")

    # ------------------------------------------------------------------
    # Endpoints de tipos de hardware
    # ------------------------------------------------------------------
    def create_hardware_type(self, data: Dict[str, Any]) -> requests.Response:
        """POST /api/hardware-types"""
        return self._request("POST", "/api/hardware-types", data=data)

    def get_hardware_types(self) -> requests.Response:
        """GET /api/hardware-types"""
        return self._request("GET", "/api/hardware-types")

    def get_hardware_type(self, type_id: str) -> requests.Response:
        """GET /api/hardware-types/<id>"""
        return self._request("GET", f"/api/hardware-types/{type_id}")

    def update_hardware_type(self, type_id: str, data: Dict[str, Any]) -> requests.Response:
        """PUT /api/hardware-types/<id>"""
        return self._request("PUT", f"/api/hardware-types/{type_id}", data=data)

    def delete_hardware_type(self, type_id: str) -> requests.Response:
        """DELETE /api/hardware-types/<id>"""
        return self._request("DELETE", f"/api/hardware-types/{type_id}")

    # ------------------------------------------------------------------
    # Endpoints multi-tenant
    # ------------------------------------------------------------------
    def create_usuario_for_empresa(self, empresa_id: str, data: Dict[str, Any]) -> requests.Response:
        """POST /empresas/<empresa_id>/usuarios

        Ejemplo de body
        ----------------
        ```json
        {
            "nombre": "Ana",
            "cedula": "123456",
            "rol": "operador"
        }
        ```
        """
        return self._request("POST", f"/empresas/{empresa_id}/usuarios", data=data)

    def get_usuarios_by_empresa(self, empresa_id: str) -> requests.Response:
        """GET /empresas/<empresa_id>/usuarios"""
        return self._request("GET", f"/empresas/{empresa_id}/usuarios")

    def get_usuario_by_empresa(self, empresa_id: str, usuario_id: str) -> requests.Response:
        """GET /empresas/<empresa_id>/usuarios/<usuario_id>"""
        endpoint = f"/empresas/{empresa_id}/usuarios/{usuario_id}"
        return self._request("GET", endpoint)

    def update_usuario_by_empresa(self, empresa_id: str, usuario_id: str, data: Dict[str, Any]) -> requests.Response:
        """PUT /empresas/<empresa_id>/usuarios/<usuario_id>

        Ejemplo de body
        ----------------
        ```json
        {
            "nombre": "Nuevo Nombre",
            "cedula": "123456",
            "rol": "operador"
        }
        ```
        """
        endpoint = f"/empresas/{empresa_id}/usuarios/{usuario_id}"
        return self._request("PUT", endpoint, data=data)

    def delete_usuario_by_empresa(self, empresa_id: str, usuario_id: str) -> requests.Response:
        """DELETE /empresas/<empresa_id>/usuarios/<usuario_id>"""
        endpoint = f"/empresas/{empresa_id}/usuarios/{usuario_id}"
        return self._request("DELETE", endpoint)

    # ------------------------------------------------------------------
    # Utilidades públicas
    # ------------------------------------------------------------------
    def set_token(self, token: str) -> None:
        """Actualiza el token de autenticación para las próximas peticiones."""
        self.token = token

    def pretty_response(self, response: requests.Response) -> str:
        """Devuelve la respuesta formateada en JSON para impresión."""
        try:
            return json.dumps(response.json(), indent=2, ensure_ascii=False)
        except ValueError:
            return response.text
