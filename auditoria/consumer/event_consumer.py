import os, json, pika, time, asyncio
from database.database import db
from models.audit_event import AuditEvent
from logic.logic_audit_logs import crear_log_auditoria

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
QUEUE_NAME = "audit_queue"
user = os.getenv("RABBITMQ_USER", "admin")
password = os.getenv("RABBITMQ_PASS", "admin")

credentials = pika.PlainCredentials(user, password)

def callback(ch, method, properties, body):
    data = json.loads(body)
    audit_event = AuditEvent(**data)
    asyncio.run(crear_log_auditoria(audit_event, db))
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
def start_consumer():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
            
            print(" [*] Waiting for audit logs. To exit press CTRL+C")
            channel.start_consuming()
        except (pika.exceptions.AMQPConnectionError, Exception) as e:
            print(f"Connection to RabbitMQ failed: {e}, retrying in 5 seconds...")
            time.sleep(5)