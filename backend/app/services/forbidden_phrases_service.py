"""Service for checking forbidden phrases on labels"""

import logging
import re
from typing import List, Optional

from app.db.supabase_client import SupabaseClient
from app.api.schemas.compliance import ComplianceError

logger = logging.getLogger(__name__)


class ForbiddenPhrasesService:
    """
    Перевірка заборонених фраз згідно Наказу МОЗ №1114
    
    Використовує таблицю: forbidden_phrases
    """

    def __init__(self):
        """Ініціалізація з підключенням до Supabase"""
        self.supabase = SupabaseClient().client

    async def check_phrases(self, full_text: str) -> List[ComplianceError]:
        """
        Перевірити текст на заборонені фрази
        
        Args:
            full_text: Повний текст етикетки
            
        Returns:
            Список помилок ComplianceError
        """
        if not full_text:
            logger.info("Forbidden phrases check skipped: empty full_text")
            return []

        try:
            result = self.supabase.table("forbidden_phrases").select(
                "phrase, phrase_variations, category, regulatory_source, explanation, severity"
            ).execute()
            records = result.data or []
        except Exception as exc:
            logger.error(f"Error fetching forbidden phrases: {exc}", exc_info=True)
            raise

        logger.info(f"Checking forbidden phrases against {len(records)} records")

        errors: List[ComplianceError] = []

        for record in records:
            phrase = record.get("phrase")
            variations: Optional[List[str]] = record.get("phrase_variations")

            candidates: List[str] = []
            if phrase:
                candidates.append(phrase)
            if variations:
                candidates.extend(filter(None, variations))

            violation_found = False

            for candidate in candidates:
                for match in self._find_phrase_matches(candidate, full_text):
                    if self._has_negation_context(full_text, match.start()):
                        logger.debug(
                            "Skipping forbidden phrase '%s' due to negation context",
                            candidate,
                        )
                        continue

                    found_phrase = match.group(0)
                    logger.info(f"Forbidden phrase detected: {found_phrase}")
                    explanation = record.get("explanation") or ""
                    recommendation_suffix = explanation.strip()
                    recommendation = (
                        f"Видаліть фразу '{found_phrase}' з етикетки. {recommendation_suffix}"
                        if recommendation_suffix
                        else f"Видаліть фразу '{found_phrase}' з етикетки."
                    )

                    errors.append(
                        ComplianceError(
                            type="forbidden_phrase",
                            phrase=found_phrase,
                            category=record.get("category"),
                            regulatory_source=record.get("regulatory_source", ""),
                            explanation=explanation if explanation else None,
                            severity=record.get("severity"),
                            error_message=f"Знайдено заборонену фразу: {found_phrase}",
                            recommendation=recommendation,
                            penalty_amount=640000,
                        )
                    )
                    violation_found = True
                    break

                if violation_found:
                    break

        logger.info(f"Forbidden phrases check completed: {len(errors)} errors found")
        return errors

    def _normalize_text(self, text: str) -> str:
        """Привести текст до нижнього регістру, видалити зайві пробіли"""

        if not text:
            return ""
        return " ".join(text.lower().split())

    def _find_phrase_matches(self, phrase: str, text: str) -> List[re.Match]:
        """Знайти входження фрази у тексті (цілі слова, без урахування регістру)"""

        if not phrase or not text:
            return []

        pattern = re.compile(rf"\b{re.escape(phrase)}\b", re.IGNORECASE | re.UNICODE)
        return list(pattern.finditer(text))

    def _has_negation_context(self, text: str, match_start: int) -> bool:
        """Перевірити чи є заперечення перед знайденою фразою"""

        negation_phrases = [
            "не призначений",
            "не призначена",
            "не призначене",
            "не є",
            "не використовується",
            "не використовується для",
        ]

        context_start = max(0, match_start - 50)
        context = text[context_start:match_start].lower()

        return any(negation in context for negation in negation_phrases)

