from __future__ import annotations

from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from jartbrowser.services.vision import (
    VisionService,
    VisionCaptureType,
    OCREngine,
    get_vision_service,
)


router = APIRouter()

# Singleton VisionService instance
vision_service: VisionService = get_vision_service()


class CaptureRequest(BaseModel):
    url: Optional[str] = None
    area: Optional[str] = None
    capture_type: Optional[VisionCaptureType] = None


class OCRRequest(BaseModel):
    capture_id: str
    engine: Optional[OCREngine] = None


class AnalyzeRequest(BaseModel):
    image_id: Optional[str] = None
    image_data: Optional[str] = None  # base64 or data URL
    options: Optional[Dict[str, Any]] = None


class ElementsRequest(BaseModel):
    image_id: Optional[str] = None
    image_data: Optional[str] = None
    types: Optional[List[str]] = None


class CompareRequest(BaseModel):
    image_a_id: Optional[str] = None
    image_b_id: Optional[str] = None
    image_a_data: Optional[str] = None
    image_b_data: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


@router.post("/vision/capture")
async def capture_capture(req: CaptureRequest):
    """Capture a screenshot or viewport."""
    try:
        return vision_service.capture(
            url=req.url,
            area=req.area,
            capture_type=req.capture_type,  # type: ignore[arg-type]
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/vision/captures")
async def list_captures():
    return vision_service.list_captures()


@router.get("/vision/captures/{id}")
async def get_capture(id: str):
    cap = vision_service.get_capture(id)
    if cap is None:
        raise HTTPException(status_code=404, detail="Capture not found")
    return cap


@router.post("/vision/ocr")
async def ocr(req: OCRRequest):
    if not req.capture_id:
        raise HTTPException(status_code=400, detail="capture_id is required")
    return vision_service.ocr(req.capture_id, engine=req.engine)


@router.post("/vision/analyze")
async def analyze(req: AnalyzeRequest):
    return vision_service.analyze(
        image_id=req.image_id, image_data=req.image_data, options=req.options
    )


@router.post("/vision/elements")
async def detect_elements(req: ElementsRequest):
    return vision_service.detect_elements(
        image_id=req.image_id, image_data=req.image_data, types=req.types
    )


@router.post("/vision/compare")
async def compare(req: CompareRequest):
    return vision_service.compare(
        image_a_id=req.image_a_id,
        image_b_id=req.image_b_id,
        image_a_data=req.image_a_data,
        image_b_data=req.image_b_data,
        options=req.options,
    )
