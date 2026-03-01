"""Provider API endpoints - Enhanced with LLM service"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from jartbrowser.models.schemas import ProviderListResponse, APIKeyCreate, APIKeyResponse
from jartbrowser.models.database import APIKey
from jartbrowser.services.database import get_database_service
from jartbrowser.services.encryption import get_encryption_service
from jartbrowser.services.llm_service import LLMService, MODEL_REGISTRY, get_llm_service
from jartbrowser.services.privacy import get_privacy_service

router = APIRouter()


def get_db() -> Session:
    """Database dependency"""
    db_service = get_database_service()
    with db_service.get_session() as session:
        yield session


def get_llm() -> LLMService:
    """LLM service dependency"""
    return get_llm_service()


# ============== Providers ==============


@router.get("/providers", response_model=ProviderListResponse)
async def list_providers():
    """List available LLM providers and their models"""
    from jartbrowser.services.llm_service import PROVIDER_CLASSES

    providers = list(PROVIDER_CLASSES.keys())
    llm = get_llm_service()
    default_provider, default_model = llm.get_default()

    return ProviderListResponse(
        providers=providers, default_provider=default_provider, default_model=default_model
    )


@router.get("/providers/{provider}/models")
async def list_provider_models(provider: str):
    """List models for a specific provider"""
    models = [m for m in MODEL_REGISTRY.values() if m.provider == provider]

    if not models:
        raise HTTPException(status_code=404, detail=f"Provider '{provider}' not found")

    return {
        "provider": provider,
        "models": [
            {
                "id": m.id,
                "name": m.name,
                "context_window": m.context_window,
                "max_output_tokens": m.max_output_tokens,
                "supports_vision": m.supports_vision,
                "input_cost_per_1k": m.input_cost_per_1k,
                "output_cost_per_1k": m.output_cost_per_1k,
            }
            for m in models
        ],
    }


@router.get("/providers/{provider}/models/{model}")
async def get_model_info(provider: str, model: str):
    """Get detailed information about a specific model"""
    from jartbrowser.services.llm_service import MODEL_REGISTRY

    model_info = MODEL_REGISTRY.get(model)

    if not model_info or model_info.provider != provider:
        raise HTTPException(
            status_code=404, detail=f"Model '{model}' not found for provider '{provider}'"
        )

    return {
        "id": model_info.id,
        "name": model_info.name,
        "provider": model_info.provider,
        "context_window": model_info.context_window,
        "max_output_tokens": model_info.max_output_tokens,
        "supports_vision": model_info.supports_vision,
        "supports_streaming": model_info.supports_streaming,
        "input_cost_per_1k": model_info.input_cost_per_1k,
        "output_cost_per_1k": model_info.output_cost_per_1k,
    }


# ============== API Keys ==============


@router.post("/providers/keys", response_model=APIKeyResponse)
async def create_api_key(key_data: APIKeyCreate, db: Session = Depends(get_db)):
    """Store a new API key for a provider"""
    # Check privacy settings
    privacy = get_privacy_service()
    if not privacy.is_api_key_encryption_enabled():
        raise HTTPException(
            status_code=403,
            detail="API key encryption is disabled. Enable it in security settings.",
        )

    # Encrypt the key
    encryption = get_encryption_service()
    encrypted_key = encryption.encrypt(key_data.api_key)

    # Store in database
    api_key = APIKey(
        provider=key_data.provider,
        key_alias=key_data.key_alias,
        encrypted_key=encrypted_key,
        is_active=True,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    # Also set in LLM service for immediate use
    llm = get_llm_service()
    llm.set_api_key(key_data.provider, key_data.api_key)

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


# ============== Model Selection ==============


class SetDefaultModel(BaseModel):
    provider: str
    model: str


@router.post("/providers/default")
async def set_default_model(config: SetDefaultModel, llm: LLMService = Depends(get_llm)):
    """Set the default provider and model"""
    # Validate provider and model
    from jartbrowser.services.llm_service import MODEL_REGISTRY

    if config.provider not in ["openai", "anthropic", "ollama"]:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {config.provider}")

    if config.model not in MODEL_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown model: {config.model}")

    model_info = MODEL_REGISTRY[config.model]
    if model_info.provider != config.provider:
        raise HTTPException(
            status_code=400,
            detail=f"Model {config.model} is not available for provider {config.provider}",
        )

    llm.set_default(config.provider, config.model)

    return {"success": True, "default_provider": config.provider, "default_model": config.model}


@router.get("/providers/default")
async def get_default_model(llm: LLMService = Depends(get_llm)):
    """Get the default provider and model"""
    provider, model = llm.get_default()
    return {"default_provider": provider, "default_model": model}


# ============== Usage Stats ==============


@router.get("/providers/usage")
async def get_usage_stats(llm: LLMService = Depends(get_llm)):
    """Get token usage statistics"""
    usage = llm.get_usage_stats()

    # Calculate costs
    costs = {}
    for provider, tokens in usage.items():
        costs[provider] = llm.estimate_cost(provider)

    return {"tokens_used": usage, "estimated_cost": costs}


# ============== Test ==============


class TestProviderRequest(BaseModel):
    provider: str
    model: Optional[str] = None


@router.post("/providers/test")
async def test_provider(request: TestProviderRequest, llm: LLMService = Depends(get_llm)):
    """Test if a provider/model works"""
    model = request.model
    if not model:
        # Get first available model for provider
        models = [m for m in MODEL_REGISTRY.values() if m.provider == request.provider]
        if not models:
            raise HTTPException(
                status_code=404, detail=f"No models found for provider {request.provider}"
            )
        model = models[0].id

    try:
        response = await llm.complete(
            "Say 'OK' if you can read this.", provider=request.provider, model=model, max_tokens=10
        )

        return {
            "success": True,
            "provider": request.provider,
            "model": model,
            "response": response.content,
            "latency_ms": response.latency_ms,
        }
    except Exception as e:
        return {"success": False, "provider": request.provider, "model": model, "error": str(e)}
