import os
import json
import pika
import datetime

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "admin")
QUEUE_NAME = "audit_queue"

def send_audit_event(user_id: str, action: str, description: str, entity: str, entity_id: str, metadata: dict = None, ip: str = None):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        message = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_id": user_id,
            "audited_service_id": "INVENTARIO",
            "action": action,
            "description": description,
            "entity": entity,
            "entity_id": entity_id,
            "metadata": metadata or {},
            "ip": ip
        }

        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2
            ))
        
        print(f" [x] Sent audit event: {action} on {entity}")
        connection.close()
    except Exception as e:
        print(f"Failed to send audit event: {e}")
