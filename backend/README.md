# Backend

JartBROWSER FastAPI backend with REST API and MCP Server.

## Structure

```
backend/
├─ src/
│   ├─ api/              # FastAPI routes
│   ├─ mcp/              # MCP Server
│   ├─ docker/           # Docker management
│   ├─ config/           # Config management
│   ├─ browser/          # Browser automation
│   ├─ agents/           # Agent orchestration
│   └─ main.py
├─ requirements.txt
└─ pyproject.toml
```

## Development

```bash
pnpm dev
```

## Build

```bash
pnpm build
```
