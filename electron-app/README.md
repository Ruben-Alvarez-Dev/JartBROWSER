# Electron App

JartBROWSER Electron main process with Docker management, config, and system APIs.

## Structure

```
electron-app/
├─ src/
│   ├─ main.ts           # Entry point
│   ├─ ipc/              # IPC handlers
│   │   ├─ docker.ts
│   │   ├─ config.ts
│   │   ├─ updater.ts
│   │   └─ bridge.ts
│   ├─ utils/
│   │   ├─ encryption.ts
│   │   ├─ logger.ts
│   │   └─ validation.ts
│   └─ config/
│       └─ docker-templates/
├─ package.json
└─ electron-builder.yml
```

## Development

```bash
pnpm dev
```

## Build

```bash
pnpm build
```
