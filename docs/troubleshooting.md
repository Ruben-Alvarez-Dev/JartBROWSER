# Troubleshooting

## Common Issues

### Docker Issues

**Container won't start**
```bash
# Check logs
docker-compose logs

# Check status
docker-compose ps

# Restart
docker-compose restart
```

**Port conflicts**
- Check if ports 8000, 3000, 11434, 6379 are in use
- Edit `docker-compose.yml` to change ports
- Restart Docker daemon

**Out of disk space**
```bash
# Clean up unused images
docker system prune -a

# Check disk usage
docker system df
```

### Electron App Issues

**App won't open**
- Check Node.js version: `node --version` (should be 18+)
- Clear Electron cache: `rm -rf ~/Library/Application\ Support/JartBROWSER`
- Check logs: `~/Library/Logs/JartBROWSER/`

**Backend connection failed**
- Verify API is running: `curl http://localhost:8000/health`
- Check CORS configuration
- Verify firewall settings

**Update failed**
- Check internet connection
- Disable VPN/proxy temporarily
- Clear update cache

### Chrome Extension Issues

**Extension not loading**
- Verify Chrome Canary version (114+)
- Check Manifest V3 syntax
- Disable conflicting extensions
- Check browser console for errors

**API calls failing**
- Verify API key is configured
- Check rate limits
- Check CORS headers
- Verify provider status

### Backend API Issues

**Server won't start**
- Check Python version: `python --version` (should be 3.11+)
- Install dependencies: `poetry install`
- Check port conflicts
- Check logs: `backend/logs/`

**Database errors**
- Run migrations: `alembic upgrade head`
- Check database connection string
- Verify PostgreSQL/SQLite is running

**MCP server issues**
- Check SSE endpoint is accessible
- Verify CORS configuration
- Check server logs for errors

## Debugging

### Enable Debug Mode

**Electron App**
```bash
DEBUG=jartbrowser:* pnpm dev:app
```

**Backend API**
```bash
export LOG_LEVEL=DEBUG
pnpm dev:api
```

**Chrome Extension**
- Open DevTools in extension popup
- Check background service worker logs
- Use `chrome.runtime.getBackgroundPage()` to access background

### Log Locations

- **Electron**: `~/Library/Logs/JartBROWSER/` (macOS), `%APPDATA%/JartBROWSER/logs/` (Windows)
- **Backend**: `backend/logs/`
- **Docker**: `docker-compose logs`
- **Extension**: Chrome DevTools Console

## Getting Help

1. Check [Documentation](https://docs.jartbrowser.io)
2. Search [GitHub Issues](https://github.com/jartbrowser/JartBROWSER/issues)
3. Join [Discord](https://discord.gg/jartbrowser)
4. Email: support@jartbrowser.io

## Known Issues

See [GitHub Milestones](https://github.com/jartbrowser/JartBROWSER/milestones) for upcoming fixes.
