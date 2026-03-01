# Docker Compose - VPS Deployment

## Overview

This docker-compose.yml is for **VPS deployment** of JartBROWSER.

## Services

### 1. OpenWebUI (Backend + UI)
- **Port**: 3000 (public)
- **Purpose**: LLM interface, chat management, RAG, tools
- **Data**: Persistent in `openwebui-data` volume
- **Access**: Public internet access

### 2. Redis (Caching)
- **Port**: 6379 (public)
- **Purpose**: Caching, session management, rate limiting
- **Data**: Persistent in `redis-data` volume

## Usage

### Start services
```bash
docker-compose -f docker-compose.vps.yml up -d
```

### Stop services
```bash
docker-compose -f docker-compose.vps.yml down
```

### View logs
```bash
docker-compose -f docker-compose.vps.yml logs -f
```

## Configuration

### Environment Variables

Create a `.env` file:

```bash
# Security
WEBUI_SECRET_KEY=your-secret-key-here

# Ollama (if running locally and accessing remotely)
OLLAMA_BASE_URL=http://YOUR_LOCAL_IP:11434
```

### Accessing from local machines

The VPS services will be accessible from your local machines via:

- **OpenWebUI**: `http://YOUR_VPS_IP:3000`
- **Redis**: `http://YOUR_VPS_IP:6379`

**Note**: Configure your VPS firewall to allow ports 3000 and 6379.

### Security Recommendations

1. **Change default secrets**
   ```bash
   # Generate a strong secret
   openssl rand -hex 32
   ```

2. **Configure firewall**
   ```bash
   # Ubuntu/Debian
   sudo ufw allow 3000/tcp
   sudo ufw allow 6379/tcp
   sudo ufw enable
   ```

3. **Use SSL/TLS**
   - Use reverse proxy (Nginx, Caddy)
   - Configure Let's Encrypt certificates
   - Redirect HTTP to HTTPS

4. **Limit access**
   - Restrict to specific IP ranges if possible
   - Use strong authentication

### Nginx Reverse Proxy Example

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Scaling

For production, consider:

1. **Multiple instances**
   ```bash
   docker-compose -f docker-compose.vps.yml up -d --scale openwebui=3
   ```

2. **Load balancer**
   - Use Nginx as load balancer
   - Configure health checks

3. **Monitoring**
   - Add health monitoring
   - Set up alerting

### Backups

Automate backups with cron:

```bash
# Backup daily at 3 AM
0 3 * * * /usr/bin/docker exec jartbrowser-openwebui sh -c 'tar -czf /backup/jartbrowser-$(date +\%Y\%m\%d).tar.gz /app/backend/data'
```

## Troubleshooting

### Service won't start
```bash
# Check service logs
docker-compose -f docker-compose.vps.yml logs <service>

# Check service status
docker-compose -f docker-compose.vps.yml ps
```

### Port conflicts
```bash
# Check what's using the port
sudo lsof -i :3000
sudo lsof -i :6379
```

### Out of memory
```bash
# Check system resources
free -h

# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Connection refused
```bash
# Check if services are running
docker-compose -f docker-compose.vps.yml ps

# Check firewall
sudo ufw status

# Check ports
sudo netstat -tlnp | grep -E ':(3000|6379)'
```
