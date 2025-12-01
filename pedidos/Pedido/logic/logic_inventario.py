import requests
from django.conf import settings

INVENTARIO_URL = getattr(settings, 'INVENTARIO_URL', 'http://inventario:8000')

def get_bodegas():
    try:
        response = requests.get(f"{INVENTARIO_URL}/bodegas/")
        if response.status_code == 200:
            return response.json()
        return []
    except requests.RequestException:
        return []

def get_item(sku):
    try:
        response = requests.get(f"{INVENTARIO_URL}/items/{sku}")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None

def get_bodega(bodega_id):
    try:
        response = requests.get(f"{INVENTARIO_URL}/bodegas/{bodega_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None
