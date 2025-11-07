"""Service for checking mandatory label fields"""

import logging
from typing import Any, Callable, Dict, List, Optional

from app.db.supabase_client import SupabaseClient
from app.api.schemas.compliance import ComplianceError

logger = logging.getLogger(__name__)


FIELD_MAPPING: Dict[str, Callable[[Dict], Any]] = {
    "product_name_label": lambda d: d.get("mandatory_phrases", {}).get("has_dietary_supplement_label"),
    "edrpou_code": lambda d: d.get("operator", {}).get("edrpou"),
    "operator_full_name": lambda d: d.get("operator", {}).get("name"),
    "operator_address": lambda d: d.get("operator", {}).get("address"),
    "composition": lambda d: len(d.get("ingredients", [])) > 0,
    "recommended_dose": lambda d: d.get("daily_dose"),
    "do_not_exceed_warning": lambda d: d.get("mandatory_phrases", {}).get("has_not_exceed_dose"),
    "not_substitute_warning": lambda d: d.get("mandatory_phrases", {}).get("has_not_replace_diet"),
    "keep_away_children": lambda d: d.get("mandatory_phrases", {}).get("has_keep_away_children"),
    "expiry_date": lambda d: d.get("shelf_life"),
    "net_quantity": lambda d: d.get("product_info", {}).get("quantity") or d.get("quantity"),
    "batch_number": lambda d: None,  # TODO: Claude не витягує batch number
    "allergen_info": lambda d: None,  # TODO: Claude не витягує окремо алергени
}


class MandatoryFieldsService:
    """
    Перевірка обов'язкових полів згідно Закону №2639-VIII та Наказу №1114
    
    Використовує таблицю: mandatory_fields
    """

    def __init__(self):
        """Ініціалізація з підключенням до Supabase"""
        self.supabase = SupabaseClient().client

    async def check_fields(self, label_data: Dict) -> List[ComplianceError]:
        """
        Перевірити наявність обов'язкових полів
        
        Args:
            label_data: Дані витягнуті Claude OCR (JSON)
            
        Returns:
            Список помилок ComplianceError для відсутніх полів
        """
        label_data = label_data or {}

        try:
            result = self.supabase.table("mandatory_fields").select("*").eq(
                "criticality", "critical"
            ).execute()
            records = result.data or []
        except Exception as exc:
            logger.error(f"Error fetching mandatory fields: {exc}", exc_info=True)
            raise

        logger.info(f"Checking mandatory fields: {len(records)} critical fields loaded")

        errors: List[ComplianceError] = []

        for record in records:
            field_name = record.get("field_name")
            field_name_ua = record.get("field_name_ua", field_name)

            value = self._evaluate_field(field_name, label_data)

            if self._is_missing(value):
                logger.info(f"Mandatory field missing: {field_name} ({field_name_ua})")
                errors.append(
                    ComplianceError(
                        type="mandatory_field",
                        field_name=field_name_ua,
                        regulatory_source=record.get("regulatory_source", ""),
                        article_number=record.get("article_number"),
                        error_message=record.get("error_message", "Поле обов'язкове"),
                        explanation=None,
                        severity=None,
                        recommendation=record.get("recommendation", ""),
                        penalty_amount=int(record.get("penalty_amount") or 0),
                    )
                )

        logger.info(f"Mandatory fields check completed: {len(errors)} errors found")
        return errors

    def _evaluate_field(self, field_name: Optional[str], data: Dict) -> Any:
        """Отримати значення поля з використанням мапінгу або шляху"""

        if not field_name:
            return None

        mapper = FIELD_MAPPING.get(field_name)
        if mapper:
            try:
                return mapper(data)
            except Exception as exc:
                logger.debug(f"Error evaluating field '{field_name}': {exc}")
                return None

        # Якщо мапінгу немає, пробуємо використати шлях через крапку
        return self._get_nested_value(data, field_name)

    def _is_missing(self, value: Any) -> bool:
        """Перевірити чи значення відсутнє"""

        if value is None:
            return True

        if isinstance(value, bool):
            return not value

        if isinstance(value, str):
            return len(value.strip()) == 0

        if isinstance(value, (list, tuple, set)):
            return len(value) == 0

        return False

    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Отримати значення з вкладеного словника за шляхом (наприклад: "operator.edrpou")"""

        if not path:
            return None

        current: Any = data
        for part in path.split('.'):
            if isinstance(current, dict) and part in current:
                current = current.get(part)
            else:
                return None
        return current

