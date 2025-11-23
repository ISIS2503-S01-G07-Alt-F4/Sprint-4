import os
import json
import pika
from models.audit_event import AuditEvent
from logic.logic_audit_logs import crear_log_auditoria

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "http://localhost:15672")
QUEUE_NAME = "audit_queue"

def callback(ch, method, properties, body):
    data = json.loads(body)
    audit_event = AuditEvent(**data)
    crear_log_auditoria(audit_event)
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    
    print(" [*] Waiting for audit logs. To exit press CTRL+C")
    channel.start_consuming()