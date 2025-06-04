# PARCIAL 2 SEGUNDO CORTE
# Arquitectura de Microservicios con FastAPI, RabbitMQ y Traefik

Este proyecto implementa una arquitectura de microservicios local que incluye:
- API REST en FastAPI
- Worker consumidor de RabbitMQ
- Traefik como reverse proxy
- Orquestación con Docker Compose

## 📋 Tabla de Contenidos

- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Requisitos](#-requisitos)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Endpoints](#-endpoints)
- [Monitorización](#-monitorización)

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

### Ver mensajes procesados
```bash
docker-compose exec worker cat /app/data/messages.log
```

### Acceder a interfaces web
- **API Documentation**: http://localhost/api/docs
- **RabbitMQ Management**: http://localhost/monitor (usuario: `admin`, contraseña: `secret`)
- **Traefik Dashboard**: http://localhost:8080/dashboard/

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

2. **Logs**:
   ```bash
   docker-compose logs -f api
   docker-compose logs -f worker
   ```

3. **Métricas**:
   - Traefik expone métricas en el dashboard
   - RabbitMQ proporciona métricas en la interfaz de management
