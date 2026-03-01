# JartBROWSER

Your browser, powered by Artificial Intelligence.

## Overview

JartBROWSER is an enterprise-grade agentic browser automation platform with complete programmatic control via REST API and MCP.

## Features

- 🤖 **Autonomous Navigation** - 122+ features for browser automation
- 🔗 **All LLM Providers** - OpenAI, Anthropic, Google, Z.ai, MiniMax, Mistral, and custom
- 🎯 **100% Optimized** - Prompts, skills, and tools for maximum efficiency
- 🐳 **Docker Ready** - One-command deployment with Docker Compose
- 🔌 **Complete API** - REST API (OpenAPI 3.1) + MCP Server for programmatic control
- 🖥️ **Cross-Platform** - Desktop app (Electron) for macOS, Windows, Linux
- 🔐 **Enterprise Security** - Encrypted API keys, local-first by default

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        JARTBROWSER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │  Electron Desktop App (GUI + Docker Management)             │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │  REST API (FastAPI + OpenAPI 3.1)                      │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │  MCP Server (SSE + Tools)                                 │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │  Chrome Extension (Sidebar + Agent)                        │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │  Docker Containers (OpenWebUI, Ollama, Redis, Caddy)   │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
JartBROWSER/
├─ electron-app/           # Electron main process
├─ renderer/               # React UI (Vite)
├─ backend/               # FastAPI + MCP Server
├─ chrome-extension/       # Chrome extension source
├─ prompts/              # Optimized prompts library
├─ skills/               # Skill definitions
├─ docs/                 # Documentation
└─ logs/                 # Build/scaffold logs
```

## Getting Started

### Prerequisites

- Docker 20.10+
- Node.js 18+
- Python 3.11+
- Chrome Canary (for extension)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jartbrowser/JartBROWSER.git
   cd JartBROWSER
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   ```

3. **Run the setup wizard**
   ```bash
   pnpm dev:app
   ```

4. **Follow the wizard**
   - Choose installation mode (Recommended/Advanced)
   - Select deployment location (Local/VPS/Hybrid)
   - Configure LLM providers
   - Customize prompts and skills
   - Deploy Docker containers

## Development

### Run Electron App
```bash
pnpm dev:app
```

### Run Backend API
```bash
pnpm dev:api
```

### Run Chrome Extension
```bash
pnpm dev:extension
```

### Build for Production
```bash
pnpm build
```

## API Documentation

- **REST API**: http://localhost:8000/api/v1/docs
- **OpenAPI Spec**: http://localhost:8000/api/v1/openapi.json
- **MCP Server**: SSE endpoint at http://localhost:3001/sse

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: https://github.com/jartbrowser/JartBROWSER/issues
- **Docs**: https://docs.jartbrowser.io
- **Email**: support@jartbrowser.io
