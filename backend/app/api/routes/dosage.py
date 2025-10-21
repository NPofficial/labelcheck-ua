"""Dosage calculation and recommendation routes"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

from app.api.schemas.label import DosageRequest
from app.api.schemas.response import APIResponse
from app.services.dosage_service import DosageService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/calculate")
async def calculate_dosage(request: DosageRequest):
    """
    Calculate recommended dosage
    
    - **request**: Patient information and medication details
    - Returns: Recommended dosage and instructions
    """
    try:
        logger.info(f"Calculating dosage for: {request.medication_name}")
        
        dosage_service = DosageService()
        result = await dosage_service.calculate_dosage(request)
        
        return APIResponse(
            success=True,
            data=result,
            message="Дозування розраховано"
        )
        
    except Exception as e:
        logger.error(f"Error calculating dosage: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations")
async def get_dosage_recommendations(
    medication: str,
    age: Optional[int] = None,
    weight: Optional[float] = None
):
    """
    Get dosage recommendations for a medication
    
    - **medication**: Medication name
    - **age**: Patient age
    - **weight**: Patient weight in kg
    """
    try:
        logger.info(f"Getting dosage recommendations for: {medication}")
        
        # TODO: Implement recommendation logic
        
        return APIResponse(
            success=True,
            data={"medication": medication, "recommendations": []},
            message="Рекомендації отримано"
        )
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

