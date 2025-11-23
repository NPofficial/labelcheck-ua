"""Service for mapping ingredient names to base substances and calculating elemental content"""

import json
import logging
import re
from typing import Dict, Optional

from app.db.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

# Keywords для розпізнавання екстрактів
EXTRACT_KEYWORDS = [
    "екстракт", "extract", "экстракт",
    "порошок", "powder", "порошка",
    "композиція", "composition", "комплекс",
    "олія", "oil", "масло",
    "концентрат", "concentrate",
    "витяжка", "настойка", "настой", "тинктура"
]


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
                "matched": True,
                "is_extract": False,
                "extract_type": None,
                "ratio": None
            }
        """
        logger.debug(f"📥 parse_ingredient: name='{name}', quantity={quantity}, unit='{unit}'")
        
        # Зберегти оригінальну назву для відображення
        original_name = name
        
        # 1. Видалити дужки та все що в них: "вітамін В7 (біотин)" → "вітамін В7"
        name_clean = re.sub(r'\s*\([^)]*\)', '', name).strip()
        
        # 2. Нормалізувати пробіли
        name_clean = " ".join(name_clean.split())
        
        # 3. Синонім: Вітамін B7 → Біотин
        name_clean_lower = name_clean.lower()
        if "b7" in name_clean_lower or "в7" in name_clean_lower or "біотин" in name_clean_lower:
            name_clean = "Біотин"
            logger.info(f"Synonym applied: '{name}' → 'Біотин'")
        
        # Якщо після очищення порожньо - використати оригінал
        if not name_clean:
            name_clean = name
        
        if name_clean != name:
            logger.info(f"Cleaned ingredient name: '{name}' → '{name_clean}'")
        
        # ПРІОРИТЕТ #1: Перевірити чи це excipient (використовуємо очищену назву)
        if await self._is_excipient(name_clean):
            # ФІНАЛЬНА ОЧИСТКА base_substance перед поверненням
            base_substance_clean = original_name.replace('\n', ' ').replace('  ', ' ').strip()
            result = {
                "base_substance": base_substance_clean,  # БЕЗ переносу рядків!
                "elemental_quantity": quantity,
                "type": "excipient",
                "source": "excipients_db",
                "original_quantity": quantity,
                "coefficient_used": 1.0,
                "unit": unit,
                "matched": True,
            }
            
            # Розпізнати чи це екстракт
            is_extract = False
            extract_type = None
            ratio = None
            
            # Перевірка keywords
            ingredient_name_lower = original_name.lower()
            for keyword in EXTRACT_KEYWORDS:
                if keyword in ingredient_name_lower:
                    is_extract = True
                    extract_type = keyword
                    logger.info(f"🌿 Extract detected: {original_name} (type: {keyword})")
                    break
            
            # Витягти ratio якщо є (10:1, 20:1, тощо)
            ratio_match = re.search(r'(\d+):(\d+)', original_name)
            if ratio_match:
                ratio = ratio_match.group(0)  # "10:1"
                logger.info(f"📊 Ratio detected: {ratio}")
            
            # Додати до результату
            result["is_extract"] = is_extract
            result["extract_type"] = extract_type
            result["ratio"] = ratio
            
            return result
        
        # Якщо немає кількості - повернути як є
        if quantity is None:
            # ФІНАЛЬНА ОЧИСТКА base_substance перед поверненням
            base_substance_clean = original_name.replace('\n', ' ').replace('  ', ' ').strip()
            result = {
                "base_substance": base_substance_clean,  # БЕЗ переносу рядків!
                "form": None,
                "original_quantity": None,
                "elemental_quantity": None,
                "coefficient_used": 1.0,
                "unit": unit,
                "matched": False,
            }

            # Розпізнати чи це екстракт
            is_extract = False
            extract_type = None
            ratio = None
            
            # Перевірка keywords
            ingredient_name_lower = original_name.lower()
            for keyword in EXTRACT_KEYWORDS:
                if keyword in ingredient_name_lower:
                    is_extract = True
                    extract_type = keyword
                    logger.info(f"🌿 Extract detected: {original_name} (type: {keyword})")
                    break
            
            # Витягти ratio якщо є (10:1, 20:1, тощо)
            ratio_match = re.search(r'(\d+):(\d+)', original_name)
            if ratio_match:
                ratio = ratio_match.group(0)  # "10:1"
                logger.info(f"📊 Ratio detected: {ratio}")
            
            # Додати до результату
            result["is_extract"] = is_extract
            result["extract_type"] = extract_type
            result["ratio"] = ratio
            
            return result

        # Використовуємо очищену назву для нормалізації та пошуку
        name_normalized = self._normalize_name(name_clean)
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

            # ФІНАЛЬНА ОЧИСТКА base_substance перед поверненням
            base_substance = form_data.get("substance_name_ua", original_name)
            base_substance = base_substance.replace('\n', ' ').replace('  ', ' ').strip() if base_substance else original_name
            
            # Якщо застосовано синонім B7 → Біотин, використати "Біотин" як base_substance
            if name_clean == "Біотин" and base_substance != "Біотин":
                # Спробувати знайти "Біотин" в БД
                biotin_normalized = self._normalize_name("Біотин")
                biotin_form_data = await self._find_form_in_db(biotin_normalized)
                original_substance_name = form_data.get("substance_name_ua", "N/A")
                if biotin_form_data:
                    base_substance = "Біотин"
                    logger.info(f"✅ Using 'Біотин' as base_substance instead of '{original_substance_name}'")
                else:
                    # Якщо "Біотин" не знайдено, але синонім застосовано, використати "Біотин"
                    base_substance = "Біотин"
                    logger.info(f"✅ Using 'Біотин' as base_substance (synonym applied)")

            result = {
                "base_substance": base_substance,  # БЕЗ переносу рядків!
                "form": form_data.get("form_name_ua"),
                "original_quantity": quantity,
                "elemental_quantity": elemental_qty,
                "coefficient_used": float(coefficient),
                "unit": unit,
                "matched": True,
            }

            # Розпізнати чи це екстракт
            is_extract = False
            extract_type = None
            ratio = None
            
            # Перевірка keywords
            ingredient_name_lower = original_name.lower()
            for keyword in EXTRACT_KEYWORDS:
                if keyword in ingredient_name_lower:
                    is_extract = True
                    extract_type = keyword
                    logger.info(f"🌿 Extract detected: {original_name} (type: {keyword})")
                    break
            
            # Витягти ratio якщо є (10:1, 20:1, тощо)
            ratio_match = re.search(r'(\d+):(\d+)', original_name)
            if ratio_match:
                ratio = ratio_match.group(0)  # "10:1"
                logger.info(f"📊 Ratio detected: {ratio}")
            
            # Додати до результату
            result["is_extract"] = is_extract
            result["extract_type"] = extract_type
            result["ratio"] = ratio
            
            return result

        # Форма НЕ знайдена в БД → спробувати знайти в рослинах
        plant_result = await self._find_plant_in_db(name_clean)
        if plant_result and plant_result.get("found"):
            # base_substance вже очищено в _find_plant_in_db
            result = {
                "base_substance": plant_result["base_substance"],
                "elemental_quantity": quantity,
                "type": "plant",
                "source": "allowed_plants",
                "original_quantity": quantity,
                "coefficient_used": 1.0,
                "unit": unit,
                "matched": True,
            }
            
            # Розпізнати чи це екстракт
            is_extract = False
            extract_type = None
            ratio = None
            
            # Перевірка keywords
            ingredient_name_lower = original_name.lower()
            for keyword in EXTRACT_KEYWORDS:
                if keyword in ingredient_name_lower:
                    is_extract = True
                    extract_type = keyword
                    logger.info(f"🌿 Extract detected: {original_name} (type: {keyword})")
                    break
            
            # Витягти ratio якщо є (10:1, 20:1, тощо)
            ratio_match = re.search(r'(\d+):(\d+)', original_name)
            if ratio_match:
                ratio = ratio_match.group(0)  # "10:1"
                logger.info(f"📊 Ratio detected: {ratio}")
            
            # Додати до результату
            result["is_extract"] = is_extract
            result["extract_type"] = extract_type
            result["ratio"] = ratio
            
            return result

        logger.warning(f"Form not found in DB: {original_name}")
        
        # ФІНАЛЬНА ОЧИСТКА base_substance перед поверненням
        base_substance_clean = original_name.replace('\n', ' ').replace('  ', ' ').strip()
        
        # Розпізнати чи це екстракт (ПЕРЕМІСТИТИ СЮДИ!)
        is_extract = False
        extract_type = None
        ratio = None
        
        # Перевірка keywords
        ingredient_name_lower = original_name.lower()
        for keyword in EXTRACT_KEYWORDS:
            if keyword in ingredient_name_lower:
                is_extract = True
                extract_type = keyword
                logger.info(f"🌿 Extract detected: {original_name} (type: {keyword})")
                break
        
        # Витягти ratio якщо є (10:1, 20:1, тощо)
        ratio_match = re.search(r'(\d+):(\d+)', original_name)
        if ratio_match:
            ratio = ratio_match.group(0)  # "10:1"
            logger.info(f"📊 Ratio detected: {ratio}")
        
        result = {
            "base_substance": base_substance_clean,  # БЕЗ переносу рядків!
            "form": None,
            "original_quantity": quantity,
            "elemental_quantity": quantity,
            "coefficient_used": 1.0,
            "unit": unit,
            "matched": False,
            "is_extract": is_extract,
            "extract_type": extract_type,
            "ratio": ratio,
        }
        
        return result

    async def _find_form_in_db(self, name_normalized: str) -> Optional[Dict]:
        """
        Search for form in substance_form_conversions table
        
        Шукає по:
        1. substance_name_ua (найточніше)
        2. substance_name_en
        3. name_variations (варіанти назв)

        Args:
            name_normalized: Normalized ingredient name (lowercase, В→B)

        Returns:
            Row from DB or None
        """
        try:
            # СПОСІБ 1: Прямий пошук по substance_name_ua (найшвидше)
            try:
                # Завантажити всі записи та перевірити нормалізовані назви
                # (бо ilike не завжди працює з нормалізованими назвами)
                result_ua = self.supabase.table("substance_form_conversions").select("*").execute()
                
                if result_ua.data:
                    for row in result_ua.data:
                        substance_ua = row.get("substance_name_ua", "")
                        substance_ua_normalized = self._normalize_name(substance_ua)
                        
                        # Точне співпадіння нормалізованих назв
                        if substance_ua_normalized == name_normalized:
                            logger.info(
                                f"✅ Form found by substance_name_ua: '{name_normalized}' → '{substance_ua}' ({row.get('form_name_ua')})"
                            )
                            return row
            except Exception as e:
                logger.debug(f"Search by substance_name_ua failed: {e}")
            
            # СПОСІБ 2: Пошук по substance_name_en
            try:
                result_en = self.supabase.table("substance_form_conversions").select("*").execute()
                
                if result_en.data:
                    for row in result_en.data:
                        substance_en = row.get("substance_name_en", "")
                        substance_en_normalized = self._normalize_name(substance_en)
                        
                        # Точне співпадіння нормалізованих назв
                        if substance_en_normalized == name_normalized:
                            logger.info(
                                f"✅ Form found by substance_name_en: '{name_normalized}' → '{substance_en}' ({row.get('form_name_ua')})"
                            )
                            return row
            except Exception as e:
                logger.debug(f"Search by substance_name_en failed: {e}")
            
            # СПОСІБ 3: Пошук в name_variations (fallback - повільніше)
            logger.debug(f"🔍 Searching in name_variations for: '{name_normalized}'")
            result = self.supabase.table("substance_form_conversions").select("*").execute()
            logger.debug(f"📊 Loaded {len(result.data or [])} forms from DB for variations search")

            for row in result.data or []:
                name_variations_raw = row.get("name_variations", [])
                
                # Визначити тип та парсити правильно
                if isinstance(name_variations_raw, str):
                    try:
                        variations = json.loads(name_variations_raw)  # parse JSON string
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse name_variations as JSON: {name_variations_raw}")
                        variations = []
                elif isinstance(name_variations_raw, list):
                    variations = name_variations_raw  # вже list
                else:
                    variations = []  # fallback
                
                for variation in variations or []:
                    variation_normalized = self._normalize_name(variation)
                    if variation_normalized == name_normalized:
                        logger.info(
                            f"✅ Form found by name_variations: '{name_normalized}' → '{row.get('substance_name_ua')}' ({row.get('form_name_ua')})"
                        )
                        return row
            
            logger.debug(f"⚠️ Form not found for normalized name: '{name_normalized}'")
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
            Normalized name (lowercase, trimmed, кирилиця В→B)
        """
        normalized = (name or "").lower().strip()
        
        # Критична заміна кирилиці на латиницю
        normalized = normalized.replace('в', 'b')
        normalized = normalized.replace('В', 'B')
        
        return normalized
    
    async def _is_excipient(self, ingredient_name: str) -> bool:
        """
        Перевірити чи інгредієнт є допоміжною речовиною (excipient)
        
        Args:
            ingredient_name: Назва інгредієнта
            
        Returns:
            True якщо знайдено в таблиці excipients, False інакше
        """
        try:
            ingredient_lower = ingredient_name.lower().strip()
            
            # Пряме співпадіння в excipient_name_ua або excipient_name_en
            result = self.supabase.table("excipients").select("id").or_(
                f"excipient_name_ua.ilike.%{ingredient_lower}%,excipient_name_en.ilike.%{ingredient_lower}%"
            ).execute()
            
            if result.data and len(result.data) > 0:
                return True
            
            # Якщо не знайдено - шукати в name_variations через SQL функцію
            try:
                rpc_result = self.supabase.rpc(
                    'search_excipient_variations',
                    {'search_term': ingredient_lower}
                ).execute()
                
                if rpc_result.data and len(rpc_result.data) > 0:
                    return True
            except Exception as rpc_exc:
                logger.debug(f"RPC search_excipient_variations failed: {rpc_exc}")
            
            return False
        except Exception as e:
            logger.debug(f"Error checking excipient {ingredient_name}: {e}")
            return False
    
    async def _find_plant_in_db(self, ingredient_name: str) -> Optional[Dict]:
        """
        Знайти рослину в таблиці allowed_plants
        
        Args:
            ingredient_name: Назва інгредієнта (наприклад: "екстракт півонії (10:1)")
            
        Returns:
            Dict з полями found, base_substance, coefficient_min, coefficient_max, source
            або None якщо не знайдено
        """
        try:
            # 1. Очистити назву від службових слів
            cleaned_name = ingredient_name.lower().strip()
            
            # Видалити слова: "екстракт", "порошок", "олія", "сік"
            service_words = ["екстракт", "порошок", "олія", "сік", "extract", "powder", "oil", "juice"]
            for word in service_words:
                cleaned_name = cleaned_name.replace(word, "").strip()
            
            # Видалити дужки та цифри: "(10:1)" → ""
            cleaned_name = re.sub(r'\([^)]*\)', '', cleaned_name).strip()
            cleaned_name = re.sub(r'\d+', '', cleaned_name).strip()
            
            # 2. Зробити stemming (відсікти закінчення)
            # Простий stemming: видалити останні 2 літери якщо слово довше 4 символів
            words = cleaned_name.split()
            stemmed_words = []
            for word in words:
                if len(word) > 4:
                    stemmed_word = word[:-2]  # Видалити останні 2 літери
                else:
                    stemmed_word = word
                stemmed_words.append(stemmed_word)
            
            plant_stem = " ".join(stemmed_words).strip()
            
            if not plant_stem:
                return None
            
            # 3. Пошук в БД через ILIKE
            result = self.supabase.table("allowed_plants").select("*").or_(
                f"botanical_family_ua.ilike.%{plant_stem}%,common_name_ua.ilike.%{plant_stem}%,botanical_name_lat.ilike.%{plant_stem}%"
            ).execute()
            
            if result.data and len(result.data) > 0:
                plant = result.data[0]
                
                # КРИТИЧНО: Прибрати перенос рядка з назви!
                plant_family = (plant.get('botanical_family_ua') or '').replace('\n', ' ').replace('  ', ' ').strip()
                plant_name = (plant.get('common_name_ua') or '').replace('\n', ' ').replace('  ', ' ').strip()
                base_substance = plant_family or plant_name
                
                logger.info(f"Found plant: {ingredient_name} -> {base_substance}")
                return {
                    "found": True,
                    "base_substance": base_substance,  # БЕЗ переносу!
                    "coefficient_min": 1.0,  # рослини не конвертуються
                    "coefficient_max": 1.0,
                    "source": "allowed_plants"
                }
            
            return None
        except Exception as e:
            logger.debug(f"Error finding plant {ingredient_name}: {e}")
            return None

