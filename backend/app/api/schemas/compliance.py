"""Compliance-related Pydantic schemas"""

from pydantic import BaseModel
from typing import Optional, List


class ComplianceError(BaseModel):
    """Помилка compliance (заборонені фрази або відсутні поля)"""

    type: str  # "forbidden_phrase" або "mandatory_field"
    field_name: Optional[str] = None  # Для mandatory fields
    phrase: Optional[str] = None  # Для forbidden phrases
    category: Optional[str] = None  # Для forbidden phrases
    regulatory_source: str
    article_number: Optional[str] = None
    error_message: str
    explanation: Optional[str] = None  # Для forbidden phrases
    severity: Optional[str] = None  # Для forbidden phrases
    recommendation: str
    penalty_amount: int


class ComplianceCheckResult(BaseModel):
    """Результат перевірки compliance"""

    errors: List[ComplianceError]
    total_forbidden_phrases: int
    total_missing_fields: int
    total_penalty: int

