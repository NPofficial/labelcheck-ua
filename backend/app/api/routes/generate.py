"""Label generation routes"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import logging

from app.api.schemas.label import LabelGenerateRequest
from app.api.schemas.response import LabelGenerateResponse, APIResponse
from app.services.generation_service import GenerationService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=APIResponse[LabelGenerateResponse])
async def generate_label(
    request: LabelGenerateRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a pharmaceutical label
    
    - **request**: Label data and configuration
    - Returns: Generated label ID, download URL, preview URL
    """
    try:
        logger.info(f"Generating label for product: {request.product_info.name}")
        
        # TODO: Implement actual generation logic
        generation_service = GenerationService()
        result = await generation_service.generate_label(request)
        
        return APIResponse(
            success=True,
            data=result,
            message="Етикетку успішно згенеровано"
        )
        
    except Exception as e:
        logger.error(f"Error generating label: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generate/{label_id}")
async def get_generated_label(label_id: str):
    """
    Get generated label by ID
    
    - **label_id**: Label identifier
    """
    try:
        # TODO: Implement retrieval logic
        return APIResponse(
            success=True,
            data={"id": label_id, "status": "generated"},
            message="Етикетку знайдено"
        )
    except Exception as e:
        logger.error(f"Error retrieving label: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail="Label not found")


@router.get("/generate/{label_id}/download")
async def download_label(label_id: str, format: Optional[str] = "pdf"):
    """
    Download generated label
    
    - **label_id**: Label identifier
    - **format**: Output format (pdf, png, docx)
    """
    try:
        # TODO: Implement download logic
        logger.info(f"Downloading label {label_id} in {format} format")
        
        return APIResponse(
            success=True,
            data={"download_url": f"/download/{label_id}.{format}"},
            message="Завантаження готове"
        )
    except Exception as e:
        logger.error(f"Error downloading label: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

