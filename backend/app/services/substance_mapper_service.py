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

# Стандартні форми вітамінів (форма, коефіцієнт)
STANDARD_VITAMIN_FORMS = {
    "Вітамін A": ("Ретинілу ацетат", 0.85),
    "Вітамін B1": ("Тіаміну гідрохлорид", 0.85),
    "Вітамін B2": ("Рибофлавін", 1.0),
    "Вітамін B3": ("Нікотинамід", 1.0),
    "Вітамін B5": ("D-пантотенат кальцію", 0.9),
    "Вітамін B6": ("Піридоксину гідрохлорид", 0.85),
    "Вітамін B7": ("D-біотин", 1.0),
    "Біотин": ("D-біотин", 1.0),
    "Вітамін B9": ("Фолієва кислота", 1.0),
    "Вітамін B12": ("Ціанокобаламін", 1.0),
    "Вітамін C": ("L-аскорбінова кислота", 1.0),
    "Вітамін D": ("Холекальциферол", 1.0),
    "Вітамін D3": ("Холекальциферол", 1.0),
    "Вітамін E": ("D-альфа-токоферол ацетат", 0.67),
    "Вітамін K": ("Філохінон", 1.0),
    "Вітамін K1": ("Філохінон", 1.0),
}

# Стандартні форми мінералів (форма, коефіцієнт)
STANDARD_MINERAL_FORMS = {
    "Магній": ("Цитрат магнію", 0.16),
    "Кальцій": ("Карбонат кальцію", 0.4),
    "Залізо": ("Фумарат заліза", 0.33),
    "Цинк": ("Цитрат цинку", 0.31),
    "Мідь": ("Глюконат міді", 0.14),
    "Селен": ("Селенометіонін", 0.4),
    "Йод": ("Йодид калію", 0.76),
    "Хром": ("Піколінат хрому", 0.12),
    "Марганець": ("Сульфат марганцю", 0.32),
    "Молібден": ("Молібдат натрію", 0.4),
}


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

        # Форма НЕ знайдена в БД → спробувати стандартну форму
        # Спочатку визначити base_substance (може бути name_clean після синонімів)
        potential_base_substance = name_clean
        
        # Спробувати знайти base_substance через стандартні форми
        default_form = self._get_default_form(potential_base_substance)
        
        if default_form:
            # Використати стандартну форму
            coefficient = default_form["coefficient"]
            elemental_qty = round(quantity * float(coefficient), 2)
            form_name = default_form["form"]
            
            # Знайти правильну назву base_substance зі словника (з великої літери)
            all_defaults = {**STANDARD_VITAMIN_FORMS, **STANDARD_MINERAL_FORMS}
            base_substance_key = potential_base_substance
            for key in all_defaults.keys():
                if key.lower() == potential_base_substance.lower():
                    base_substance_key = key
                    break
            
            # ФІНАЛЬНА ОЧИСТКА base_substance перед поверненням
            base_substance_clean = base_substance_key.replace('\n', ' ').replace('  ', ' ').strip()
            
            logger.info(f"✅ Applied default form: {potential_base_substance} → {base_substance_clean} → {form_name} (coef: {coefficient})")
            
            result = {
                "base_substance": base_substance_clean,
                "form": form_name,
                "original_quantity": quantity,
                "elemental_quantity": elemental_qty,
                "coefficient_used": float(coefficient),
                "unit": unit,
                "matched": True,
                "source": "default_form"
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

        # Спробувати знайти в рослинах (використовуємо очищену назву)
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

        Args:
            name_normalized: Normalized ingredient name

        Returns:
            Row from DB or None
        """
        try:
            result = self.supabase.table("substance_form_conversions").select("*").execute()

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
            Normalized name (lowercase, trimmed, кирилиця В→B)
        """
        normalized = (name or "").lower().strip()
        
        # Критична заміна кирилиці на латиницю
        normalized = normalized.replace('в', 'b')
        normalized = normalized.replace('В', 'B')
        
        return normalized
    
    def _get_default_form(self, base_substance: str) -> Optional[Dict]:
        """
        Припустити стандартну форму якщо не вказана на етикетці.
        
        Використовується коли:
        - На етикетці написано просто "магній" без форми
        - Або "вітамін B6" без форми
        
        Args:
            base_substance: Назва базової речовини (наприклад, "Магній", "Вітамін B6", "магній")
        
        Returns:
            Dict з формою та коефіцієнтом або None
        """
        # Об'єднані словники
        all_defaults = {**STANDARD_VITAMIN_FORMS, **STANDARD_MINERAL_FORMS}
        
        # Спробувати точне співпадіння
        if base_substance in all_defaults:
            form_name, coefficient = all_defaults[base_substance]
            logger.info(f"📌 Using default form: {base_substance} → {form_name} (coef: {coefficient})")
            return {
                "form": form_name,
                "coefficient": coefficient
            }
        
        # Спробувати case-insensitive пошук
        base_substance_lower = base_substance.lower()
        for key, value in all_defaults.items():
            if key.lower() == base_substance_lower:
                form_name, coefficient = value
                logger.info(f"📌 Using default form (case-insensitive): {base_substance} → {key} → {form_name} (coef: {coefficient})")
                return {
                    "form": form_name,
                    "coefficient": coefficient
                }
        
        return None
    
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

