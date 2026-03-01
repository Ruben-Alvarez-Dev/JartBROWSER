"""Tests for VisionService"""

import pytest
from jartbrowser.services.vision import (
    VisionService,
    VisionCaptureType,
    OCREngine,
)


@pytest.fixture
def vision_service():
    return VisionService()


@pytest.mark.asyncio
async def test_capture_screenshot(vision_service):
    """Test screenshot capture"""
    capture = await vision_service.capture_screenshot(capture_type=VisionCaptureType.SCREENSHOT)
    assert capture is not None
    assert capture.capture_type == VisionCaptureType.SCREENSHOT
    assert capture.id is not None


@pytest.mark.asyncio
async def test_capture_region(vision_service):
    """Test region capture"""
    capture = await vision_service.capture_region(x=0, y=0, width=100, height=100)
    assert capture is not None
    assert capture.bounding_box is not None


@pytest.mark.asyncio
async def test_capture_element(vision_service):
    """Test element capture"""
    capture = await vision_service.capture_element(selector="#button")
    assert capture is not None


@pytest.mark.asyncio
async def test_capture_full_page(vision_service):
    """Test full page capture"""
    capture = await vision_service.capture_full_page()
    assert capture is not None
    assert capture.capture_type == VisionCaptureType.FULL_PAGE


def test_get_capture(vision_service):
    """Test getting a capture"""
    # Capture first
    capture = vision_service._captures["test"] = type(
        "Capture",
        (),
        {
            "id": "test",
            "capture_type": VisionCaptureType.SCREENSHOT,
            "timestamp": None,
        },
    )()

    retrieved = vision_service.get_capture("test")
    assert retrieved is not None


def test_get_captures(vision_service):
    """Test listing captures"""
    captures = vision_service.get_captures()
    assert isinstance(captures, list)


@pytest.mark.asyncio
async def test_extract_text(vision_service):
    """Test OCR text extraction"""
    # Create a mock capture
    from datetime import datetime

    capture_id = "ocr-test"
    vision_service._captures[capture_id] = type(
        "Capture",
        (),
        {
            "id": capture_id,
            "capture_type": VisionCaptureType.SCREENSHOT,
            "image_data": "",
            "width": 800,
            "height": 600,
            "timestamp": datetime.utcnow(),
        },
    )()

    result = await vision_service.extract_text(
        capture_id=capture_id,
        engine=OCREngine.TESSERACT,
    )
    assert result is not None
    assert result.engine == OCREngine.TESSERACT


@pytest.mark.asyncio
async def test_detect_elements(vision_service):
    """Test element detection"""
    from datetime import datetime

    capture_id = "elements-test"
    vision_service._captures[capture_id] = type(
        "Capture",
        (),
        {
            "id": capture_id,
            "capture_type": VisionCaptureType.SCREENSHOT,
            "image_data": "",
            "width": 800,
            "height": 600,
            "timestamp": datetime.utcnow(),
        },
    )()

    elements = await vision_service.detect_elements(capture_id)
    assert isinstance(elements, list)


@pytest.mark.asyncio
async def test_analyze_image(vision_service):
    """Test image analysis"""
    from datetime import datetime

    capture_id = "analyze-test"
    vision_service._captures[capture_id] = type(
        "Capture",
        (),
        {
            "id": capture_id,
            "capture_type": VisionCaptureType.SCREENSHOT,
            "image_data": "",
            "width": 800,
            "height": 600,
            "timestamp": datetime.utcnow(),
        },
    )()

    analysis = await vision_service.analyze_image(capture_id)
    assert analysis is not None
    assert "width" in analysis
    assert "height" in analysis


@pytest.mark.asyncio
async def test_compare_images(vision_service):
    """Test image comparison"""
    from datetime import datetime

    capture1_id = "compare1"
    capture2_id = "compare2"

    for cid in [capture1_id, capture2_id]:
        vision_service._captures[cid] = type(
            "Capture",
            (),
            {
                "id": cid,
                "capture_type": VisionCaptureType.SCREENSHOT,
                "image_data": "",
                "width": 800,
                "height": 600,
                "timestamp": datetime.utcnow(),
            },
        )()

    comparison = await vision_service.compare_images(capture1_id, capture2_id)
    assert comparison is not None
