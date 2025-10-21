"""Database models"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LabelModel(BaseModel):
    """Label database model"""
    id: str = Field(description="Label ID")
    product_name: str = Field(description="Product name")
    manufacturer: str = Field(description="Manufacturer")
    content: dict = Field(description="Label content")
    format: str = Field(description="File format")
    file_url: Optional[str] = Field(default=None, description="File URL")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ValidationResultModel(BaseModel):
    """Validation result database model"""
    id: str = Field(description="Validation result ID")
    label_id: Optional[str] = Field(default=None, description="Associated label ID")
    is_valid: bool = Field(description="Validation status")
    score: float = Field(description="Quality score")
    errors_count: int = Field(description="Number of errors")
    warnings_count: int = Field(description="Number of warnings")
    result_data: dict = Field(description="Full validation result")
    validated_at: datetime = Field(default_factory=datetime.utcnow)


class RegulatoryDataModel(BaseModel):
    """Regulatory data model"""
    id: str = Field(description="Regulation ID")
    name: str = Field(description="Regulation name")
    category: str = Field(description="Category")
    content: dict = Field(description="Regulation content")
    effective_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserModel(BaseModel):
    """User model"""
    id: str = Field(description="User ID")
    email: str = Field(description="Email address")
    full_name: Optional[str] = Field(default=None)
    organization: Optional[str] = Field(default=None)
    role: str = Field(default="user", description="User role")
    created_at: datetime = Field(default_factory=datetime.utcnow)

