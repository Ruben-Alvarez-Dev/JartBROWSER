from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from jartbrowser.api.router import api_router
from jartbrowser.mcp.server import MCPServer


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    mcp_server = MCPServer()
    await mcp_server.start(port=3001)
    yield
    # Shutdown
    await mcp_server.stop()


app = FastAPI(
    title="JartBROWSER API",
    description="Complete REST API for JartBROWSER control",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "uptime": 0
    }


@app.get("/info")
async def get_info():
    return {
        "name": "JartBROWSER API",
        "version": "1.0.0",
        "description": "Complete REST API and MCP Server for JartBROWSER"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
