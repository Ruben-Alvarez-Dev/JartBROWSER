"""Config API endpoints"""

import os
import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from jartbrowser.core.config import get_settings

router = APIRouter()


class ConfigUpdate(BaseModel):
    key: str
    value: Any


@router.get("/config")
async def get_config():
    """Get current configuration (non-sensitive)"""
    settings = get_settings()

    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "debug": settings.debug,
        "api_host": settings.api_host,
        "api_port": settings.api_port,
        "mcp_host": settings.mcp_host,
        "mcp_port": settings.mcp_port,
        "default_provider": settings.default_provider,
        "default_model": settings.default_model,
        "data_dir": settings.data_dir,
    }


@router.get("/config/{key}")
async def get_config_value(key: str):
    """Get a specific configuration value"""
    settings = get_settings()

    if not hasattr(settings, key):
        raise HTTPException(status_code=404, detail=f"Config key not found: {key}")

    return {"key": key, "value": getattr(settings, key)}


@router.post("/config")
async def update_config(config: ConfigUpdate):
    """Update configuration (runtime only - not persisted)"""
    # Note: This only updates runtime values, not persisted to file/env
    settings = get_settings()

    if not hasattr(settings, config.key):
        raise HTTPException(status_code=404, detail=f"Config key not found: {config.key}")

    # Validate value type
    current_value = getattr(settings, config.key)
    if type(config.value) != type(current_value):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type for {config.key}: expected {type(current_value).__name__}, got {type(config.value).__name__}",
        )

    setattr(settings, config.key, config.value)

    return {"success": True, "key": config.key, "value": config.value}


@router.get("/config/export")
async def export_config():
    """Export configuration as JSON"""
    settings = get_settings()

    config_dict = {}
    for key in settings.model_fields.keys():
        value = getattr(settings, key)
        # Skip sensitive values
        if key not in ["secret_key", "api_keys_encryption_key"]:
            config_dict[key] = value

    return config_dict


@router.post("/config/import")
async def import_config(config_dict: Dict[str, Any]):
    """Import configuration from JSON"""
    # This would typically save to .env file or config store
    # For now, validate the config

    required_keys = ["app_name", "app_version"]
    missing_keys = [k for k in required_keys if k not in config_dict]

    if missing_keys:
        raise HTTPException(status_code=400, detail=f"Missing required keys: {missing_keys}")

    return {"success": True, "message": "Configuration validated", "keys": list(config_dict.keys())}


@router.get("/config/environment")
async def get_environment():
    """Get environment variables (non-sensitive)"""
    env_vars = {
        "PYTHON_VERSION": os.environ.get("PYTHON_VERSION", "unknown"),
        "NODE_VERSION": os.environ.get("NODE_VERSION", "unknown"),
        "DOCKER_AVAILABLE": os.environ.get("DOCKER_AVAILABLE", "unknown"),
        "DATABASE_URL": os.environ.get("DATABASE_URL", "not set"),
    }

    return env_vars
