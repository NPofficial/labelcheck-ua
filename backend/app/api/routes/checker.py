"""API routes for label checking"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from fastapi.responses import FileResponse
from typing import Dict
from pydantic import BaseModel
import logging
import uuid
from datetime import datetime
import os

from app.services.claude_ocr_service import ClaudeOCRService
from app.services.dosage_service import DosageService
from app.services.report_service import ReportService
from app.services.forbidden_phrases_service import ForbiddenPhrasesService
from app.services.mandatory_fields_service import MandatoryFieldsService
from app.services.substance_mapper_service import SubstanceMapperService
from app.api.schemas.validation import DosageCheckResult
from app.api.schemas.compliance import ComplianceCheckResult
from app.db.supabase_client import SupabaseClient
from app.config import settings


class FullCheckRequest(BaseModel):
    """Request model for full check endpoint"""
    check_id: str

router = APIRouter(prefix="/api/check-label", tags=["checker"])
logger = logging.getLogger(__name__)

# Initialize services
ocr_service = ClaudeOCRService()
dosage_service = DosageService()
report_service = ReportService()
forbidden_service = ForbiddenPhrasesService()
mandatory_service = MandatoryFieldsService()
mapper_service = SubstanceMapperService()
supabase = SupabaseClient().client


@router.post("/quick")
async def quick_check(
    file: UploadFile = File(...)
) -> Dict:
    """
    Step 1: Quick OCR analysis to extract ingredients list
    
    This is optimized for speed and cost (~$0.006 per check)
    
    Args:
        file: Uploaded image file (JPEG, PNG) or PDF
        
    Returns:
        {
            "check_id": "uuid",
            "ingredients": [...],
            "product_info": {...},
            "extracted_at": "ISO datetime"
        }
    """
    try:
        # Generate unique check ID
        check_id = str(uuid.uuid4())
        
        # Validate file type
        ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "application/pdf"]
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.content_type}. Allowed: {', '.join(ALLOWED_TYPES)}"
            )
        
        # Read file
        file_bytes = await file.read()
        
        # Validate file size (max 10MB)
        max_size = settings.max_file_size if hasattr(settings, 'max_file_size') else 10 * 1024 * 1024
        if len(file_bytes) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {max_size / (1024*1024):.1f}MB."
            )
        
        # Extract data using Claude OCR
        logger.info(f"Quick check started: {check_id}")
        label_data = await ocr_service.extract_label_data(file_bytes)
        
        # Store extracted data in Supabase for Step 2
        try:
            supabase.table("check_sessions").insert({
                "check_id": check_id,
                "label_data": label_data,
                "status": "extracted",
                "created_at": datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            logger.warning(f"Could not save to Supabase: {e}. Continuing without saving.")
            # Continue even if Supabase save fails
        
        # Return extracted data
        return {
            "check_id": check_id,
            "ingredients": label_data.get("ingredients", []),
            "product_info": {
                "name": label_data.get("product_name"),
                "form": label_data.get("form"),
                "quantity": label_data.get("quantity"),
                "batch_number": label_data.get("batch_number")
            },
            "allergens": label_data.get("allergens", []),
            "allergen_statement": label_data.get("allergen_statement"),
            "mandatory_phrases": label_data.get("mandatory_phrases"),
            "full_text": label_data.get("full_text"),
            "operator": label_data.get("operator"),
            "warnings": label_data.get("warnings"),
            "daily_dose": label_data.get("daily_dose"),
            "storage": label_data.get("storage"),
            "manufacturer": label_data.get("manufacturer"),
            "shelf_life": label_data.get("shelf_life"),
            "tech_specs": label_data.get("tech_specs"),
            "extracted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quick check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/full")
async def full_check(
    request: FullCheckRequest = Body(...)
) -> Dict:
    """
    Step 2: Full validation check using DosageService
    
    This loads only relevant substances from DB for efficiency
    
    Args:
        request: Request body with check_id from Step 1
        
    Returns:
        Full validation report with errors, warnings, and recommendations
    """
    try:
        check_id = request.check_id
        
        # Retrieve label data from Supabase
        try:
            result = supabase.table("check_sessions").select("*").eq(
                "check_id", check_id
            ).single().execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Check ID not found")
            
            label_data = result.data["label_data"]
        except Exception as e:
            logger.error(f"Error retrieving check session: {e}")
            raise HTTPException(status_code=404, detail=f"Check ID not found: {str(e)}")
        
        ingredients = label_data.get("ingredients", [])
        
        logger.info(f"Full check started: {check_id} ({len(ingredients)} ingredients)")
        
        # Парсити інгредієнти через mapper для статистики та обогачення даних
        parsed_ingredients = []
        for ingredient in ingredients:
            parsed = await mapper_service.parse_ingredient(
                ingredient.get("name"),
                ingredient.get("quantity"),
                ingredient.get("unit", "мг")
            )
            
            # Додати результат парсингу до інгредієнта
            # found = True якщо matched = True АБО є source (excipient, plant тощо)
            is_found = parsed.get("matched", False) or parsed.get("source") is not None
            
            ingredient_with_parsed = {
                **ingredient,
                "found": is_found,
                "base_substance": parsed.get("base_substance"),
                "form": parsed.get("form"),  # Форма речовини (наприклад, "Цитрат", "Піридоксину гідрохлорид")
                "source": parsed.get("source"),
                "type": parsed.get("type", ingredient.get("type")),
                "elemental_quantity": parsed.get("elemental_quantity"),
                "coefficient_used": parsed.get("coefficient_used"),
                "is_extract": parsed.get("is_extract", False),
                "extract_type": parsed.get("extract_type"),
                "ratio": parsed.get("ratio")
            }
            parsed_ingredients.append(ingredient_with_parsed)
        
        # Рахувати статистику
        substances_not_found = sum(1 for ing in parsed_ingredients if not ing.get("found", False))
        
        logger.info(f"Parsed ingredients: {len(parsed_ingredients)} total, {substances_not_found} not found")
        
        # Підготувати інгредієнти для DosageService з base_substance та elemental_quantity
        # КРИТИЧНО: EFSA Upper Limits встановлені для ЕЛЕМЕНТАРНИХ форм, не для сполук!
        # Наприклад: "Магній" (base_substance) з elemental_quantity = 100 мг,
        # а не "цитрат магнію" (форма) з quantity = 500 мг
        dosage_ingredients = []
        for ing in parsed_ingredients:
            # Використати base_substance та elemental_quantity (які mapper розрахував з коефіцієнтами)
            base_substance = ing.get("base_substance") or ing.get("name")
            elemental_qty = ing.get("elemental_quantity")
            
            # Якщо elemental_quantity не розраховано (наприклад, для excipients), використати оригінальну кількість
            if elemental_qty is None:
                elemental_qty = ing.get("quantity")
            
            dosage_ing = {
                "name": base_substance,  # "Магній" замість "цитрат магнію"
                "quantity": elemental_qty,  # 100 замість 500 (якщо коефіцієнт 0.2)
                "unit": ing.get("unit", "мг"),
                "form": ing.get("form"),  # Зберегти форму для додаткової перевірки
                "type": ing.get("type")
            }
            dosage_ingredients.append(dosage_ing)
            
            logger.debug(
                f"Dosage ingredient: '{ing.get('name')}' ({ing.get('quantity')} {ing.get('unit')}) "
                f"→ '{base_substance}' ({elemental_qty} {ing.get('unit')})"
            )
        
        # Run dosage validation (uses existing DosageService)
        # Передаємо base_substance та elemental_quantity для правильної перевірки EFSA limits
        dosage_result: DosageCheckResult = await dosage_service.check_dosages(
            dosage_ingredients
        )
        
        # НОВИЙ КОД: Перевірка заборонених фраз
        full_text = label_data.get("full_text", "")
        forbidden_errors = await forbidden_service.check_phrases(full_text)

        # НОВИЙ КОД: Перевірка обов'язкових полів
        mandatory_errors = await mandatory_service.check_fields(label_data)

        # Об'єднати всі типи помилок
        all_compliance_errors = forbidden_errors + mandatory_errors

        compliance_result = ComplianceCheckResult(
            errors=all_compliance_errors,
            total_forbidden_phrases=sum(
                1 for error in all_compliance_errors if error.type == "forbidden_phrase"
            ),
            total_missing_fields=sum(
                1 for error in all_compliance_errors if error.type == "mandatory_field"
            ),
            total_penalty=sum(error.penalty_amount for error in all_compliance_errors),
        )

        # TODO: Add other validation checks:
        # - Mandatory fields check (18 fields)
        # - Forbidden phrases check (50+ phrases)
        # - Format validation (font size, units)
        
        dosage_penalty_total = sum(error.penalty_amount for error in dosage_result.errors)
        compliance_penalty_total = compliance_result.total_penalty

        # Build comprehensive report
        report = {
            "check_id": check_id,
            "is_valid": dosage_result.all_valid and len(all_compliance_errors) == 0,
            "product_info": {
                "name": label_data.get("product_name"),
                "form": label_data.get("form"),
                "quantity": label_data.get("quantity"),
                "batch_number": label_data.get("batch_number"),
                "ingredients": parsed_ingredients  # Використовуємо обогачені інгредієнти
            },
            # Оператор ринку та виробник
            "operator": label_data.get("operator"),
            "manufacturer": label_data.get("manufacturer"),
            # Обов'язкові поля з етикетки
            "mandatory_phrases": label_data.get("mandatory_phrases"),
            "full_text": label_data.get("full_text"),
            # Інша інформація з етикетки
            "label_warnings": label_data.get("warnings"),  # Застереження з етикетки
            "daily_dose": label_data.get("daily_dose"),
            "storage": label_data.get("storage"),
            "shelf_life": label_data.get("shelf_life"),
            "tech_specs": label_data.get("tech_specs"),
            "allergens": label_data.get("allergens"),
            "allergen_statement": label_data.get("allergen_statement"),
            # Результати перевірки
            "errors": [error.dict() for error in dosage_result.errors],
            "warnings": [warning.dict() for warning in dosage_result.warnings],
            "compliance_errors": [error.dict() for error in all_compliance_errors],
            "stats": {
                "total_ingredients": len(parsed_ingredients),
                "substances_not_found": substances_not_found,  # Використовуємо правильну статистику
                "total_dosage_errors": len(dosage_result.errors),
                "total_dosage_warnings": len(dosage_result.warnings),
                "total_forbidden_phrases": compliance_result.total_forbidden_phrases,
                "total_missing_fields": compliance_result.total_missing_fields,
            },
            "penalties": {
                "dosage_penalties": dosage_penalty_total,
                "compliance_penalties": compliance_penalty_total,
                "total_amount": dosage_penalty_total + compliance_penalty_total,
                "currency": "UAH"
            },
            "checked_at": datetime.utcnow().isoformat()
        }
        
        # Update session in Supabase
        try:
            supabase.table("check_sessions").update({
                "status": "completed",
                "report": report,
                "completed_at": datetime.utcnow().isoformat()
            }).eq("check_id", check_id).execute()
        except Exception as e:
            logger.warning(f"Could not update Supabase: {e}. Continuing without saving.")
        
        logger.info(
            f"Full check completed: {check_id} - "
            f"dosage errors={len(dosage_result.errors)}, "
            f"dosage warnings={len(dosage_result.warnings)}, "
            f"forbidden_phrases={compliance_result.total_forbidden_phrases}, "
            f"missing_fields={compliance_result.total_missing_fields}"
        )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Full check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{check_id}/report.pdf")
async def download_pdf_report(check_id: str):
    """
    Download PDF validation report
    
    Args:
        check_id: UUID from check session
        
    Returns:
        PDF file
    """
    try:
        # Retrieve report data
        result = supabase.table("check_sessions").select("*").eq(
            "check_id", check_id
        ).single().execute()
        
        if not result.data or not result.data.get("report"):
            raise HTTPException(status_code=404, detail="Report not found")
        
        report_data = result.data["report"]
        
        # Generate PDF
        # Create temp directory if it doesn't exist
        temp_dir = "/tmp"
        os.makedirs(temp_dir, exist_ok=True)
        output_path = os.path.join(temp_dir, f"{check_id}.pdf")
        
        await report_service.generate_pdf_report(
            check_id=check_id,
            report_data=report_data,
            output_path=output_path
        )
        
        # Return PDF file
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=f"LabelCheck_Report_{check_id[:8]}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

