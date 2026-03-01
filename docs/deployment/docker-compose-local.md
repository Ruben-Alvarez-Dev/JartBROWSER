# Docker Compose - Local Deployment

## Overview

This docker-compose.yml is for **local deployment** of JartBROWSER.

## Services

### 1. OpenWebUI (Backend + UI)
- **Port**: 3000 (localhost only)
- **Purpose**: LLM interface, chat management, RAG, tools
- **Data**: Persistent in `openwebui-data` volume

### 2. Ollama (Local Models)
- **Port**: 11434 (localhost only)
- **Purpose**: Run local LLM models (Llama, Qwen, etc.)
- **Data**: Persistent in `ollama-data` volume
- **GPU**: NVIDIA GPU required for best performance

### 3. Redis (Caching)
- **Port**: 6379 (localhost only)
- **Purpose**: Caching, session management, rate limiting
- **Data**: Persistent in `redis-data` volume

## Usage

### Start services
```bash
docker-compose -f docker-compose.local.yml up -d
```

### Stop services
```bash
docker-compose -f docker-compose.local.yml down
```

### View logs
```bash
docker-compose -f docker-compose.local.yml logs -f openwebui
docker-compose -f docker-compose.local.yml logs -f ollama
docker-compose -f docker-compose.local.yml logs -f redis
```

### Restart services
```bash
docker-compose -f docker-compose.local.yml restart
```

## Configuration

### Environment Variables

Create a `.env` file in the same directory:

```bash
WEBUI_SECRET_KEY=your-secret-key-here
```

### GPU Support

If you have an NVIDIA GPU, Ollama will automatically detect and use it.

### Ports

| Service | Internal Port | External Port | Access |
|---------|---------------|---------------|---------|
| OpenWebUI | 8080 | 3000 | Localhost only |
| Ollama | 11434 | 11434 | Localhost only |
| Redis | 6379 | 6379 | Localhost only |

## Data Persistence

All data is persisted in Docker volumes:

- `openwebui-data`: OpenWebUI backend data
- `ollama-data`: Downloaded models and configuration
- `redis-data`: Redis cache and sessions

## Troubleshooting

### Port already in use
```bash
# Check what's using the port
lsof -i :3000
lsof -i :11434
lsof -i :6379

# Kill the process if needed
kill -9 <PID>
```

### GPU not detected
```bash
# Check if NVIDIA GPU is available
nvidia-smi

# Verify Docker GPU support
docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
```

### Service won't start
```bash
# Check service logs
docker-compose -f docker-compose.local.yml logs <service>

# Check service status
docker-compose -f docker-compose.local.yml ps
```

## Security Notes

- All services are bound to `127.0.0.1` (localhost only)
- No external access by default
- Change `WEBUI_SECRET_KEY` in production
- Use strong passwords for all services
