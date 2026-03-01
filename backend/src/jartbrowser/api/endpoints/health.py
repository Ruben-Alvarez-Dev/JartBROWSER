"""Health API endpoints"""

import time
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from jartbrowser.models.schemas import HealthResponse, InfoResponse
from jartbrowser.services.database import get_database_service

router = APIRouter()

_start_time = time.time()


def get_db() -> Session:
    """Database dependency"""
    db_service = get_database_service()
    with db_service.get_session() as session:
        yield session


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime=time.time() - _start_time,
        database="connected",
        mcp_server=True,
    )


@router.get("/info", response_model=InfoResponse)
async def get_info():
    """Get application info"""
    return InfoResponse(
        name="JartBROWSER API",
        version="1.0.0",
        description="Complete REST API and MCP Server for JartBROWSER",
        api_version="v1",
    )
