import pika
import os
import json
from datetime import datetime
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "content": message.get("content"),
            "priority": message.get("priority", 1)
        }
        
        with open("/app/data/messages.log", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        logger.info(f"Processed message: {message}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def connect_to_rabbitmq():
    credentials = pika.PlainCredentials('admin', 'secret')
    parameters = pika.ConnectionParameters(
        host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    return pika.BlockingConnection(parameters)

def main():
    # Ensure data directory exists
    if not os.path.exists("/app/data"):
        os.makedirs("/app/data")
    
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            connection = connect_to_rabbitmq()
            channel = connection.channel()
            
            queue_name = os.getenv('RABBITMQ_QUEUE', 'messages')
            channel.queue_declare(queue=queue_name, durable=True)
            channel.basic_qos(prefetch_count=1)
            
            logger.info("Worker successfully connected to RabbitMQ")
            logger.info("Waiting for messages. To exit press CTRL+C")
            
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback
            )
            
            channel.start_consuming()
            
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise
        except KeyboardInterrupt:
            logger.info("Worker stopped by user")
            connection.close()
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(retry_delay)
            if attempt == max_retries - 1:
                raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Worker failed: {e}")
        exit(1)