"""JartBROWSER Backend Main Application"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jartbrowser.api.router import api_router
from jartbrowser.mcp.server import get_mcp_server


_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    print("Starting JartBROWSER Backend...")

    # Start MCP server
    mcp_server = get_mcp_server()
    await mcp_server.start(port=3001)

    yield

    # Shutdown
    print("Shutting down JartBROWSER Backend...")
    await mcp_server.stop()


app = FastAPI(
    title="JartBROWSER API",
    description="Complete REST API for JartBROWSER - Agentic Browser Automation Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0", "uptime": time.time() - _start_time}


@app.get("/api/v1/info")
async def get_info():
    """Get application information"""
    return {
        "name": "JartBROWSER API",
        "version": "1.0.0",
        "description": "Complete REST API and MCP Server for JartBROWSER",
        "api_version": "v1",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
