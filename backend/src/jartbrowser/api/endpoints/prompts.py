"""Prompts API endpoints"""

import os
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from jartbrowser.models.schemas import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
    PromptTemplateResponse,
)
from jartbrowser.models.database import PromptTemplate
from jartbrowser.services.database import get_database_service
from jartbrowser.core.config import get_settings

router = APIRouter()


def get_db() -> Session:
    """Database dependency"""
    db_service = get_database_service()
    with db_service.get_session() as session:
        yield session


@router.get("/prompts", response_model=List[PromptTemplateResponse])
async def list_prompts(
    category: Optional[str] = None, active_only: bool = True, db: Session = Depends(get_db)
):
    """List all prompt templates"""
    query = db.query(PromptTemplate)
    if category:
        query = query.filter(PromptTemplate.category == category)
    if active_only:
        query = query.filter(PromptTemplate.is_active == True)

    prompts = query.all()
    return prompts


@router.get("/prompts/{prompt_id}", response_model=PromptTemplateResponse)
async def get_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """Get a specific prompt template"""
    prompt = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.post("/prompts", response_model=PromptTemplateResponse)
async def create_prompt(prompt_data: PromptTemplateCreate, db: Session = Depends(get_db)):
    """Create a new prompt template"""
    prompt = PromptTemplate(
        name=prompt_data.name,
        category=prompt_data.category,
        content=prompt_data.content,
        variables=prompt_data.variables,
        description=prompt_data.description,
        is_active=True,
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


@router.patch("/prompts/{prompt_id}", response_model=PromptTemplateResponse)
async def update_prompt(
    prompt_id: int, prompt_data: PromptTemplateUpdate, db: Session = Depends(get_db)
):
    """Update a prompt template"""
    prompt = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    update_data = prompt_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prompt, field, value)

    db.commit()
    db.refresh(prompt)
    return prompt


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """Delete a prompt template"""
    prompt = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    db.delete(prompt)
    db.commit()

    return {"success": True, "message": "Prompt deleted"}


@router.post("/prompts/{prompt_id}/use")
async def use_prompt(prompt_id: int, variables: dict, db: Session = Depends(get_db)):
    """Use a prompt template with variables"""
    prompt = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Increment usage count
    prompt.usage_count += 1
    db.commit()

    # Render template with variables
    content = prompt.content
    if prompt.variables:
        for var_name, var_value in variables.items():
            content = content.replace(f"{{{var_name}}}", str(var_value))

    return {"rendered_prompt": content, "usage_count": prompt.usage_count}


# Load prompts from filesystem
@router.post("/prompts/load-from-filesystem")
async def load_prompts_from_filesystem(db: Session = Depends(get_db)):
    """Load prompts from the prompts directory"""
    settings = get_settings()
    prompts_dir = settings.prompts_dir

    loaded_count = 0
    if os.path.exists(prompts_dir):
        for filename in os.listdir(prompts_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(prompts_dir, filename)
                with open(filepath, "r") as f:
                    content = f.read()

                # Check if prompt already exists
                name = os.path.splitext(filename)[0]
                existing = db.query(PromptTemplate).filter(PromptTemplate.name == name).first()

                if not existing:
                    prompt = PromptTemplate(
                        name=name, category="filesystem", content=content, is_active=True
                    )
                    db.add(prompt)
                    loaded_count += 1

    db.commit()
    return {"success": True, "loaded_count": loaded_count}
