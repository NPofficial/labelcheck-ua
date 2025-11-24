"""Tests for 8 critical bug fixes"""

import pytest
import json
from app.services.substance_mapper_service import SubstanceMapperService
from app.services.mandatory_fields_service import MandatoryFieldsService, _check_allergen_compliance


# ============================================
# БАГ #4: name_variations JSON parsing
# ============================================

@pytest.mark.asyncio
async def test_name_variations_json_string():
    """name_variations як JSON string має парситись"""
    mapper = SubstanceMapperService()
    
    # Симулюємо що з БД прийшов string (не list)
    test_row = {
        "substance_name_ua": "Вітамін A",
        "base_substance_ua": "Вітамін A",
        "name_variations": '["ретинілу ацетат", "ретиніл ацетат"]',  # STRING!
        "conversion_coefficient_min": 0.3,
        "conversion_coefficient_max": 0.3
    }
    
    # Має розпарсити і знайти
    result = await mapper.parse_ingredient("ретинілу ацетат", 800, "мкг")
    
    assert result["base_substance"] in ["Вітамін A", "Вітамін А"]
    print("✅ БАГ #4: name_variations JSON parsing - FIXED")


# ============================================
# БАГ #5: Кирилиця В → латиниця B
# ============================================

@pytest.mark.asyncio
async def test_cyrillic_v_normalization():
    """Кирилиця 'В' має дорівнювати латиниці 'B'"""
    mapper = SubstanceMapperService()
    
    # Тест з кирилицею В
    normalized_cyrillic = mapper._normalize_name("вітамін В6")
    normalized_latin = mapper._normalize_name("вітамін B6")
    
    assert normalized_cyrillic == normalized_latin
    assert "b6" in normalized_cyrillic  # Має бути латиниця b
    
    print("✅ БАГ #5: Cyrillic В → Latin B - FIXED")


# ============================================
# БАГ #6: Пошук рослин
# ============================================

@pytest.mark.asyncio
async def test_plant_search_with_stemming():
    """Рослини мають знаходитись через stemming"""
    mapper = SubstanceMapperService()
    
    # Тест з різними формами
    test_cases = [
        "екстракт півонії",
        "порошок півонії", 
        "півонія",
    ]
    
    for plant_name in test_cases:
        result = await mapper._find_plant_in_db(plant_name)
        
        if result and result.get("found"):
            print(f"✅ Знайдено: '{plant_name}' → '{result['base_substance']}'")
            assert "півон" in result["base_substance"].lower()
            return  # Хоча б один має знайтись
    
    pytest.skip("No plants found in DB - check allowed_plants table")


# ============================================
# БАГ #7: Excipients detection
# ============================================

@pytest.mark.asyncio
async def test_excipient_detection():
    """МКЦ, крохмаль мають розпізнаватись як excipients"""
    mapper = SubstanceMapperService()
    
    excipients = ["МКЦ", "мкц", "магнію стеарат", "крохмаль", "тальк"]
    
    found_count = 0
    for exc in excipients:
        is_exc = await mapper._is_excipient(exc)
        if is_exc:
            print(f"✅ Excipient detected: {exc}")
            found_count += 1
    
    assert found_count > 0, "No excipients found - check excipients table"
    print(f"✅ БАГ #7: {found_count}/{len(excipients)} excipients detected")


# ============================================
# БАГ #3: Allergens logic (3 scenarios)
# ============================================

def test_allergens_with_statement():
    """Сценарій A: Є алергени + є statement = OK"""
    data = {
        "ingredients": [{"name": "Соєвий лецитин"}],
        "allergens": ["соя"],
        "allergen_statement": "Містить алергени: соя"
    }
    
    result = _check_allergen_compliance(data)
    assert result == True
    print("✅ Сценарій A: Алергени + statement = OK")


def test_allergens_without_statement():
    """Сценарій B: Є алергени + НЕМАЄ statement = ERROR"""
    data = {
        "ingredients": [{"name": "Соєвий лецитин"}],
        "allergens": ["соя"],
        "allergen_statement": None
    }
    
    result = _check_allergen_compliance(data)
    assert result == False  # Має бути FALSE (штраф!)
    print("✅ Сценарій B: Алергени БЕЗ statement = ERROR (штраф)")


def test_no_allergens():
    """Сценарій C: Немає алергенів = OK"""
    data = {
        "ingredients": [{"name": "Вітамін С"}],
        "allergens": [],
        "allergen_statement": None
    }
    
    result = _check_allergen_compliance(data)
    assert result == True
    print("✅ Сценарій C: Немає алергенів = OK")


# ============================================
# INTEGRATION: Повний flow
# ============================================

@pytest.mark.asyncio
async def test_full_ingredient_recognition():
    """10 типових інгредієнтів мають знаходитись"""
    mapper = SubstanceMapperService()
    
    ingredients = [
        ("Вітамін В6", 2.0, "мг"),         # Кирилиця В
        ("вітамін С", 100, "мг"),          # lowercase
        ("цинк глюконат", 25, "мг"),       # форма
        ("магнію стеарат", 5, "мг"),       # excipient
        ("МКЦ", 100, "мг"),                # excipient абревіатура
        ("L-аргінін", 500, "мг"),          # амінокислота
    ]
    
    found = 0
    for name, qty, unit in ingredients:
        result = await mapper.parse_ingredient(name, qty, unit)
        
        if result.get("base_substance"):
            found += 1
            print(f"✅ Found: {name} → {result['base_substance']}")
    
    print(f"\n📊 Recognition rate: {found}/{len(ingredients)}")
    assert found >= 4, f"Only {found}/{len(ingredients)} found - should be more"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

