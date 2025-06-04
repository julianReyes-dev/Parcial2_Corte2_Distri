from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import pika
import os
from typing import Optional

app = FastAPI(
    root_path="/api",
    docs_url="/docs",
    redoc_url="/redoc"
)
security = HTTPBasic()

class Message(BaseModel):
    content: str
    priority: Optional[int] = 1

# RabbitMQ connection
def get_rabbitmq_connection():
    credentials = pika.PlainCredentials('admin', 'secret')
    parameters = pika.ConnectionParameters(
        host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
        credentials=credentials
    )
    return pika.BlockingConnection(parameters)

# Authentication
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv('BASIC_AUTH_USERNAME', 'admin')
    correct_password = os.getenv('BASIC_AUTH_PASSWORD', 'secret')
    
    if (credentials.username != correct_username or 
        credentials.password != correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.post("/message")
async def create_message(message: Message, username: str = Depends(authenticate)):
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        queue_name = os.getenv('RABBITMQ_QUEUE', 'messages')
        channel.queue_declare(queue=queue_name, durable=True)
        
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message.json(),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
        
        connection.close()
        return {"status": "Message published to RabbitMQ"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}