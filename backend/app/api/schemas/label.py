"""Label-related Pydantic schemas"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class DosageForm(str, Enum):
    """Pharmaceutical dosage forms"""
    TABLETS = "Таблетки"
    CAPSULES = "Капсули"
    SYRUP = "Сироп"
    SOLUTION = "Розчин"
    SUSPENSION = "Суспензія"
    OINTMENT = "Мазь"
    CREAM = "Крем"
    GEL = "Гель"
    POWDER = "Порошок"
    OTHER = "Інше"


class ProductInfo(BaseModel):
    """Product information"""
    name: str = Field(description="Product name")
    manufacturer: str = Field(description="Manufacturer name")
    dosage_form: str = Field(description="Dosage form")
    strength: str = Field(description="Product strength/dosage")


class Ingredient(BaseModel):
    """Ingredient information"""
    name: str = Field(description="Ingredient name")
    quantity: str = Field(description="Quantity")
    unit: str = Field(description="Unit of measurement")
    is_active: bool = Field(default=True, description="Is active ingredient")


class Dosage(BaseModel):
    """Dosage instructions"""
    population: str = Field(description="Target population (adults, children, etc.)")
    instruction: str = Field(description="Dosage instruction")
    frequency: str = Field(description="Frequency of administration")
    duration: str = Field(description="Duration of treatment")


class WarningSeverity(str, Enum):
    """Warning severity levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class WarningType(str, Enum):
    """Warning types"""
    CONTRAINDICATION = "contraindication"
    PRECAUTION = "precaution"
    SIDE_EFFECT = "side_effect"
    INTERACTION = "interaction"


class Warning(BaseModel):
    """Warning information"""
    type: WarningType = Field(description="Warning type")
    severity: WarningSeverity = Field(description="Severity level")
    description: str = Field(description="Warning description")


class OperatorInfo(BaseModel):
    """Operator/manufacturer information"""
    name: str = Field(description="Operator name")
    license_number: str = Field(description="License number")
    production_date: str = Field(description="Production date")
    expiry_date: str = Field(description="Expiry date")
    batch_number: str = Field(description="Batch number")


class LabelData(BaseModel):
    """Complete label data"""
    product_info: ProductInfo
    ingredients: List[Ingredient]
    dosages: List[Dosage]
    warnings: List[Warning]
    operator_info: OperatorInfo


class LabelGenerateRequest(BaseModel):
    """Label generation request"""
    product_info: ProductInfo
    ingredients: List[Ingredient]
    dosages: List[Dosage]
    warnings: List[Warning]
    operator_info: OperatorInfo
    format: str = Field(default="pdf", description="Output format (pdf, png, docx)")


class DosageRequest(BaseModel):
    """Dosage calculation request"""
    medication_name: str = Field(description="Medication name")
    patient_age: Optional[int] = Field(default=None, description="Patient age in years")
    patient_weight: Optional[float] = Field(default=None, description="Patient weight in kg")
    indication: Optional[str] = Field(default=None, description="Medical indication")

