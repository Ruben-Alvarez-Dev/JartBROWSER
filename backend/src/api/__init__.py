from fastapi import APIRouter

from jartbrowser.api.endpoints import (
    docker,
    config,
    providers,
    prompts,
    skills,
    mcp,
    browser,
    agent,
    health
)

api_router = APIRouter()

# Include all sub-routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(docker.router, prefix="/docker", tags=["Docker"])
api_router.include_router(config.router, prefix="/config", tags=["Config"])
api_router.include_router(providers.router, prefix="/providers", tags=["Providers"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["Prompts"])
api_router.include_router(skills.router, prefix="/skills", tags=["Skills"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["MCP"])
api_router.include_router(browser.router, prefix="/browser", tags=["Browser"])
api_router.include_router(agent.router, prefix="/agent", tags=["Agent"])
