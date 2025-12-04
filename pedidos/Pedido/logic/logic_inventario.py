import requests
from django.conf import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Usar la URL directa del microservicio de inventario
INVENTARIO_URL = getattr(settings, 'INVENTARIO_URL', 'http://inventario:8000')

def get_bodegas(headers: Optional[dict] = None):
    try:
        response = requests.get(f"{INVENTARIO_URL}/bodegas/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and data.get('codigo') == 'ERROR':
                return None
            return data
        return []
    except requests.RequestException as e:
        logger.error(f"Error obteniendo bodegas: {str(e)}")
        return []

def get_item(sku, headers: Optional[dict] = None):
    try:
        url = f"{INVENTARIO_URL}/items/sku/{sku}"
        logger.info(f"Consultando item en: {url} con headers: {headers}")
        response = requests.get(url, headers=headers, timeout=5)
        logger.info(f"Respuesta de inventario: status={response.status_code}, headers={response.headers}")
        logger.info(f"Respuesta body: {response.text}")
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error obteniendo item {sku}: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        logger.error(f"Error conectando a inventario para item {sku}: {str(e)}")
        return None

def get_producto(producto_codigo, headers: Optional[dict] = None):
    try:
        response = requests.get(
            f"{INVENTARIO_URL}/productos/{producto_codigo}",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        if response.status_code == 404:
            return None
        logger.error(
            "Error obteniendo producto %s: %s - %s",
            producto_codigo,
            response.status_code,
            response.text
        )
        return None
    except requests.RequestException as e:
        logger.error("Error conectando a inventario para producto %s: %s", producto_codigo, str(e))
        return None


def get_bodega(bodega_id, headers: Optional[dict] = None):
    try:
        response = requests.get(f"{INVENTARIO_URL}/bodegas/{bodega_id}", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error obteniendo bodega {bodega_id}: {response.status_code}")
            return None
    except requests.RequestException as e:
        logger.error(f"Error conectando a inventario para bodega {bodega_id}: {str(e)}")
        return None


def get_items_disponibles_por_producto(producto_codigo, bodega_id, headers: Optional[dict] = None):
    """Obtiene el listado de items disponibles para un producto en una bodega."""
    try:
        params = {
            "codigo_barras": producto_codigo,
            "bodega_id": bodega_id
        }
        response = requests.get(
            f"{INVENTARIO_URL}/items/itemsDisponibles",
            headers=headers,
            params=params,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("items_disponibles", [])
        logger.error(
            "Error obteniendo items disponibles para producto %s en bodega %s: %s - %s",
            producto_codigo,
            bodega_id,
            response.status_code,
            response.text
        )
        return None
    except requests.RequestException as e:
        logger.error(
            "Error conectando a inventario para producto %s en bodega %s: %s",
            producto_codigo,
            bodega_id,
            str(e)
        )
        return None
