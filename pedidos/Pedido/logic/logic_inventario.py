import requests
from django.conf import settings
from typing import Optional

# Usar Kong como API Gateway. `INVENTARIO_URL` ya está ensamblado en settings
INVENTARIO_URL = getattr(settings, 'INVENTARIO_URL', 'http://kong:8000/inventario')

def get_bodegas(headers: Optional[dict] = None):
    try:
        response = requests.get(f"{INVENTARIO_URL}/bodegas/", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.RequestException:
        return []

def get_item(sku, headers: Optional[dict] = None):
    try:
        response = requests.get(f"{INVENTARIO_URL}/items/{sku}", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None

def get_bodega(bodega_id, headers: Optional[dict] = None):
    try:
        response = requests.get(f"{INVENTARIO_URL}/bodegas/{bodega_id}", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None
