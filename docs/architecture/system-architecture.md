# Architecture Overview

## System Architecture

JartBROWSER is a multi-component system designed for enterprise-grade agentic browser automation with complete programmatic control.

## Components

### 1. Electron Desktop App
- **Purpose**: GUI application for configuration and Docker management
- **Tech Stack**: Electron 28, Node.js 20, React 18, TypeScript
- **Responsibilities**:
  - Setup wizard for initial configuration
  - Docker container management (start/stop/status)
  - Configuration UI (providers, prompts, skills)
  - Dashboard for monitoring
  - Auto-update management

### 2. REST API (FastAPI)
- **Purpose**: Complete programmatic control via REST API
- **Tech Stack**: Python 3.11, FastAPI, SQLAlchemy, Redis
- **Responsibilities**:
  - Docker management endpoints
  - Configuration management
  - Provider management
  - Browser automation control
  - Agent task orchestration
  - API authentication and rate limiting

### 3. MCP Server
- **Purpose**: Expose JartBROWSER as MCP provider for other AI systems
- **Tech Stack**: SSE (Server-Sent Events), JSON-RPC
- **Responsibilities**:
  - Register tools for browser automation
  - Handle MCP protocol messages
  - Stream responses via SSE
  - Resource and prompt management

### 4. Chrome Extension
- **Purpose**: In-browser automation and sidebar UI
- **Tech Stack**: Manifest V3, React 18, TypeScript
- **Responsibilities**:
  - Background service worker for orchestration
  - Sidebar panel for AI chat interface
  - Content scripts for page interaction
  - CDP (Chrome DevTools Protocol) bridge

### 5. Docker Containers
- **Purpose**: Isolated deployment of backend services
- **Tech Stack**: Docker Compose
- **Components**:
  - OpenWebUI (LLM interface)
  - Ollama (local models)
  - Redis (caching)
  - Caddy (TLS/HTTPS)

## Data Flow

```
┌─────────────┐     REST API     ┌─────────────┐
│  Electron   │ ←────────────→  │   Backend    │
│    GUI      │                 │   FastAPI   │
└──────┬──────┘                 └──────┬──────┘
       │                               │
       │                               │
       ↓                               ↓
┌─────────────┐              ┌─────────────┐
│    Docker   │ ←────────────→  │   MCP Server │
│   Manager   │                 │    (SSE)     │
└─────────────┘                 └─────────────┘
         │                               │
         │                               │
         ↓                               ↓
┌─────────────┐              ┌─────────────┐
│ Containers  │              │   Chrome     │
│  (OpenWebUI,│ ←──────────→  │ Extension   │
│  Ollama...) │              │  Sidebar     │
└─────────────┘              └─────────────┘
```

## Security

- API keys encrypted with system keychain
- API authentication with JWT
- Rate limiting per API key
- CORS configuration
- CSP policies in Chrome extension

## Scalability

- Horizontal scaling of FastAPI with Gunicorn
- Redis for distributed caching
- Docker swarm/Kubernetes ready
- Stateless REST API design

## Monitoring

- Structured logging (JSON format)
- Error tracking with Sentry
- Health check endpoints
- Metrics collection (Prometheus compatible)
