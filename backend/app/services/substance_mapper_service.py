"""Service for mapping ingredient names to base substances and calculating elemental content"""

import logging
from typing import Dict, Optional

from app.db.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)


class SubstanceMapperService:
    """Maps ingredient variations to base substances and converts to elemental content"""

    def __init__(self):
        self.supabase = SupabaseClient().client
        logger.info("SubstanceMapperService initialized")

    async def parse_ingredient(
        self,
        name: str,
        quantity: Optional[float],
        unit: str,
    ) -> Dict:
        """
        Parse ingredient name and calculate elemental content

        Args:
            name: Ingredient name (e.g. "цитрат магнію")
            quantity: Amount (e.g. 500)
            unit: Unit (e.g. "мг")

        Returns:
            {
                "base_substance": "Магній",
                "form": "Цитрат",
                "original_quantity": 500,
                "elemental_quantity": 100,  # 500 × 0.20 (max coefficient)
                "coefficient_used": 0.20,
                "unit": "мг",
                "matched": True
            }
        """
        # Якщо немає кількості - повернути як є
        if quantity is None:
            return {
                "base_substance": name,
                "form": None,
                "original_quantity": None,
                "elemental_quantity": None,
                "coefficient_used": 1.0,
                "unit": unit,
                "matched": False,
            }

        name_normalized = self._normalize_name(name)
        form_data = await self._find_form_in_db(name_normalized)

        if form_data:
            coefficient = form_data.get("elemental_coefficient_max") or form_data.get(
                "elemental_coefficient"
            )
            if coefficient is None:
                logger.warning(
                    "Coefficient missing for %s (%s), fallback to 1.0",
                    form_data.get("substance_name_ua"),
                    form_data.get("form_name_ua"),
                )
                coefficient = 1.0

            elemental_qty = round(quantity * float(coefficient), 2)

            return {
                "base_substance": form_data.get("substance_name_ua", name),
                "form": form_data.get("form_name_ua"),
                "original_quantity": quantity,
                "elemental_quantity": elemental_qty,
                "coefficient_used": float(coefficient),
                "unit": unit,
                "matched": True,
            }

        logger.warning(f"Form not found in DB: {name}")
        return {
            "base_substance": name,
            "form": None,
            "original_quantity": quantity,
            "elemental_quantity": quantity,
            "coefficient_used": 1.0,
            "unit": unit,
            "matched": False,
        }

    async def _find_form_in_db(self, name_normalized: str) -> Optional[Dict]:
        """
        Search for form in substance_form_conversions table

        Args:
            name_normalized: Normalized ingredient name

        Returns:
            Row from DB or None
        """
        try:
            result = self.supabase.table("substance_form_conversions").select("*").execute()

            for row in result.data or []:
                variations = row.get("name_variations", [])
                for variation in variations or []:
                    if self._normalize_name(variation) == name_normalized:
                        logger.info(
                            "Mapped form: %s -> %s (%s)",
                            name_normalized,
                            row.get("substance_name_ua"),
                            row.get("form_name_ua"),
                        )
                        return row
            return None
        except Exception as exc:
            logger.error(f"Error searching form in DB: {exc}", exc_info=True)
            return None

    def _normalize_name(self, name: str) -> str:
        """
        Normalize ingredient name for matching

        Args:
            name: Original name

        Returns:
            Normalized name (lowercase, trimmed)
        """
        return (name or "").lower().strip()

