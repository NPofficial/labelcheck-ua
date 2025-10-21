"""Label checking/validation routes"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import logging

from app.api.schemas.validation import ValidationResult
from app.api.schemas.response import APIResponse
from app.services.validation_service import ValidationService
from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/check", response_model=APIResponse[ValidationResult])
async def check_label(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    """
    Check/validate a pharmaceutical label
    
    - **file**: Image or PDF file of the label
    - **text**: Text content of the label
    - Returns: Validation result with errors and warnings
    """
    try:
        if not file and not text:
            raise HTTPException(
                status_code=400,
                detail="Потрібно надати файл або текст"
            )
        
        validation_service = ValidationService()
        
        if file:
            logger.info(f"Validating label from file: {file.filename}")
            
            # Process file
            document_service = DocumentService()
            extracted_text = await document_service.extract_text(file)
            
            # Validate extracted text
            result = await validation_service.validate_label(extracted_text)
        else:
            logger.info("Validating label from text input")
            result = await validation_service.validate_label(text)
        
        return APIResponse(
            success=True,
            data=result,
            message="Перевірку завершено"
        )
        
    except Exception as e:
        logger.error(f"Error checking label: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{result_id}", response_model=APIResponse[ValidationResult])
async def get_validation_result(result_id: str):
    """
    Get validation result by ID
    
    - **result_id**: Validation result identifier
    """
    try:
        # TODO: Retrieve from database
        logger.info(f"Retrieving validation result: {result_id}")
        
        return APIResponse(
            success=True,
            data={"id": result_id, "status": "completed"},
            message="Результат знайдено"
        )
    except Exception as e:
        logger.error(f"Error retrieving result: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail="Result not found")

