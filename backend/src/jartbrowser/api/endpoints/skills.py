"""Skills API endpoints"""

import os
import yaml
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from jartbrowser.models.schemas import SkillCreate, SkillUpdate, SkillResponse
from jartbrowser.models.database import Skill
from jartbrowser.services.database import get_database_service
from jartbrowser.core.config import get_settings

router = APIRouter()


def get_db() -> Session:
    """Database dependency"""
    db_service = get_database_service()
    with db_service.get_session() as session:
        yield session


@router.get("/skills", response_model=List[SkillResponse])
async def list_skills(
    category: Optional[str] = None, active_only: bool = True, db: Session = Depends(get_db)
):
    """List all skills"""
    query = db.query(Skill)
    if category:
        query = query.filter(Skill.category == category)
    if active_only:
        query = query.filter(Skill.is_active == True)

    skills = query.all()
    return skills


@router.get("/skills/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: int, db: Session = Depends(get_db)):
    """Get a specific skill"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.post("/skills", response_model=SkillResponse)
async def create_skill(skill_data: SkillCreate, db: Session = Depends(get_db)):
    """Create a new skill"""
    skill = Skill(
        name=skill_data.name,
        category=skill_data.category,
        description=skill_data.description,
        definition=skill_data.definition,
        is_active=True,
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.patch("/skills/{skill_id}", response_model=SkillResponse)
async def update_skill(skill_id: int, skill_data: SkillUpdate, db: Session = Depends(get_db)):
    """Update a skill"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    update_data = skill_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(skill, field, value)

    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/skills/{skill_id}")
async def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    """Delete a skill"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    db.delete(skill)
    db.commit()

    return {"success": True, "message": "Skill deleted"}


@router.post("/skills/{skill_id}/activate")
async def activate_skill(skill_id: int, db: Session = Depends(get_db)):
    """Activate a skill"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    skill.is_active = True
    db.commit()

    return {"success": True, "message": "Skill activated"}


@router.post("/skills/{skill_id}/deactivate")
async def deactivate_skill(skill_id: int, db: Session = Depends(get_db)):
    """Deactivate a skill"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    skill.is_active = False
    db.commit()

    return {"success": True, "message": "Skill deactivated"}


# Load skills from filesystem
@router.post("/skills/load-from-filesystem")
async def load_skills_from_filesystem(db: Session = Depends(get_db)):
    """Load skills from YAML files in the skills directory"""
    settings = get_settings()
    skills_dir = settings.skills_dir

    loaded_count = 0
    if os.path.exists(skills_dir):
        for filename in os.listdir(skills_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                filepath = os.path.join(skills_dir, filename)
                with open(filepath, "r") as f:
                    definition = yaml.safe_load(f)

                # Check if skill already exists
                name = os.path.splitext(filename)[0]
                existing = db.query(Skill).filter(Skill.name == name).first()

                if not existing:
                    skill = Skill(
                        name=name,
                        category=definition.get("category"),
                        description=definition.get("description"),
                        definition=definition,
                        is_active=True,
                    )
                    db.add(skill)
                    loaded_count += 1

    db.commit()
    return {"success": True, "loaded_count": loaded_count}
