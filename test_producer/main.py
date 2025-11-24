from fastapi import FastAPI, Request
import pika, json, os
from datetime import datetime

app = FastAPI()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
QUEUE_NAME = "audit_queue"

user = os.getenv("RABBITMQ_USER", "admin")
password = os.getenv("RABBITMQ_PASS", "admin")

credentials = pika.PlainCredentials(user, password)

def send_audit_event(event: dict):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST, 
            credentials=credentials,
            heartbeat=30,
            blocked_connection_timeout=300
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    
    body = json.dumps(event, indent=4, sort_keys=True, default=str)


    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=body,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
    
    
@app.post("/test-event")
async def send_test_event(request: Request):
    """
    Endpoint para enviar un evento de auditoría de prueba a RabbitMQ.
    """
    data = await request.json()
    
    event = {
                "timestamp": datetime.now().isoformat(),
                "user_id": "123",
                "audited_service_id": "2",
                "action": "CREATE",
                "description": "Se ha creado un producto",
                "entity": "PRODUCT",
                "entity_id": "14",
                "metadata": {
                    "new": {
                        "codigo_barras": "1234567890123",
                        "tipo": "Ropa",
                        "nombre": "Camiseta",
                        "descripcion": "Camiseta de algodón, manga corta",
                        "precio": 19.99,
                    }
                },
                "ip": "127.168.1.1"
            }
    send_audit_event(event)
    return {"message": "Audit event sent", "event": event}