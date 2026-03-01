# Installation Guide

## Quick Start (Recommended Mode)

1. **Download JartBROWSER**
   - Go to [jartbrowser.io](https://jartbrowser.io)
   - Download for your platform (macOS, Windows, Linux)
   - Run installer

2. **Follow Setup Wizard**
   - Welcome screen with feature overview
   - Choose installation mode (Recommended/Advanced)
   - Select deployment location (Local/VPS/Hybrid)
   - Configure LLM providers
   - Review summary and deploy

3. **Complete Setup**
   - Docker containers start automatically
   - Chrome extension installed
   - Setup wizard guides you through final steps

## Advanced Installation

### System Requirements

**Minimum:**
- 4GB RAM
- 20GB free disk space
- Node.js 18+
- Python 3.11+
- Docker 20.10+

**Recommended:**
- 8GB RAM
- 50GB free disk space
- GPU for local models (NVIDIA/AMD)
- SSD for better performance

### Manual Installation

1. **Clone repository**
   ```bash
   git clone https://github.com/jartbrowser/JartBROWSER.git
   cd JartBROWSER
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   cd backend && poetry install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Build application**
   ```bash
   pnpm build
   ```

5. **Run application**
   ```bash
   pnpm dev:app
   ```

## Docker Deployment

### Local Deployment
```bash
cd JartBROWSER
./generate-docker-compose.sh
docker-compose up -d
```

### VPS Deployment
1. **SSH to your VPS**
2. **Clone repository**
3. **Run setup script**
   ```bash
   ./scripts/setup-vps.sh
   ```

## Chrome Extension Installation

### Chrome Web Store
1. Open Chrome Web Store
2. Search for "JartBROWSER"
3. Click "Add to Chrome"
4. Grant permissions

### Developer Mode
1. Open `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `chrome-extension/dist` folder

## Verification

1. **Check Docker status**
   - Open JartBROWSER app
   - Go to Docker tab
   - Verify all containers are running

2. **Test API**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Test extension**
   - Open Chrome Canary
   - Check sidebar appears
   - Test AI chat

## Troubleshooting

See [troubleshooting.md](./troubleshooting.md) for common issues.
