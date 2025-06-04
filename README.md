# PARCIAL 2 SEGUNDO CORTE
# Arquitectura de Microservicios con FastAPI, RabbitMQ y Traefik

Este proyecto implementa una arquitectura de microservicios local que incluye:
- API REST en FastAPI
- Worker consumidor de RabbitMQ
- Traefik como reverse proxy
- Orquestación con Docker Compose

## 📋 Tabla de Contenidos

- [Respuestas a Conceptos Teoricos](#-conceptos-teoricos)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Requisitos](#-requisitos)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Endpoints](#-endpoints)
- [Monitorización](#-monitorización)


## Conceptos Teóricos

## 1.1 RabbitMQ

### ¿Qué es RabbitMQ y cuándo se debe utilizar una cola frente a un exchange tipo fanout?

RabbitMQ es un broker de mensajería de código abierto que implementa el protocolo AMQP (Advanced Message Queuing Protocol). Actúa como intermediario para el envío asíncrono de mensajes entre aplicaciones o microservicios.

**Cola vs Exchange Fanout:**
- **Cola tradicional**: Se usa cuando necesitas:
  - Garantizar el procesamiento de mensajes por un solo consumidor
  - Mantener el orden de los mensajes
  - Balanceo de carga entre múltiples workers
  - Ejemplo: Procesamiento de pedidos donde cada mensaje debe ser procesado una sola vez

- **Exchange Fanout**: Se usa cuando necesitas:
  - Difundir mensajes a múltiples colas simultáneamente
  - Patrón publish/subscribe
  - Escenarios de broadcasting
  - Ejemplo: Notificaciones en tiempo real a múltiples servicios

### ¿Qué es una Dead Letter Queue (DLQ) y cómo se configura en RabbitMQ?

Una Dead Letter Queue (DLQ) es una cola especial donde se redirigen mensajes que:
- No pueden ser procesados correctamente
- Exceden el límite de reintentos
- Son rechazados explícitamente
- Exceden su TTL (Time-To-Live)

**Configuración en RabbitMQ:**
```python
# Al declarar la cola principal
args = {
    "x-dead-letter-exchange": "dlx_exchange",
    "x-dead-letter-routing-key": "dl_queue"
}
channel.queue_declare(queue='main_queue', arguments=args)

# Declarar el exchange y cola DLQ
channel.exchange_declare(exchange='dlx_exchange', exchange_type='direct')
channel.queue_declare(queue='dl_queue')
channel.queue_bind(queue='dl_queue', exchange='dlx_exchange', routing_key='dl_queue')
```

## 1.2 Docker y Docker Compose

### Diferencia entre un volumen y un bind mount con ejemplos

**Volumen Docker:**
- Administrado por Docker
- Almacenado en el sistema de archivos de Docker (/var/lib/docker/volumes)
- Mejor rendimiento (especialmente en Linux)
- Ejemplo en docker-compose.yml:
```yaml
services:
  db:
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

**Bind Mount:**
- Mapea directamente un directorio del host al contenedor
- Útil para desarrollo (cambios inmediatos)
- Ejemplo:
```yaml
services:
  app:
    volumes:
      - ./src:/app/src
```

### ¿Qué implica usar network_mode: host en un contenedor?

`network_mode: host` hace que el contenedor comparta la red del host (misma interfaz de red, mismos puertos). Implicaciones:

**Ventajas:**
- Mayor rendimiento de red (sin NAT)
- Acceso directo a servicios locales del host
- No necesita mapeo de puertos explícito

**Desventajas:**
- Pérdida de aislamiento de red
- Conflictos de puertos
- No compatible con Docker Swarm

Ejemplo:
```yaml
services:
  monitoring:
    network_mode: host
    image: prom/prometheus
```

## 1.3 Traefik

### Función de Traefik en una arquitectura de microservicios

Traefik actúa como:
1. **Reverse Proxy/API Gateway**:
   - Enrutamiento inteligente de peticiones
   - Balanceo de carga entre instancias
   - Terminación SSL/TLS

2. **Service Discovery**:
   - Integración automática con Docker, Kubernetes, etc.
   - Detección dinámica de servicios

3. **Middleware**:
   - Autenticación
   - Rate limiting
   - Compresión
   - Circuit breakers

4. **Monitorización**:
   - Dashboard en tiempo real
   - Métricas de tráfico
   - Logs de acceso

### ¿Cómo se puede asegurar un endpoint usando certificados TLS automáticos en Traefik?

Configuración para TLS automático con Let's Encrypt:

1. **docker-compose.yml**:
```yaml
services:
  traefik:
    image: traefik:v2.5
    command:
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --certificatesresolvers.le.acme.email=tucorreo@example.com
      - --certificatesresolvers.le.acme.storage=/letsencrypt/acme.json
      - --certificatesresolvers.le.acme.tlschallenge=true
    volumes:
      - ./letsencrypt:/letsencrypt
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - "80:80"
      - "443:443"
```

2. **Configuración del servicio** (labels):
```yaml
labels:
  - "traefik.http.routers.myservice.rule=Host(`tudominio.com`)"
  - "traefik.http.routers.myservice.entrypoints=websecure"
  - "traefik.http.routers.myservice.tls.certresolver=le"
  - "traefik.http.routers.myservice.tls.domains[0].main=tudominio.com"
```

Esto habilita:
- Redirección automática HTTP→HTTPS
- Renovación automática de certificados
- HTTP/2 habilitado
- A+ en SSL Labs (con configuración adicional)


## 🗂 Estructura del Proyecto

```
microservicios/
├── api/
│   ├── app.py              # Implementación de la API FastAPI
│   ├── requirements.txt    # Dependencias de Python
│   └── Dockerfile          # Configuración del contenedor
├── worker/
│   ├── worker.py           # Consumidor de RabbitMQ
│   ├── requirements.txt
│   └── Dockerfile
├── traefik/
│   └── traefik.yml         # Configuración de Traefik
├── docker-compose.yml      # Orquestación de servicios
```

## ⚙️ Requisitos

- Docker 20.10+
- Docker Compose 1.29+
- Python 3.9+ (solo para desarrollo)

## 🔧 Configuración

1. Clona el repositorio:
   ```bash
   git clone https://github.com/julianReyes-dev/Parcial2_Corte2_Distri.git
   cd Parcial2_Corte2_Distri
   ```

2. Inicia los servicios:
   ```bash
   docker-compose up -d --build
   ```

## 🚀 Uso

### Publicar un mensaje
```bash
curl -X POST "http://localhost/api/message" \
-H "Authorization: Basic YWRtaW46c2VjcmV0" \
-H "Content-Type: application/json" \
-d '{"content":"Mi mensaje","priority":1}'
```
![image](https://github.com/user-attachments/assets/2dd7d073-d079-4685-8804-bff3c4b4144d)


### Ver mensajes procesados
```bash
docker-compose exec worker cat /app/data/messages.log
```
![image](https://github.com/user-attachments/assets/b4b79272-f3ee-4c18-9928-497630e1ea0e)


### Acceder a interfaces web
- **API Documentation**: http://localhost/api/docs
![image](https://github.com/user-attachments/assets/59d59c3a-bcc9-4709-b4ee-a44de6182a74)

- **RabbitMQ Management**: http://localhost/monitor (usuario: `admin`, contraseña: `secret`)
![image](https://github.com/user-attachments/assets/eb9f68e9-7a9d-43b8-af32-ac5bc85763ef)

- **Traefik Dashboard**: http://localhost:8080/dashboard/
![image](https://github.com/user-attachments/assets/39ba45f3-5bfb-41fb-8667-c191f3ffdf7a)


## 📡 Endpoints

### API
- `POST /api/message` - Publica un mensaje en RabbitMQ
- `GET /api/health` - Health check del servicio

### RabbitMQ
- Cola: `messages` (duradera)
- Interfaz web en `/monitor`

## 📊 Monitorización

1. **Health Checks**:
   ```bash
   curl http://localhost/api/health
   ```
![image](https://github.com/user-attachments/assets/448de76b-e069-4f8d-bc61-074c7321d35c)


2. **Logs**:
   ```bash
   docker-compose logs -f api
   docker-compose logs -f worker
   ```

3. **Métricas**:
   - Traefik expone métricas en el dashboard
   - RabbitMQ proporciona métricas en la interfaz de management
