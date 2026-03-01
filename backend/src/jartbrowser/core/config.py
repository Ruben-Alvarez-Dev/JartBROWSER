"""JartBROWSER Configuration Module"""

import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # App
    app_name: str = "JartBROWSER"
    app_version: str = "1.0.0"
    debug: bool = False

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # MCP Server
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 3001

    # Database
    database_url: str = "sqlite:///./jartbrowser.db"

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    api_keys_encryption_key: Optional[str] = None

    # Docker
    docker_socket_path: str = "/var/run/docker.sock"

    # LLM Providers - Default settings
    default_provider: str = "openai"
    default_model: str = "gpt-4"

    # Storage
    data_dir: str = "./data"
    prompts_dir: str = "./prompts"
    skills_dir: str = "./skills"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings"""
    return Settings()
