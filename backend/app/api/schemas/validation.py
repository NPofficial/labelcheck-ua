"""Validation-related Pydantic schemas"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ValidationSeverity(str, Enum):
    """Validation error severity"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationError(BaseModel):
    """Validation error/warning"""
    field: str = Field(description="Field name or section")
    message: str = Field(description="Error/warning message")
    severity: ValidationSeverity = Field(description="Severity level")
    code: str = Field(description="Error code")
    suggestion: Optional[str] = Field(default=None, description="Suggested fix")


class ValidationResult(BaseModel):
    """Validation result"""
    id: str = Field(description="Validation result ID")
    is_valid: bool = Field(description="Overall validation status")
    errors: List[ValidationError] = Field(default_factory=list, description="List of errors")
    warnings: List[ValidationError] = Field(default_factory=list, description="List of warnings")
    validated_at: str = Field(description="Validation timestamp")
    label_data: Optional[dict] = Field(default=None, description="Extracted label data")
    score: Optional[float] = Field(default=None, description="Quality score (0-100)")


class RegulatoryCheck(BaseModel):
    """Regulatory compliance check"""
    regulation_id: str = Field(description="Regulation identifier")
    name: str = Field(description="Regulation name")
    is_compliant: bool = Field(description="Compliance status")
    details: Optional[str] = Field(default=None, description="Check details")


class ComplianceReport(BaseModel):
    """Full compliance report"""
    validation_result: ValidationResult
    regulatory_checks: List[RegulatoryCheck]
    overall_compliance: bool = Field(description="Overall compliance status")
    report_generated_at: str = Field(description="Report generation timestamp")


class DosageError(BaseModel):
    """Dosage validation error with penalty information"""
    ingredient: str = Field(description="Ingredient name")
    message: str = Field(description="Error message")
    current_dose: Optional[str] = Field(default=None, description="Current dose (e.g., '1000 mg')")
    max_allowed: Optional[str] = Field(default=None, description="Maximum allowed dose")
    three_times_limit: Optional[str] = Field(default=None, description="Triple limit dose")
    current_form: Optional[str] = Field(default=None, description="Current form used")
    allowed_forms: Optional[List[str]] = Field(default=None, description="List of allowed forms")
    regulatory_source: str = Field(description="Regulatory source reference")
    recommendation: str = Field(description="Recommendation to fix the issue")
    penalty_amount: int = Field(description="Penalty amount in UAH")


class DosageWarning(BaseModel):
    """Dosage validation warning"""
    ingredient: str = Field(description="Ingredient name")
    message: str = Field(description="Warning message")
    current_dose: Optional[str] = Field(default=None, description="Current dose")
    max_allowed: Optional[str] = Field(default=None, description="Maximum recommended dose")
    recommendation: str = Field(description="Recommendation")


class DosageCheckResult(BaseModel):
    """Result of dosage validation check"""
    errors: List[DosageError] = Field(default_factory=list, description="Critical dosage errors")
    warnings: List[DosageWarning] = Field(default_factory=list, description="Dosage warnings")
    all_valid: bool = Field(description="True if all dosages are valid")
    total_ingredients_checked: int = Field(description="Total number of ingredients checked")
    substances_not_found: int = Field(default=0, description="Number of substances not found in database")

