"""Database queries"""

from typing import Optional, List, Dict
import logging

from app.db.supabase_client import supabase_client
from app.db.models import LabelModel, ValidationResultModel

logger = logging.getLogger(__name__)


class LabelQueries:
    """Queries for labels table"""
    
    TABLE_NAME = "labels"
    
    @staticmethod
    async def create_label(label_data: Dict) -> LabelModel:
        """Create a new label"""
        try:
            result = await supabase_client.insert(
                LabelQueries.TABLE_NAME,
                label_data
            )
            return LabelModel(**result)
        except Exception as e:
            logger.error(f"Error creating label: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_label(label_id: str) -> Optional[LabelModel]:
        """Get label by ID"""
        try:
            results = await supabase_client.select(
                LabelQueries.TABLE_NAME,
                filters={"id": label_id}
            )
            return LabelModel(**results[0]) if results else None
        except Exception as e:
            logger.error(f"Error getting label: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def list_labels(limit: int = 50, offset: int = 0) -> List[LabelModel]:
        """List labels"""
        try:
            results = await supabase_client.select(LabelQueries.TABLE_NAME)
            return [LabelModel(**r) for r in results]
        except Exception as e:
            logger.error(f"Error listing labels: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def update_label(label_id: str, data: Dict) -> LabelModel:
        """Update label"""
        try:
            result = await supabase_client.update(
                LabelQueries.TABLE_NAME,
                data,
                {"id": label_id}
            )
            return LabelModel(**result)
        except Exception as e:
            logger.error(f"Error updating label: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def delete_label(label_id: str) -> bool:
        """Delete label"""
        try:
            return await supabase_client.delete(
                LabelQueries.TABLE_NAME,
                {"id": label_id}
            )
        except Exception as e:
            logger.error(f"Error deleting label: {e}", exc_info=True)
            raise


class ValidationQueries:
    """Queries for validation_results table"""
    
    TABLE_NAME = "validation_results"
    
    @staticmethod
    async def create_validation_result(data: Dict) -> ValidationResultModel:
        """Create a validation result"""
        try:
            result = await supabase_client.insert(
                ValidationQueries.TABLE_NAME,
                data
            )
            return ValidationResultModel(**result)
        except Exception as e:
            logger.error(f"Error creating validation result: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_validation_result(result_id: str) -> Optional[ValidationResultModel]:
        """Get validation result by ID"""
        try:
            results = await supabase_client.select(
                ValidationQueries.TABLE_NAME,
                filters={"id": result_id}
            )
            return ValidationResultModel(**results[0]) if results else None
        except Exception as e:
            logger.error(f"Error getting validation result: {e}", exc_info=True)
            raise

