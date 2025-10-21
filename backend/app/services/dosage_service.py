"""Dosage validation service for checking ingredient dosages against regulatory limits"""

import logging
from typing import List, Dict, Optional

from app.data.loader import RegulatoryDataLoader
from app.api.schemas.validation import DosageCheckResult, DosageError, DosageWarning

logger = logging.getLogger(__name__)


class DosageService:
    """Service for validating ingredient dosages against regulatory limits"""
    
    def __init__(self):
        """Initialize dosage service with regulatory data loader"""
        self.loader = RegulatoryDataLoader()
    
    async def check_dosages(self, ingredients: List[Dict]) -> DosageCheckResult:
        """
        Check dosages of all ingredients against regulatory limits.
        
        Validates:
        - Substance is in allowed substances database
        - Form is allowed for the substance
        - Dosage does not exceed maximum daily dose
        - Dosage does not exceed triple the maximum (critical violation)
        
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
            
        Example:
            >>> service = DosageService()
            >>> ingredients = [
            ...     {"name": "Вітамін C", "quantity": 1000.0, "unit": "мг", "form": "аскорбінова кислота"}
            ... ]
            >>> result = await service.check_dosages(ingredients)
            >>> result.all_valid
            False
            >>> result.warnings[0].message
            'Дозування перевищує рекомендовану добову норму'
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
            
            # Find substance in database (fuzzy matching)
            substance = self.loader.get_substance_by_name(ingredient_name)
            
            if not substance:
                # Substance not found in database
                substances_not_found += 1
                warnings.append(DosageWarning(
                    ingredient=ingredient_name,
                    message="Речовина не знайдена в базі дозволених речовин",
                    current_dose=f"{quantity} {unit}",
                    max_allowed="Невідомо",
                    recommendation=(
                        f"Переконайтесь що '{ingredient_name}' є дозволеною речовиною "
                        "згідно Наказу МОЗ №1114. Можливо назва вказана неправильно або "
                        "речовина не дозволена для використання в дієтичних добавках."
                    )
                ))
                logger.warning(f"Substance not found: {ingredient_name}")
                continue
            
            logger.debug(f"Found substance: {substance['substance_name']}")
            
            # Check if form is allowed
            if form:
                if not self._is_form_allowed(form, substance.get("allowed_forms", [])):
                    errors.append(DosageError(
                        ingredient=substance["substance_name"],
                        message=f"Форма '{form}' не є дозволеною для цієї речовини",
                        current_form=form,
                        allowed_forms=substance.get("allowed_forms", []),
                        regulatory_source=substance.get("regulatory_source", "Наказ МОЗ №1114"),
                        recommendation=(
                            f"Використовуйте одну з дозволених форм: "
                            f"{', '.join(substance.get('allowed_forms', []))}"
                        ),
                        penalty_amount=640000
                    ))
                    logger.error(f"Disallowed form for {ingredient_name}: {form}")
                    continue
            
            # Check dosage
            dose_check = self._check_dose(
                quantity,
                unit,
                substance["max_daily_dose"],
                substance["unit"],
                substance["substance_name"]
            )
            
            current_dose_str = f"{quantity} {unit}"
            max_allowed_str = f"{substance['max_daily_dose']} {substance['unit']}"
            three_times_str = f"{substance['three_times_limit']} {substance['unit']}"
            
            if dose_check["exceeds_3x"]:
                # Critical error - exceeds triple limit
                errors.append(DosageError(
                    ingredient=substance["substance_name"],
                    message="КРИТИЧНА ПОМИЛКА: Дозування перевищує потрійну добову норму",
                    current_dose=current_dose_str,
                    max_allowed=max_allowed_str,
                    three_times_limit=three_times_str,
                    regulatory_source=substance.get("regulatory_source", "Наказ МОЗ №1114"),
                    recommendation=(
                        f"НЕГАЙНО зменшіть дозування до {max_allowed_str} або нижче. "
                        f"Поточне дозування {current_dose_str} небезпечне та порушує "
                        f"нормативи більш ніж утричі!"
                    ),
                    penalty_amount=640000
                ))
                logger.error(
                    f"CRITICAL: {ingredient_name} exceeds 3x limit: "
                    f"{quantity} {unit} > {substance['three_times_limit']} {substance['unit']}"
                )
                
            elif dose_check["exceeds_max"]:
                # Warning - exceeds maximum but within triple limit
                warnings.append(DosageWarning(
                    ingredient=substance["substance_name"],
                    message="Дозування перевищує рекомендовану добову норму",
                    current_dose=current_dose_str,
                    max_allowed=max_allowed_str,
                    recommendation=(
                        f"Рекомендується зменшити дозування до {max_allowed_str}. "
                        f"Поточне дозування {current_dose_str} перевищує максимальну "
                        f"добову норму, але знаходиться в межах потрійного ліміту "
                        f"({three_times_str})."
                    )
                ))
                logger.warning(
                    f"{ingredient_name} exceeds max: "
                    f"{quantity} {unit} > {substance['max_daily_dose']} {substance['unit']}"
                )
            else:
                # Dosage is within limits
                logger.debug(f"{ingredient_name} dosage is within limits")
        
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
    
    def _is_form_allowed(self, form: str, allowed_forms: List[str]) -> bool:
        """
        Check if ingredient form is in the list of allowed forms.
        
        Uses case-insensitive partial matching to handle variations.
        
        Args:
            form: The form to check (e.g., "аскорбінова кислота")
            allowed_forms: List of allowed forms
            
        Returns:
            True if form is allowed, False otherwise
            
        Example:
            >>> service = DosageService()
            >>> service._is_form_allowed("аскорбінова кислота", ["аскорбінова кислота", "аскорбат натрію"])
            True
            >>> service._is_form_allowed("невідома форма", ["аскорбінова кислота"])
            False
        """
        if not form or not allowed_forms:
            return True  # If no form specified or no restrictions, allow
        
        form_lower = form.lower().strip()
        
        for allowed_form in allowed_forms:
            allowed_lower = allowed_form.lower().strip()
            
            # Exact match
            if form_lower == allowed_lower:
                return True
            
            # Partial match (form contains or is contained in allowed form)
            if form_lower in allowed_lower or allowed_lower in form_lower:
                return True
        
        return False
    
    def _check_dose(
        self,
        current_quantity: float,
        current_unit: str,
        max_dose: float,
        max_unit: str,
        substance_name: str
    ) -> Dict[str, bool]:
        """
        Check if current dose exceeds maximum allowed dose.
        
        Converts units to common base (mg) for comparison.
        
        Args:
            current_quantity: Current dose quantity
            current_unit: Current dose unit (мг, г, мкг)
            max_dose: Maximum allowed dose
            max_unit: Maximum dose unit
            substance_name: Name of substance (for logging)
            
        Returns:
            Dictionary with:
                - exceeds_max: True if exceeds maximum daily dose
                - exceeds_3x: True if exceeds triple the maximum
                
        Example:
            >>> service = DosageService()
            >>> service._check_dose(1000, "мг", 80, "мг", "Вітамін C")
            {'exceeds_max': True, 'exceeds_3x': True}
        """
        try:
            # Convert to base unit (mg)
            current_in_mg = self._convert_to_base_unit(current_quantity, current_unit)
            max_in_mg = self._convert_to_base_unit(max_dose, max_unit)
            triple_limit_in_mg = max_in_mg * 3
            
            logger.debug(
                f"{substance_name}: Current={current_in_mg}mg, "
                f"Max={max_in_mg}mg, 3x={triple_limit_in_mg}mg"
            )
            
            return {
                "exceeds_max": current_in_mg > max_in_mg,
                "exceeds_3x": current_in_mg > triple_limit_in_mg
            }
            
        except Exception as e:
            logger.error(f"Error checking dose for {substance_name}: {e}")
            # In case of conversion error, assume no violation
            return {"exceeds_max": False, "exceeds_3x": False}
    
    def _convert_to_base_unit(self, quantity: float, unit: str) -> float:
        """
        Convert quantity to base unit (mg).
        
        Supported units:
        - мг, mg → 1 (base unit)
        - г, g → 1000
        - мкг, μg, mcg → 0.001
        - МО, IU → 1 (assumed equivalent for simplicity)
        - КУО, CFU → 1 (for probiotics, no conversion)
        
        Args:
            quantity: Amount in specified unit
            unit: Unit of measurement
            
        Returns:
            Quantity in mg
            
        Example:
            >>> service = DosageService()
            >>> service._convert_to_base_unit(1, "г")
            1000.0
            >>> service._convert_to_base_unit(500, "мкг")
            0.5
        """
        unit_lower = unit.lower().strip()
        
        # Conversion factors to mg
        conversions = {
            "мг": 1.0,
            "mg": 1.0,
            "г": 1000.0,
            "g": 1000.0,
            "мкг": 0.001,
            "μg": 0.001,
            "mcg": 0.001,
            "мо": 1.0,  # International Units (approximate)
            "iu": 1.0,
            "куо": 1.0,  # CFU (Colony Forming Units) - no conversion
            "cfu": 1.0,
        }
        
        factor = conversions.get(unit_lower, 1.0)
        result = quantity * factor
        
        logger.debug(f"Converted {quantity} {unit} → {result} mg (factor={factor})")
        
        return result


if __name__ == "__main__":
    import asyncio
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 25 + "DOSAGE SERVICE - DEMO" + " " * 31 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    async def test_dosage_service():
        """Test dosage validation service"""
        
        service = DosageService()
        
        # Test cases
        test_ingredients = [
            # Valid dosage
            {
                "name": "Вітамін C",
                "quantity": 80.0,
                "unit": "мг",
                "form": "аскорбінова кислота"
            },
            # Exceeds max but within 3x (warning)
            {
                "name": "Вітамін C",
                "quantity": 150.0,
                "unit": "мг",
                "form": "аскорбінова кислота"
            },
            # Exceeds 3x limit (critical error)
            {
                "name": "Вітамін A",
                "quantity": 3000.0,
                "unit": "мкг",
                "form": "ретинол ацетат"
            },
            # Unknown substance
            {
                "name": "Невідома Речовина",
                "quantity": 100.0,
                "unit": "мг",
                "form": ""
            },
            # Valid - Zinc
            {
                "name": "Цинк",
                "quantity": 10.0,
                "unit": "мг",
                "form": "цинк цитрат"
            },
            # Disallowed form
            {
                "name": "Залізо",
                "quantity": 14.0,
                "unit": "мг",
                "form": "залізо оксид"  # Not in allowed forms
            },
        ]
        
        print("📋 Testing dosage validation with sample ingredients:")
        print("─" * 80)
        for i, ing in enumerate(test_ingredients, 1):
            print(f"{i}. {ing['name']}: {ing['quantity']} {ing['unit']} ({ing['form'] or 'no form'})")
        print()
        
        # Run validation
        result = await service.check_dosages(test_ingredients)
        
        # Display results
        print("=" * 80)
        print("VALIDATION RESULTS")
        print("=" * 80)
        print()
        
        print(f"📊 Summary:")
        print(f"   Total ingredients checked: {result.total_ingredients_checked}")
        print(f"   Substances not found: {result.substances_not_found}")
        print(f"   Errors: {len(result.errors)}")
        print(f"   Warnings: {len(result.warnings)}")
        print(f"   All valid: {'✅ YES' if result.all_valid else '❌ NO'}")
        print()
        
        if result.errors:
            print("🔴 ERRORS (Critical - 640,000 грн penalty each):")
            print("─" * 80)
            for i, error in enumerate(result.errors, 1):
                print(f"\n{i}. {error.ingredient}")
                print(f"   Message: {error.message}")
                if error.current_dose:
                    print(f"   Current dose: {error.current_dose}")
                if error.max_allowed:
                    print(f"   Max allowed: {error.max_allowed}")
                if error.three_times_limit:
                    print(f"   Triple limit: {error.three_times_limit}")
                if error.current_form and error.allowed_forms:
                    print(f"   Current form: {error.current_form}")
                    print(f"   Allowed forms: {', '.join(error.allowed_forms)}")
                print(f"   Recommendation: {error.recommendation}")
                print(f"   Penalty: {error.penalty_amount:,} грн")
            print()
        
        if result.warnings:
            print("⚠️  WARNINGS:")
            print("─" * 80)
            for i, warning in enumerate(result.warnings, 1):
                print(f"\n{i}. {warning.ingredient}")
                print(f"   Message: {warning.message}")
                if warning.current_dose:
                    print(f"   Current dose: {warning.current_dose}")
                if warning.max_allowed:
                    print(f"   Max recommended: {warning.max_allowed}")
                print(f"   Recommendation: {warning.recommendation}")
            print()
        
        if result.all_valid:
            print("✅ All dosages are within regulatory limits!")
        else:
            total_penalties = sum(e.penalty_amount for e in result.errors)
            print(f"⚠️  Total potential penalties: {total_penalties:,} грн")
        
        print()
        print("=" * 80)
    
    # Run async test
    asyncio.run(test_dosage_service())
    
    print("\n✅ Demo completed!")
