"""Dosage validation service with 4-level hierarchy for vitamins/minerals"""

import logging
from typing import List, Dict, Optional, Tuple

from app.db.supabase_client import SupabaseClient
from app.services.substance_mapper_service import SubstanceMapperService
from app.api.schemas.validation import DosageCheckResult, DosageError, DosageWarning

logger = logging.getLogger(__name__)


class DosageService:
    """Service for validating ingredient dosages against regulatory limits with 4-level hierarchy"""
    
    def __init__(self):
        """Initialize dosage service with Supabase client"""
        self.supabase = SupabaseClient().client
        self.mapper = SubstanceMapperService()
        logger.info("DosageService initialized with SubstanceMapperService")
    
    async def check_dosages(self, ingredients: List[Dict]) -> DosageCheckResult:
        """
        Check dosages of all ingredients against regulatory limits.
        
        Implements 4-level hierarchy for vitamins/minerals:
        - Level 1: EFSA Upper Limit (UL)
        - Level 2: EFSA Safe Level
        - Level 3: Table 1 (max_doses_table1)
        - Level 4: Appendix 3, Section IV (physiological)
        
        Args:
            ingredients: List of ingredient dictionaries with structure:
                [
                    {
                        "name": "Вітамін С",
                        "quantity": 1000.0,
                        "unit": "мг",
                        "form": "аскорбінова кислота"
                    },
                    ...
                ]
        
        Returns:
            DosageCheckResult with errors, warnings, and validation status
        """
        logger.info(f"Checking dosages for {len(ingredients)} ingredients")
        
        errors = []
        warnings = []
        substances_not_found = 0
        
        for ingredient in ingredients:
            ingredient_name = ingredient.get("name", "Unknown")
            quantity = ingredient.get("quantity")
            unit = ingredient.get("unit", "мг")
            form = ingredient.get("form", "")
            
            logger.debug(f"Checking ingredient: {ingredient_name} ({quantity} {unit})")
            
            # PRIORITY #1: Check banned substances FIRST!
            if await self._is_banned_substance(ingredient_name):
                errors.append(DosageError(
                    ingredient=ingredient_name,
                    message="ЗАБОРОНЕНА РЕЧОВИНА! Використання суворо заборонено.",
                    level=0,  # Special level for banned substances
                    source="banned_substances",
                    current_dose=f"{quantity} {unit}" if quantity else None,
                    regulatory_source="Проєкт Змін до Наказу №1114, Додаток 3",
                    recommendation="ВИДАЛИТИ цю речовину з складу",
                    penalty_amount=640000
                ))
                logger.error(f"BANNED SUBSTANCE DETECTED: {ingredient_name}")
                continue  # Skip other checks
            
            # Determine substance type and call appropriate method
            result = None
            
            # Type 1: Vitamins/Minerals (4-level hierarchy)
            if await self._is_vitamin_mineral(ingredient_name):
                result = await self._check_vitamin_mineral(ingredient_name, quantity, unit, form)
            
            # Type 2: Amino acids (direct check in amino_acids table)
            elif await self._is_amino_acid(ingredient_name):
                result = await self._check_amino_acid(ingredient_name, quantity, unit, form)
            
            # Type 3: Plants (only allowed/forbidden check, NO dosage check)
            elif await self._is_plant(ingredient_name):
                result = await self._check_plant(ingredient_name, form)
            
            # Type 4: Microorganisms (only allowed/forbidden check, NO dosage check)
            elif await self._is_microorganism(ingredient_name):
                result = await self._check_microorganism(ingredient_name, form)
            
            # Type 5: Physiological substances (from max_doses_table1)
            elif await self._is_physiological(ingredient_name):
                result = await self._check_physiological(ingredient_name, quantity, unit, form)
            
            # Type 6: Novel Foods (future)
            elif await self._is_novel_food(ingredient_name):
                result = await self._check_novel_food(ingredient_name, quantity, unit, form)
            
            # Type 7: Unknown substance
            else:
                substances_not_found += 1
                warnings.append(DosageWarning(
                    ingredient=ingredient_name,
                    message="Речовина не знайдена в базі дозволених",
                    current_dose=f"{quantity} {unit}" if quantity else None,
                    recommendation=(
                        f"Переконайтесь що '{ingredient_name}' є дозволеною речовиною "
                        "згідно Наказу МОЗ №1114. Можливо назва вказана неправильно або "
                        "речовина не дозволена для використання в дієтичних добавках."
                    )
                ))
                logger.warning(f"Substance not found: {ingredient_name}")
                continue
            
            # Process result
            if result:
                if result.get("type") == "error":
                    errors.append(result["error"])
                    # Also add form warning if exists
                    if result.get("form_warning"):
                        warnings.append(result["form_warning"])
                elif result.get("type") == "warning":
                    warnings.append(result["warning"])
                elif result.get("type") == "ok":
                    # Valid dose, but check for form warning
                    if result.get("form_warning"):
                        warnings.append(result["form_warning"])
                # "ok" type means no errors/warnings (except form)
        
        # Determine if all dosages are valid
        all_valid = len(errors) == 0
        
        result = DosageCheckResult(
            errors=errors,
            warnings=warnings,
            all_valid=all_valid,
            total_ingredients_checked=len(ingredients),
            substances_not_found=substances_not_found
        )
        
        logger.info(
            f"Dosage check complete: {len(errors)} errors, "
            f"{len(warnings)} warnings, valid={all_valid}"
        )
        
        return result
    
    # ==================== TYPE CHECKING METHODS ====================
    
    async def _is_banned_substance(self, ingredient_name: str) -> bool:
        """Check if substance is in banned_substances table (PRIORITY!)"""
        try:
            result = self.supabase.table("banned_substances").select("id").or_(
                f"substance_name_ua.ilike.%{ingredient_name}%,substance_name_en.ilike.%{ingredient_name}%"
            ).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.debug(f"Error checking banned substance {ingredient_name}: {e}")
            return False
    
    async def _is_vitamin_mineral(self, ingredient_name: str) -> bool:
        """Check if substance is in allowed_vitamins_minerals"""
        try:
            result = self.supabase.table("allowed_vitamins_minerals").select("id").or_(
                f"substance_name_ua.eq.{ingredient_name},substance_name_en.eq.{ingredient_name}"
            ).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.debug(f"Error checking vitamin/mineral {ingredient_name}: {e}")
            return False
    
    async def _is_amino_acid(self, ingredient_name: str) -> bool:
        """Check if substance is in amino_acids"""
        try:
            result = self.supabase.table("amino_acids").select("id").or_(
                f"amino_acid_name_ua.eq.{ingredient_name},amino_acid_name_en.eq.{ingredient_name}"
            ).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.debug(f"Error checking amino acid {ingredient_name}: {e}")
            return False
    
    async def _is_plant(self, ingredient_name: str) -> bool:
        """Check if substance is in allowed_plants"""
        try:
            result = self.supabase.table("allowed_plants").select("id").or_(
                f"botanical_name_lat.ilike.%{ingredient_name}%,common_name_ua.ilike.%{ingredient_name}%"
            ).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.debug(f"Error checking plant {ingredient_name}: {e}")
            return False
    
    async def _is_microorganism(self, ingredient_name: str) -> bool:
        """Check if substance is in microorganisms"""
        try:
            # Split into genus and species if space exists
            parts = ingredient_name.split()
            if len(parts) >= 2:
                genus, species = parts[0], parts[1]
                result = self.supabase.table("microorganisms").select("id").eq(
                    "genus", genus
                ).eq("species", species).execute()
                return len(result.data) > 0
            return False
        except Exception as e:
            logger.debug(f"Error checking microorganism {ingredient_name}: {e}")
            return False
    
    async def _is_physiological(self, ingredient_name: str) -> bool:
        """Check if substance is in max_doses_table1 with category='physiological'"""
        try:
            result = self.supabase.table("max_doses_table1").select("id").or_(
                f"substance_name_ua.eq.{ingredient_name},substance_name_en.eq.{ingredient_name}"
            ).eq("category", "physiological").execute()
            return len(result.data) > 0
        except Exception as e:
            logger.debug(f"Error checking physiological {ingredient_name}: {e}")
            return False
    
    async def _is_novel_food(self, ingredient_name: str) -> bool:
        """Check if substance is in novel_foods"""
        try:
            result = self.supabase.table("novel_foods").select("id").or_(
                f"substance_name_ua.eq.{ingredient_name},substance_name_en.eq.{ingredient_name}"
            ).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.debug(f"Error checking novel food {ingredient_name}: {e}")
            return False
    
    # ==================== CHECKING METHODS FOR EACH TYPE ====================
    
    async def _check_vitamin_mineral(
        self,
        ingredient_name: str,
        quantity: Optional[float],
        unit: str,
        form: Optional[str],
    ) -> Optional[Dict]:
        """
        Check vitamin/mineral dosage with elemental conversion

        4-level hierarchy:
            Level 1: EFSA Upper Limit (UL)
            Level 2: EFSA Safe Level
            Level 3: Table 1 (max_doses_table1)
            Level 4: Warning if not found
        """
        parsed = await self.mapper.parse_ingredient(ingredient_name, quantity, unit)
        base_substance = parsed["base_substance"]
        elemental_quantity = parsed["elemental_quantity"]
        coefficient_used = parsed["coefficient_used"]

        logger.info(
            "Mapped ingredient '%s' (%s %s) -> %s (elemental: %s %s, coefficient: %s)",
            ingredient_name,
            quantity,
            unit,
            base_substance,
            elemental_quantity,
            unit,
            coefficient_used,
        )

        if elemental_quantity is None:
            return {
                "type": "warning",
                "warning": DosageWarning(
                    ingredient=base_substance,
                    message="Кількість речовини не вказана",
                    recommendation="Вкажіть кількість речовини для перевірки дози",
                ),
            }

        vitamin_mineral = await self._get_vitamin_mineral(base_substance)
        if not vitamin_mineral:
            return {
                "type": "warning",
                "warning": DosageWarning(
                    ingredient=base_substance,
                    message="Вітамін/мінерал не знайдений в allowed_vitamins_minerals",
                    recommendation="Перевірте правильність назви",
                ),
            }

        form_warning = self._check_form(
            form,
            vitamin_mineral.get("allowed_forms", []),
            base_substance,
        )

        display_dose = f"{elemental_quantity} {unit}"

        if vitamin_mineral.get("efsa_mapping"):
            efsa_data = await self._get_efsa_limits(vitamin_mineral["efsa_mapping"])

            if efsa_data:
                if efsa_data.get("ul_value") is not None:
                    converted_quantity = self._convert_to_base_unit(
                        elemental_quantity, unit, efsa_data["ul_unit"]
                    )

                    if converted_quantity > efsa_data["ul_value"]:
                        error = DosageError(
                            ingredient=base_substance,
                            message="Перевищує EFSA Upper Limit (UL)",
                            level=1,
                            source="efsa_ul",
                            current_dose=display_dose,
                            max_allowed=f"{efsa_data['ul_value']} {efsa_data['ul_unit']}",
                            regulatory_source="EFSA 2024",
                            recommendation=(
                                f"Зменшіть дозування до {efsa_data['ul_value']} {efsa_data['ul_unit']} "
                                "або нижче. Поточна доза перевищує допустимий верхній рівень споживання (UL)."
                            ),
                            penalty_amount=640000,
                        )
                        result = {"type": "error", "error": error}
                        if form_warning:
                            result["form_warning"] = form_warning
                        return result
                    else:
                        result = {"type": "ok"}
                        if form_warning:
                            result["form_warning"] = form_warning
                        return result

                if efsa_data.get("safe_level_value") is not None:
                    converted_quantity = self._convert_to_base_unit(
                        elemental_quantity, unit, efsa_data["safe_level_unit"]
                    )

                    if converted_quantity > efsa_data["safe_level_value"]:
                        error = DosageError(
                            ingredient=base_substance,
                            message="Перевищує EFSA Safe Level",
                            level=2,
                            source="efsa_safe",
                            current_dose=display_dose,
                            max_allowed=f"{efsa_data['safe_level_value']} {efsa_data['safe_level_unit']}",
                            regulatory_source="EFSA 2024",
                            recommendation=(
                                f"Зменшіть дозування до {efsa_data['safe_level_value']} "
                                f"{efsa_data['safe_level_unit']} або нижче. Поточна доза перевищує безпечний рівень."
                            ),
                            penalty_amount=640000,
                        )
                        result = {"type": "error", "error": error}
                        if form_warning:
                            result["form_warning"] = form_warning
                        return result
                    else:
                        result = {"type": "ok"}
                        if form_warning:
                            result["form_warning"] = form_warning
                        return result

        table1_dose = await self._get_max_dose_table1(
            base_substance,
            ["vitamin", "mineral"],
        )

        if table1_dose and table1_dose.get("max_dose_value") is not None:
            converted_quantity = self._convert_to_base_unit(
                elemental_quantity, unit, table1_dose["max_dose_unit"]
            )

            if converted_quantity > table1_dose["max_dose_value"]:
                error = DosageError(
                    ingredient=base_substance,
                    message="Перевищує максимальну дозу Таблиці 1",
                    level=3,
                    source="table1",
                    current_dose=display_dose,
                    max_allowed=f"{table1_dose['max_dose_value']} {table1_dose['max_dose_unit']}",
                    regulatory_source="Проєкт Змін до Наказу №1114, Додаток 1, Таблиця 1",
                    recommendation=(
                        f"Зменшіть дозування до {table1_dose['max_dose_value']} "
                        f"{table1_dose['max_dose_unit']} або нижче."
                    ),
                    penalty_amount=640000,
                )
                result = {"type": "error", "error": error}
                if form_warning:
                    result["form_warning"] = form_warning
                return result
            else:
                result = {"type": "ok"}
                if form_warning:
                    result["form_warning"] = form_warning
                return result

        warning = DosageWarning(
            ingredient=base_substance,
            message="Доза не встановлена в EFSA та Таблиці 1",
            level=4,
            source="unknown",
            current_dose=display_dose,
            recommendation=(
                "Доза не знайдена в жодному з рівнів ієрархії. "
                "Перевірте чи речовина правильно вказана та чи встановлена для неї доза."
            ),
        )

        result = {"type": "warning", "warning": warning}
        if form_warning:
            result["form_warning"] = form_warning
        return result
    
    async def _check_amino_acid(
        self, 
        ingredient_name: str, 
        quantity: float, 
        unit: str,
        form: str
    ) -> Optional[Dict]:
        """
        Check amino acid dosage
        
        IMPORTANT: max_daily_dose is ALREADY in amino_acids table!
        No need to search in max_doses_table1
        """
        # Check if quantity is provided
        if quantity is None:
            return {
                "type": "warning",
                "warning": DosageWarning(
                    ingredient=ingredient_name,
                    message="Кількість речовини не вказана",
                    recommendation="Вкажіть кількість речовини для перевірки дози"
                )
            }
        
        try:
            result = self.supabase.table("amino_acids").select("*").or_(
                f"amino_acid_name_ua.eq.{ingredient_name},amino_acid_name_en.eq.{ingredient_name}"
            ).execute()
            
            if not result.data or len(result.data) == 0:
                return {
                    "type": "warning",
                    "warning": DosageWarning(
                        ingredient=ingredient_name,
                        message="Амінокислота не знайдена",
                        recommendation="Перевірте правильність назви"
                    )
                }
            
            # Take first match
            amino_acid = result.data[0]
            
            # Log if multiple matches
            if len(result.data) > 1:
                logger.warning(f"Multiple matches for amino acid '{ingredient_name}': {len(result.data)}")
            
            # Dose is already in table!
            max_dose = amino_acid.get("max_daily_dose")
            dose_unit = amino_acid.get("unit", "г/день")
            
            if max_dose is None:
                return {
                    "type": "warning",
                    "warning": DosageWarning(
                        ingredient=ingredient_name,
                        message="Доза не встановлена для амінокислоти",
                        level=3,
                        source="amino_acids_table",
                        recommendation="Перевірте чи доза встановлена в базі даних"
                    )
                }
            
            # Convert units (handle "г/день" format)
            if "/" in dose_unit:
                dose_unit = dose_unit.split("/")[0].strip()
            
            converted_quantity = self._convert_to_base_unit(quantity, unit, dose_unit)
            
            if converted_quantity > max_dose:
                return {
                    "type": "error",
                    "error": DosageError(
                        ingredient=ingredient_name,
                        message="Перевищує максимальну дозу для амінокислоти",
                        level=3,
                        source="amino_acids_table",
                        current_dose=f"{quantity} {unit}",
                        max_allowed=f"{max_dose} {dose_unit}",
                        regulatory_source="Проєкт Змін до Наказу №1114, Додаток 3, Розділ III",
                        recommendation=(
                            f"Зменшіть дозування до {max_dose} {dose_unit} або нижче."
                        ),
                        penalty_amount=640000
                    )
                }
            else:
                return {"type": "ok"}
                
        except Exception as e:
            logger.error(f"Error checking amino acid {ingredient_name}: {e}")
            return {
                "type": "warning",
                "warning": DosageWarning(
                    ingredient=ingredient_name,
                    message=f"Помилка при перевірці амінокислоти: {str(e)}",
                    recommendation="Перевірте правильність даних"
                )
            }
    
    async def _check_plant(self, ingredient_name: str, form: str) -> Optional[Dict]:
        """
        Check plant
        
        IMPORTANT: ONLY allowed/forbidden check
        DOSAGE IS NOT CHECKED
        """
        try:
            result = self.supabase.table("allowed_plants").select("*").or_(
                f"botanical_name_lat.ilike.%{ingredient_name}%,common_name_ua.ilike.%{ingredient_name}%"
            ).execute()
            
            if result.data and len(result.data) > 0:
                return {
                    "type": "ok",
                    "message": "Рослина дозволена, доза не обмежена"
                }
            else:
                return {
                    "type": "warning",
                    "warning": DosageWarning(
                        ingredient=ingredient_name,
                        message="Рослина не знайдена в списку дозволених",
                        level=3,
                        source="allowed_plants",
                        recommendation=(
                            "Переконайтесь що рослина дозволена згідно "
                            "Додатку 3, Розділ I Проєкту Змін до Наказу №1114"
                        )
                    )
                }
        except Exception as e:
            logger.error(f"Error checking plant {ingredient_name}: {e}")
            return {
                "type": "warning",
                "warning": DosageWarning(
                    ingredient=ingredient_name,
                    message=f"Помилка при перевірці рослини: {str(e)}",
                    recommendation="Перевірте правильність даних"
                )
            }
    
    async def _check_microorganism(self, ingredient_name: str, form: str) -> Optional[Dict]:
        """
        Check microorganism
        
        IMPORTANT: ONLY allowed/forbidden check
        DOSAGE IS NOT CHECKED (CFU not regulated)
        """
        try:
            # Split into genus and species
            parts = ingredient_name.split()
            if len(parts) < 2:
                return {
                    "type": "warning",
                    "warning": DosageWarning(
                        ingredient=ingredient_name,
                        message="Некоректна назва мікроорганізму (потрібно Genus Species)",
                        recommendation="Вкажіть повну назву мікроорганізму (наприклад, 'Lactobacillus Acidophilus')"
                    )
                }
            
            genus, species = parts[0], parts[1]
            
            result = self.supabase.table("microorganisms").select("*").eq(
                "genus", genus
            ).eq("species", species).execute()
            
            if result.data and len(result.data) > 0:
                return {
                    "type": "ok",
                    "message": "Мікроорганізм дозволений"
                }
            else:
                return {
                    "type": "warning",
                    "warning": DosageWarning(
                        ingredient=ingredient_name,
                        message="Мікроорганізм не знайдений в списку дозволених",
                        level=3,
                        source="microorganisms",
                        recommendation=(
                            "Переконайтесь що мікроорганізм дозволений згідно "
                            "Додатку 3, Розділ V Проєкту Змін до Наказу №1114"
                        )
                    )
                }
        except Exception as e:
            logger.error(f"Error checking microorganism {ingredient_name}: {e}")
            return {
                "type": "warning",
                "warning": DosageWarning(
                    ingredient=ingredient_name,
                    message=f"Помилка при перевірці мікроорганізму: {str(e)}",
                    recommendation="Перевірте правильність даних"
                )
            }
    
    async def _check_physiological(
        self, 
        ingredient_name: str, 
        quantity: float, 
        unit: str,
        form: str
    ) -> Optional[Dict]:
        """
        Check physiological substance
        
        Source: max_doses_table1 WHERE category='physiological'
        """
        # Check if quantity is provided
        if quantity is None:
            return {
                "type": "warning",
                "warning": DosageWarning(
                    ingredient=ingredient_name,
                    message="Кількість речовини не вказана",
                    recommendation="Вкажіть кількість речовини для перевірки дози"
                )
            }
        
        try:
            result = self.supabase.table("max_doses_table1").select("*").or_(
                f"substance_name_ua.eq.{ingredient_name},substance_name_en.eq.{ingredient_name}"
            ).eq("category", "physiological").execute()
            
            if not result.data or len(result.data) == 0:
                return {
                    "type": "warning",
                    "warning": DosageWarning(
                        ingredient=ingredient_name,
                        message="Речовина не знайдена в max_doses_table1",
                        recommendation="Перевірте правильність назви"
                    )
                }
            
            # Take first match
            physiological = result.data[0]
            
            # Log if multiple matches
            if len(result.data) > 1:
                logger.warning(f"Multiple matches for physiological substance '{ingredient_name}': {len(result.data)}")
            max_dose = physiological.get("max_dose_value")
            dose_unit = physiological.get("max_dose_unit")
            
            # If dose = NULL
            if max_dose is None:
                return {
                    "type": "warning",
                    "warning": DosageWarning(
                        ingredient=ingredient_name,
                        message="Доза не встановлена, але речовина дозволена",
                        level=4,
                        source="physiological_no_limit",
                        current_dose=f"{quantity} {unit}" if quantity else None,
                        recommendation=(
                            "Речовина дозволена, але максимальна доза не встановлена. "
                            "Рекомендується консультація з регуляторними органами."
                        )
                    )
                }
            
            # Check dose
            converted_quantity = self._convert_to_base_unit(quantity, unit, dose_unit)
            
            if converted_quantity > max_dose:
                return {
                    "type": "error",
                    "error": DosageError(
                        ingredient=ingredient_name,
                        message="Перевищує максимальну дозу",
                        level=4,
                        source="physiological_table",
                        current_dose=f"{quantity} {unit}",
                        max_allowed=f"{max_dose} {dose_unit}",
                        regulatory_source="Проєкт Змін до Наказу №1114, Додаток 3, Розділ IV",
                        recommendation=(
                            f"Зменшіть дозування до {max_dose} {dose_unit} або нижче."
                        ),
                        penalty_amount=640000
                    )
                }
            else:
                return {"type": "ok"}
                
        except Exception as e:
            logger.error(f"Error checking physiological {ingredient_name}: {e}")
            return {
                "type": "warning",
                "warning": DosageWarning(
                    ingredient=ingredient_name,
                    message=f"Помилка при перевірці речовини: {str(e)}",
                    recommendation="Перевірте правильність даних"
                )
            }
    
    async def _check_novel_food(
        self, 
        ingredient_name: str, 
        quantity: float, 
        unit: str,
        form: str
    ) -> Optional[Dict]:
        """
        Check Novel Food
        
        IMPORTANT: Table is currently empty, will be filled later
        """
        # Check if quantity is provided
        if quantity is None:
            return {
                "type": "warning",
                "warning": DosageWarning(
                    ingredient=ingredient_name,
                    message="Кількість речовини не вказана",
                    recommendation="Вкажіть кількість речовини для перевірки дози"
                )
            }
        
        try:
            result = self.supabase.table("novel_foods").select("*").or_(
                f"substance_name_ua.eq.{ingredient_name},substance_name_en.eq.{ingredient_name}"
            ).eq("status", "active").execute()
            
            if not result.data or len(result.data) == 0:
                return {
                    "type": "warning",
                    "warning": DosageWarning(
                        ingredient=ingredient_name,
                        message="Novel Food не знайдено (таблиця поки порожня)",
                        level=4,
                        source="novel_foods",
                        recommendation="Таблиця novel_foods буде заповнена пізніше"
                    )
                }
            
            # Take first match
            novel_food = result.data[0]
            
            # Log if multiple matches
            if len(result.data) > 1:
                logger.warning(f"Multiple matches for novel food '{ingredient_name}': {len(result.data)}")
            max_dose = novel_food.get("max_daily_dose")
            dose_unit = novel_food.get("unit")
            
            if max_dose:
                converted_quantity = self._convert_to_base_unit(quantity, unit, dose_unit)
                
                if converted_quantity > max_dose:
                    return {
                        "type": "error",
                        "error": DosageError(
                            ingredient=ingredient_name,
                            message="Перевищує максимальну дозу для Novel Food",
                            level=4,
                            source="novel_foods",
                            current_dose=f"{quantity} {unit}",
                            max_allowed=f"{max_dose} {dose_unit}",
                            regulatory_source="Проєкт Змін до Наказу №1114",
                            recommendation=(
                                f"Зменшіть дозування до {max_dose} {dose_unit} або нижче."
                            ),
                            penalty_amount=640000
                        )
                    }
            
            return {"type": "ok"}
                
        except Exception as e:
            logger.debug(f"Novel food not found or error: {e}")
            return {
                "type": "warning",
                "warning": DosageWarning(
                    ingredient=ingredient_name,
                    message="Novel Food не знайдено (таблиця поки порожня)",
                    level=4,
                    source="novel_foods",
                    recommendation="Таблиця novel_foods буде заповнена пізніше"
                )
            }
    
    # ==================== HELPER METHODS ====================
    
    async def _get_vitamin_mineral(self, ingredient_name: str) -> Optional[Dict]:
        """Get vitamin/mineral from allowed_vitamins_minerals"""
        try:
            result = self.supabase.table("allowed_vitamins_minerals").select("*").or_(
                f"substance_name_ua.eq.{ingredient_name},substance_name_en.eq.{ingredient_name}"
            ).execute()
            
            if not result.data or len(result.data) == 0:
                return None
            
            # Take first match
            data = result.data[0]
            
            # Log if multiple matches
            if len(result.data) > 1:
                logger.warning(f"Multiple matches for vitamin/mineral '{ingredient_name}': {len(result.data)}")
            
            return data
        except Exception as e:
            logger.debug(f"Vitamin/mineral not found: {ingredient_name}")
            return None
    
    async def _get_efsa_limits(self, efsa_mapping: str) -> Optional[Dict]:
        """Get EFSA limits (UL and Safe Level)"""
        try:
            result = self.supabase.table("efsa_limits").select(
                "ul_value, ul_unit, safe_level_value, safe_level_unit, notes"
            ).eq("substance_name_en", efsa_mapping).execute()
            
            if not result.data or len(result.data) == 0:
                return None
            
            # Take first match
            data = result.data[0]
            
            # Log if multiple matches
            if len(result.data) > 1:
                logger.warning(f"Multiple matches for EFSA limits '{efsa_mapping}': {len(result.data)}")
            
            return data
        except Exception as e:
            logger.debug(f"EFSA limits not found for {efsa_mapping}: {e}")
            return None
    
    async def _get_max_dose_table1(
        self, 
        ingredient_name: str, 
        categories: List[str]
    ) -> Optional[Dict]:
        """Get dose from Table 1 (max_doses_table1)"""
        try:
            result = self.supabase.table("max_doses_table1").select(
                "max_dose_value, max_dose_unit, category, notes"
            ).or_(
                f"substance_name_ua.eq.{ingredient_name},substance_name_en.eq.{ingredient_name}"
            ).in_("category", categories).execute()
            
            if not result.data or len(result.data) == 0:
                return None
            
            # Take first match
            data = result.data[0]
            
            # Log if multiple matches
            if len(result.data) > 1:
                logger.warning(f"Multiple matches for max_dose_table1 '{ingredient_name}': {len(result.data)}")
            
            return data
        except Exception as e:
            logger.debug(f"Max dose not found in table1 for {ingredient_name}: {e}")
            return None
    
    def _check_form(
        self, 
        form: str, 
        allowed_forms: List[str], 
        ingredient_name: str
    ) -> Optional[DosageWarning]:
        """
        Check form of substance
        
        IMPORTANT: Does NOT block, only warns
        """
        if not form:
            return DosageWarning(
                ingredient=ingredient_name,
                message="Форма речовини не вказана",
                recommendation=(
                    f"Рекомендується вказати форму з дозволених: {', '.join(allowed_forms)}"
                    if allowed_forms else "Перевірте чи форма потрібна для цієї речовини"
                )
            )
        
        form_lower = form.lower().strip()
        
        # Exact match
        for allowed_form in allowed_forms:
            if form_lower == allowed_form.lower().strip():
                return None  # Form is correct
        
        # Form not found - warning
        return DosageWarning(
            ingredient=ingredient_name,
            message=f"Вказана форма '{form}' не знайдена в списку дозволених",
            current_dose=None,
            recommendation=(
                f"Перевірте чи форма правильна. Дозволені: {', '.join(allowed_forms)}"
                if allowed_forms else "Перевірте правильність форми"
            )
        )
    
    def _convert_to_base_unit(
        self, 
        quantity: float, 
        from_unit: str, 
        to_unit: str
    ) -> float:
        """
        Convert quantity from one unit to another
        
        Args:
            quantity: Amount
            from_unit: Source unit (e.g., "г")
            to_unit: Target unit (e.g., "мг")
        
        Returns:
            Converted quantity
        
        Examples:
            >>> convert(1, "г", "мг")
            1000.0
            >>> convert(500, "мкг", "мг")
            0.5
        """
        # Normalize unit names
        from_unit_norm = self._normalize_unit(from_unit)
        to_unit_norm = self._normalize_unit(to_unit)
        
        if from_unit_norm == to_unit_norm:
            return quantity
        
        # Conversion through base unit (mg)
        conversion_to_mg = {
            "мг": 1.0,
            "мкг": 0.001,
            "г": 1000.0,
            "кг": 1000000.0,
            "μg_re": 0.001,  # for Vitamin A
            "μg_vde": 0.001,  # for Vitamin D
        }
        
        # Convert to mg
        quantity_in_mg = quantity * conversion_to_mg.get(from_unit_norm, 1.0)
        
        # Convert from mg to target unit
        to_mg_factor = conversion_to_mg.get(to_unit_norm, 1.0)
        
        return quantity_in_mg / to_mg_factor
    
    def _normalize_unit(self, unit: str) -> str:
        """Normalize unit name"""
        unit_lower = unit.lower().strip()
        
        # Remove "/день" or "/day" suffixes
        if "/" in unit_lower:
            unit_lower = unit_lower.split("/")[0].strip()
        
        mapping = {
            "mg": "мг",
            "мг": "мг",
            "g": "г",
            "г": "г",
            "mcg": "мкг",
            "μg": "мкг",
            "мкг": "мкг",
            "kg": "кг",
            "кг": "кг",
            "μg re": "μg_re",
            "μg vde": "μg_vde",
            "мо": "мо",  # International Units
            "iu": "мо",
            "куо": "куо",  # Colony Forming Units
            "cfu": "куо",
        }
        
        return mapping.get(unit_lower, unit_lower)
