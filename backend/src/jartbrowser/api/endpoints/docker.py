"""Docker API endpoints"""

import docker
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from jartbrowser.models.schemas import DockerStatusResponse, DockerComposeResponse

router = APIRouter()


# Docker client initialization
def get_docker_client():
    """Get Docker client"""
    try:
        return docker.from_env()
    except Exception as e:
        return None


@router.get("/docker/status", response_model=DockerStatusResponse)
async def docker_status():
    """Get Docker status"""
    client = get_docker_client()

    if not client:
        return DockerStatusResponse(running=False, containers=[], images=[], volumes=[])

    try:
        containers = client.containers.list()
        images = client.images.list()
        volumes = client.volumes.list()

        return DockerStatusResponse(
            running=True,
            containers=[
                {
                    "id": c.id[:12],
                    "name": c.name,
                    "image": c.image.tags[0] if c.image.tags else c.image.short_id,
                    "status": c.status,
                    "created": c.attrs.get("Created"),
                }
                for c in containers
            ],
            images=[
                {"id": i.id[:12], "tags": i.tags, "size": i.attrs.get("Size")}
                for i in images[:10]  # Limit to 10
            ],
            volumes=[{"name": v.name, "driver": v.driver} for v in volumes],
        )
    except Exception as e:
        return DockerStatusResponse(
            running=False, error=str(e), containers=[], images=[], volumes=[]
        )


@router.post("/docker/compose/up")
async def compose_up(compose_file: str = "docker-compose.local.yml"):
    """Start Docker Compose services"""
    import subprocess
    import os

    # Get absolute path to compose file
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    compose_path = os.path.join(base_dir, compose_file)

    if not os.path.exists(compose_path):
        raise HTTPException(status_code=404, detail=f"Compose file not found: {compose_file}")

    try:
        result = subprocess.run(
            ["docker-compose", "-f", compose_path, "up", "-d"],
            capture_output=True,
            text=True,
            cwd=base_dir,
        )

        return DockerComposeResponse(
            success=result.returncode == 0,
            message=result.stdout if result.returncode == 0 else result.stderr,
        )
    except Exception as e:
        return DockerComposeResponse(success=False, message=str(e))


@router.post("/docker/compose/down")
async def compose_down(compose_file: str = "docker-compose.local.yml"):
    """Stop Docker Compose services"""
    import subprocess
    import os

    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    compose_path = os.path.join(base_dir, compose_file)

    if not os.path.exists(compose_path):
        raise HTTPException(status_code=404, detail=f"Compose file not found: {compose_file}")

    try:
        result = subprocess.run(
            ["docker-compose", "-f", compose_path, "down"],
            capture_output=True,
            text=True,
            cwd=base_dir,
        )

        return DockerComposeResponse(
            success=result.returncode == 0,
            message=result.stdout if result.returncode == 0 else result.stderr,
        )
    except Exception as e:
        return DockerComposeResponse(success=False, message=str(e))


@router.post("/docker/container/{container_id}/action")
async def container_action(container_id: str, action: str):
    """Start, stop, restart, or remove a container"""
    client = get_docker_client()

    if not client:
        raise HTTPException(status_code=503, detail="Docker not available")

    try:
        container = client.containers.get(container_id)

        if action == "start":
            container.start()
        elif action == "stop":
            container.stop()
        elif action == "restart":
            container.restart()
        elif action == "remove":
            container.remove()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

        return {"success": True, "message": f"Container {container_id}: {action}"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail=f"Container not found: {container_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/docker/logs/{container_id}")
async def container_logs(container_id: str, lines: int = 100):
    """Get container logs"""
    client = get_docker_client()

    if not client:
        raise HTTPException(status_code=503, detail="Docker not available")

    try:
        container = client.containers.get(container_id)
        logs = container.logs(tail=lines).decode("utf-8")

        return {"container_id": container_id, "logs": logs}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail=f"Container not found: {container_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
