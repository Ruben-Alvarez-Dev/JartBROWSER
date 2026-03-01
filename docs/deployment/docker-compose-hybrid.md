# Docker Compose - Hybrid Deployment

## Overview

This docker-compose.yml is for **hybrid deployment** of JartBROWSER:

- **OpenWebUI** runs on VPS (cloud)
- **Ollama** runs on your local machine
- VPS connects to local Ollama via SSH tunnel or VPN

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  VPS (Cloud)                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  OpenWebUI (http://0.0.0.0:3000)          │  │
│  │  - Runs on VPS                                     │  │
│  │  - Publicly accessible via HTTPS                   │  │
│  │  - Connects to local Ollama                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
         │
         │ SSH Tunnel / VPN
         ↓
┌─────────────────────────────────────────────────────────────────────┐
│  Local Machine                                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Ollama (http://127.0.0.1:11434)            │  │
│  │  - Runs on local machine with GPU                  │  │
│  │  - Exposes via SSH reverse tunnel              │  │
│  │  - Models stored locally                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Services

### 1. OpenWebUI (VPS)
- **Port**: 3000 (public)
- **Purpose**: LLM interface, chat management, RAG, tools
- **Data**: Persistent in VPS volume
- **Access**: Public internet via HTTPS

### 2. Ollama (Local)
- **Port**: 11434 (localhost only)
- **Purpose**: Run local LLM models
- **Data**: Persistent in local volume
- **Access**: Via SSH tunnel from VPS

### 3. Redis (VPS)
- **Port**: 6379 (public)
- **Purpose**: Caching, session management
- **Data**: Persistent in VPS volume

## Usage

### Local Machine Setup

#### 1. Start local Ollama
```bash
# Start local Ollama with GPU support
docker-compose -f docker-compose.hybrid.yml up -d ollama
```

#### 2. Test local Ollama
```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags
```

#### 3. Set up SSH tunnel (if needed)
```bash
# Create reverse tunnel from VPS
ssh -R 11434:localhost:11434 user@your-vps-ip

# Or use autossh to keep tunnel alive
autossh -M 11434 -f user@your-vps-ip
```

### VPS Setup

#### 1. Deploy OpenWebUI and Redis
```bash
# On VPS
git clone https://github.com/Ruben-Alvarez-Dev/JartBROWSER.git
cd JartBROWSER
docker-compose -f docker-compose.hybrid.yml up -d
```

#### 2. Configure OpenWebUI to use local Ollama
```bash
# Set environment variable
export OLLAMA_BASE_URL=http://host.docker.internal:11434

# Or update .env file
echo "OLLAMA_BASE_URL=http://host.docker.internal:11434" >> .env
```

#### 3. Restart services
```bash
docker-compose -f docker-compose.hybrid.yml restart
```

## Configuration

### Environment Variables

#### Local Machine (.env.local)
```bash
# Local Ollama configuration
OLLAMA_NUM_PARALLEL=4
OLLAMA_LOAD_TIMEOUT=5m
```

#### VPS (.env.vps)
```bash
# Security
WEBUI_SECRET_KEY=your-vps-secret-key-here

# Local Ollama connection
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### SSH Tunnel Configuration

Create `~/.ssh/config` entry:

```ssh-config
Host jartbrowser-vps
    HostName your-vps-ip
    User your-username
    RemoteForward 11434 localhost:11434
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

Then start tunnel:

```bash
ssh -f jartbrowser-vps -N
```

## Security

### Local Machine
1. Firewall rules
   ```bash
   # Allow local access only
   ufw allow from 127.0.0.1 to any port 11434
   ```

2. Use SSH keys
   - Disable password authentication
   - Use key-based authentication

### VPS
1. Firewall rules
   ```bash
   # Allow from local machine only
   ufw allow from YOUR_HOME_IP to any port 3000
   ufw allow from YOUR_HOME_IP to any port 6379
   ```

2. Reverse proxy with SSL
   ```bash
   # Use Caddy for automatic HTTPS
   caddy reverse-proxy --from https://your-domain.com --to http://localhost:3000
   ```

3. Rate limiting
   - Configure Nginx/Caddy rate limits
   - Use Redis for distributed rate limiting

## Performance Optimization

### Local Ollama
1. GPU acceleration
   ```bash
   # Verify GPU is being used
   docker exec jartbrowser-ollama nvidia-smi
   ```

2. Model caching
   ```bash
   # Models are cached locally
   # No need to re-download
   ```

### VPS OpenWebUI
1. Horizontal scaling
   ```bash
   # Scale if needed
   docker-compose -f docker-compose.hybrid.yml up -d --scale openwebui=3
   ```

2. Load balancing
   - Use Nginx as load balancer
   - Configure health checks

3. Caching
   - Redis for session management
   - CDN for static assets (if applicable)

## Troubleshooting

### Connection to local Ollama fails
```bash
# Check if SSH tunnel is active
ps aux | grep "11434"

# Test local Ollama directly
curl http://localhost:11434/api/tags

# Test VPS connection
curl http://your-vps-ip:3000/health
```

### Model loading slow
```bash
# Check GPU usage
nvidia-smi

# Check model download progress
docker logs jartbrowser-ollama
```

### High latency
```bash
# Check network latency
ping your-vps-ip

# Check bandwidth
speedtest-cli

# Use nearest VPS region
```

## Monitoring

### Local Machine
- GPU usage: `nvidia-smi`
- Model memory: `docker stats`
- SSH tunnel status: `ps aux | grep ssh`

### VPS
- Resource usage: `htop`, `docker stats`
- Service health: `curl http://localhost:3000/health`
- Error logs: `docker-compose logs -f`
