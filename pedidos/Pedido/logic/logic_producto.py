import logging
from typing import Optional

import requests
from django.conf import settings

INVENTARIO_URL = getattr(settings, 'INVENTARIO_URL', 'http://inventario:8000')
logger = logging.getLogger(__name__)


def obtener_productos(headers: Optional[dict] = None):
    try:
        response = requests.get(f"{INVENTARIO_URL}/productos/", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        logger.error("No se pudieron obtener productos: %s - %s", response.status_code, response.text)
    except requests.RequestException as exc:
        logger.error("Error consultando productos en inventario: %s", exc)
    return []


def registrar_producto(data: dict, headers: Optional[dict] = None):
    try:
        response = requests.post(
            f"{INVENTARIO_URL}/productos/",
            json=data,
            headers=headers,
            timeout=5,
        )
        if response.status_code in (200, 201):
            return response.json()
        raise ValueError(response.json().get('message') or response.text)
    except requests.RequestException as exc:
        logger.error("Error creando producto en inventario: %s", exc)
        raise ValueError("No fue posible crear el producto en el microservicio de inventario") from exc