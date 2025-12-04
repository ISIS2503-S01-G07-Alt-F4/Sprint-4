import requests
from django.conf import settings

AUDITORIA_URL = getattr(settings, 'AUDITORIA_URL', 'http://localhost:8000/auditoria')

def enviar_evento_auditoria(user_data, action, entity, entity_id, description, metadata=None):
    """
    Envía un evento de auditoría al microservicio de Auditoría.
    """
    try:
        payload = {
            'user_id': str(user_data.get('id') or user_data.get('username') or 'unknown'),
            'audited_service_id': 'pedidos',
            'action': action,
            'description': description,
            'entity': entity,
            'entity_id': str(entity_id),
            'metadata': metadata or {},
        }
        resp = requests.post(f"{AUDITORIA_URL}/audit-logs/", json=payload, timeout=5)
        return resp.status_code in (200, 201)
    except requests.RequestException:
        return False
