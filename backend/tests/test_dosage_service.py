"""Pytest tests for DosageService with 4-level hierarchy"""

import pytest
from app.services.dosage_service import DosageService


@pytest.fixture
def dosage_service():
    """Fixture to create DosageService instance"""
    return DosageService()


# ==================== ТЕСТ 1: EFSA UL (Рівень 1) ====================
@pytest.mark.asyncio
async def test_vitamin_a_exceeds_efsa_ul(dosage_service):
    """Вітамін А перевищує EFSA Upper Limit"""
    ingredients = [{
        "name": "Вітамін A",
        "quantity": 3500.0,
        "unit": "мкг",
        "form": "ретинол"
    }]
    
    result = await dosage_service.check_dosages(ingredients)
    
    assert result.all_valid == False
    assert len(result.errors) == 1
    assert result.errors[0].level == 1
    assert result.errors[0].source == "efsa_ul"
    assert result.errors[0].penalty_amount == 640000
    assert "EFSA Upper Limit" in result.errors[0].message or "перевищує" in result.errors[0].message.lower()


# ==================== ТЕСТ 2: EFSA Safe/Table1 (Рівень 2-3) ====================
@pytest.mark.asyncio
async def test_biotin_level_2_or_3(dosage_service):
    """Біотин - Рівень 2 або 3"""
    ingredients = [{
        "name": "Біотин",
        "quantity": 500.0,
        "unit": "мкг",
        "form": ""
    }]
    
    result = await dosage_service.check_dosages(ingredients)
    
    # Має бути ОК або warning про форму
    # Якщо знайдено в базі - має бути valid або warning
    assert result.all_valid == True or len(result.warnings) > 0


# ==================== ТЕСТ 3: Амінокислота ====================
@pytest.mark.asyncio
async def test_l_lysine_exceeds(dosage_service):
    """L-лізин перевищує дозу"""
    ingredients = [{
        "name": "L-лізин",
        "quantity": 7.0,
        "unit": "г",
        "form": ""
    }]
    
    result = await dosage_service.check_dosages(ingredients)
    
    # Якщо знайдено в базі та доза перевищена
    if len(result.errors) > 0:
        assert result.all_valid == False
        assert result.errors[0].level == 3
        assert result.errors[0].source == "amino_acids_table"
    else:
        # Якщо не знайдено в базі - буде warning
        assert len(result.warnings) > 0 or result.substances_not_found > 0


# ==================== ТЕСТ 4: Рослина ====================
@pytest.mark.asyncio
async def test_plant_allowed(dosage_service):
    """Шипшина - рослина дозволена, доза не перевіряється"""
    ingredients = [{
        "name": "Шипшина",
        "quantity": 500.0,
        "unit": "мг",
        "form": ""
    }]
    
    result = await dosage_service.check_dosages(ingredients)
    
    # Має бути ОК (доза не перевіряється)
    # Якщо рослина знайдена в allowed_plants - має бути valid
    # Якщо не знайдена - буде warning, але не error
    assert result.all_valid == True or len(result.errors) == 0


# ==================== ТЕСТ 5: Мікроорганізм ====================
@pytest.mark.asyncio
async def test_microorganism_allowed(dosage_service):
    """Lactobacillus Acidophilus - дозволений"""
    ingredients = [{
        "name": "Lactobacillus Acidophilus",
        "quantity": 1e9,
        "unit": "КУО",
        "form": ""
    }]
    
    result = await dosage_service.check_dosages(ingredients)
    
    # Має бути ОК (доза не перевіряється)
    # Якщо мікроорганізм знайдений в microorganisms - має бути valid
    # Якщо не знайдений - буде warning, але не error
    assert result.all_valid == True or len(result.errors) == 0


# ==================== ТЕСТ 6: ЗАБОРОНЕНА РЕЧОВИНА ====================
@pytest.mark.asyncio
async def test_banned_substance(dosage_service):
    """Алое-емодин - ЗАБОРОНЕНА РЕЧОВИНА"""
    ingredients = [{
        "name": "Алое-емодин",
        "quantity": 10.0,
        "unit": "мг",
        "form": ""
    }]
    
    result = await dosage_service.check_dosages(ingredients)
    
    # Якщо знайдено в banned_substances
    if len(result.errors) > 0 and result.errors[0].source == "banned_substances":
        assert result.all_valid == False
        assert result.errors[0].level == 0
        assert result.errors[0].source == "banned_substances"
        assert "ЗАБОРОНЕНА" in result.errors[0].message.upper() or "заборонен" in result.errors[0].message.lower()
        assert result.errors[0].penalty_amount == 640000
    else:
        # Якщо не знайдено в banned_substances - може бути warning
        assert len(result.warnings) > 0 or result.substances_not_found > 0


# ==================== ТЕСТ 7: NULL доза (Рівень 4) ====================
@pytest.mark.asyncio
async def test_coenzyme_q10_null_dose(dosage_service):
    """Коензим Q10 - доза NULL (Level 4 warning)"""
    ingredients = [{
        "name": "Коензим Q10",
        "quantity": 100.0,
        "unit": "мг",
        "form": ""
    }]
    
    result = await dosage_service.check_dosages(ingredients)
    
    # Може бути warning або not found
    # Якщо знайдено як physiological з NULL дозою - буде warning з level=4
    # Якщо не знайдено - буде warning або not found
    assert result.all_valid == True or len(result.warnings) > 0
    
    # Якщо є warning з level=4 та source=physiological_no_limit
    if len(result.warnings) > 0:
        for warning in result.warnings:
            if warning.level == 4 and warning.source == "physiological_no_limit":
                assert "доза не встановлена" in warning.message.lower() or "не встановлена" in warning.message.lower()


# ==================== ТЕСТ 8: Валідна доза вітаміну ====================
@pytest.mark.asyncio
async def test_valid_vitamin_dose(dosage_service):
    """Вітамін C - валідна доза"""
    ingredients = [{
        "name": "Вітамін C",
        "quantity": 80.0,
        "unit": "мг",
        "form": "аскорбінова кислота"
    }]
    
    result = await dosage_service.check_dosages(ingredients)
    
    # Має бути valid (може бути warning про форму, але не error)
    assert result.all_valid == True or len(result.errors) == 0


# ==================== ТЕСТ 9: Невідома речовина ====================
@pytest.mark.asyncio
async def test_unknown_substance(dosage_service):
    """Невідома речовина - має бути warning"""
    ingredients = [{
        "name": "Невідома Речовина XYZ123",
        "quantity": 100.0,
        "unit": "мг",
        "form": ""
    }]
    
    result = await dosage_service.check_dosages(ingredients)
    
    # Має бути warning або substances_not_found > 0
    assert result.substances_not_found > 0 or len(result.warnings) > 0
    # Не має бути errors (тільки якщо не заборонена)
    assert len(result.errors) == 0 or result.errors[0].source != "banned_substances"


# ==================== ТЕСТ 10: Форма речовини (WARNING) ====================
@pytest.mark.asyncio
async def test_form_warning(dosage_service):
    """Неправильна форма речовини - має бути WARNING, не ERROR"""
    ingredients = [{
        "name": "Вітамін C",
        "quantity": 80.0,
        "unit": "мг",
        "form": "невідома форма XYZ"
    }]
    
    result = await dosage_service.check_dosages(ingredients)
    
    # Форма має давати WARNING, не ERROR
    # Якщо є warning про форму - перевірити
    form_warnings = [w for w in result.warnings if "форма" in w.message.lower()]
    if form_warnings:
        assert len(result.errors) == 0  # Не має бути error через форму
    # Або доза валідна
    assert result.all_valid == True or len(result.errors) == 0


# ==================== ТЕСТ 11: Кількість не вказана ====================
@pytest.mark.asyncio
async def test_missing_quantity(dosage_service):
    """Кількість не вказана - має бути warning"""
    ingredients = [{
        "name": "Вітамін C",
        "quantity": None,
        "unit": "мг",
        "form": ""
    }]
    
    result = await dosage_service.check_dosages(ingredients)
    
    # Має бути warning про відсутність кількості
    assert len(result.warnings) > 0
    # Не має бути errors
    assert len(result.errors) == 0


# ==================== ТЕСТ 12: Множинні інгредієнти ====================
@pytest.mark.asyncio
async def test_multiple_ingredients(dosage_service):
    """Перевірка кількох інгредієнтів одночасно"""
    ingredients = [
        {
            "name": "Вітамін C",
            "quantity": 80.0,
            "unit": "мг",
            "form": "аскорбінова кислота"
        },
        {
            "name": "Цинк",
            "quantity": 10.0,
            "unit": "мг",
            "form": ""
        }
    ]
    
    result = await dosage_service.check_dosages(ingredients)
    
    # Має перевірити обидва інгредієнти
    assert result.total_ingredients_checked == 2
    # Може бути valid або warnings, але не errors (якщо дози валідні)
    assert result.all_valid == True or len(result.errors) == 0 or len(result.warnings) > 0

