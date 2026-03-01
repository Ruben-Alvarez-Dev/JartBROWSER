"""Provider API endpoints"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from jartbrowser.models.schemas import ProviderListResponse, APIKeyCreate, APIKeyResponse
from jartbrowser.models.database import APIKey
from jartbrowser.services.database import get_database_service
from jartbrowser.services.encryption import get_encryption_service
from jartbrowser.services.llm_provider import PROVIDER_MODELS

router = APIRouter()


def get_db() -> Session:
    """Database dependency"""
    db_service = get_database_service()
    with db_service.get_session() as session:
        yield session


@router.get("/providers", response_model=ProviderListResponse)
async def list_providers():
    """List available LLM providers and their models"""
    return ProviderListResponse(
        providers=list(PROVIDER_MODELS.keys()), default_provider="openai", default_model="gpt-4o"
    )


@router.get("/providers/{provider}/models")
async def list_provider_models(provider: str):
    """List models for a specific provider"""
    if provider not in PROVIDER_MODELS:
        raise HTTPException(status_code=404, detail=f"Provider '{provider}' not found")
    return {"provider": provider, "models": PROVIDER_MODELS[provider]}


@router.post("/providers/keys", response_model=APIKeyResponse)
async def create_api_key(key_data: APIKeyCreate, db: Session = Depends(get_db)):
    """Store a new API key for a provider"""
    encryption = get_encryption_service()
    encrypted_key = encryption.encrypt(key_data.api_key)

    api_key = APIKey(
        provider=key_data.provider,
        key_alias=key_data.key_alias,
        encrypted_key=encrypted_key,
        is_active=True,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return APIKeyResponse(
        id=api_key.id,
        provider=api_key.provider,
        key_alias=api_key.key_alias,
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
    )


@router.get("/providers/keys", response_model=List[APIKeyResponse])
async def list_api_keys(db: Session = Depends(get_db)):
    """List all stored API keys (without the actual key values)"""
    keys = db.query(APIKey).filter(APIKey.is_active == True).all()
    return [
        APIKeyResponse(
            id=key.id,
            provider=key.provider,
            key_alias=key.key_alias,
            is_active=key.is_active,
            created_at=key.created_at,
            last_used_at=key.last_used_at,
        )
        for key in keys
    ]


@router.delete("/providers/keys/{key_id}")
async def delete_api_key(key_id: int, db: Session = Depends(get_db)):
    """Delete an API key"""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")

    key.is_active = False
    db.commit()

    return {"success": True, "message": "API key deleted"}
