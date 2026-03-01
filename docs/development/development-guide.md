# Development Guide

## Prerequisites

- Node.js 18+ and pnpm 8+
- Python 3.11+ and Poetry
- Docker 20.10+ and Docker Compose
- Git 2.30+

## Setup

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
   # Edit .env with your configuration
   ```

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

### Run All Services
```bash
pnpm dev
```

## Code Style

- **TypeScript**: Strict mode, no `any` types
- **Python**: Black formatter, Ruff linter, mypy type checking
- **Commits**: Conventional Commits, max 2-3 lines
- **Branching**: Git Flow (main, develop, feature/*)

## Testing

```bash
pnpm test        # Run all tests
pnpm test:unit  # Unit tests only
pnpm test:e2e   # E2E tests only
```

## Building

```bash
pnpm build              # Build all
pnpm build:app          # Build Electron app
pnpm build:api          # Build backend
pnpm build:extension    # Build Chrome extension
```

## Deployment

1. **Build Docker images**
   ```bash
   docker-compose build
   ```

2. **Start services**
   ```bash
   docker-compose up -d
   ```

3. **Verify health**
   ```bash
   curl http://localhost:8000/health
   ```

## Troubleshooting

See [troubleshooting.md](./troubleshooting.md) for common issues.
