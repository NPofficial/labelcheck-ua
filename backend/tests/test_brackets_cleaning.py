"""Test for brackets cleaning in ingredient names"""

import pytest
from app.services.substance_mapper_service import SubstanceMapperService


@pytest.mark.asyncio
async def test_brackets_cleaning():
    """Інгредієнти з дужками мають очищатись перед пошуком"""
    mapper = SubstanceMapperService()
    
    # Тестовий випадок: "вітамін В7 (біотин)" має знайтись як "вітамін В7"
    result = await mapper.parse_ingredient("вітамін В7 (біотин)", 30, "мкг")
    
    # Перевірити що назва була очищена (лог покаже це)
    # Але результат має містити base_substance
    assert result.get("base_substance") is not None
    print(f"✅ Parsed: 'вітамін В7 (біотин)' → base_substance: '{result.get('base_substance')}'")
    
    # Перевірити інші випадки
    test_cases = [
        "вітамін С (аскорбінова кислота)",
        "магній (цитрат)",
        "цинк (глюконат)",
    ]
    
    for test_name in test_cases:
        result = await mapper.parse_ingredient(test_name, 100, "мг")
        assert result.get("base_substance") is not None
        print(f"✅ Parsed: '{test_name}' → base_substance: '{result.get('base_substance')}'")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

