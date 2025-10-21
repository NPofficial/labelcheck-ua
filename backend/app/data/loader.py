"""Regulatory data loader with caching and search capabilities"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class RegulatoryDataLoader:
    """Loader for regulatory data with caching and search methods"""
    
    BASE_PATH = Path(__file__).parent / "regulatory"
    
    @classmethod
    @lru_cache(maxsize=1)
    def load_mandatory_fields(cls) -> List[Dict]:
        """
        Load mandatory fields from JSON file.
        
        Returns:
            List of mandatory field dictionaries with regulatory requirements
            
        Example:
            >>> fields = RegulatoryDataLoader.load_mandatory_fields()
            >>> len(fields)
            18
        """
        return cls._load_json_file("mandatory_fields.json")
    
    @classmethod
    @lru_cache(maxsize=1)
    def load_forbidden_phrases(cls) -> List[Dict]:
        """
        Load forbidden phrases from JSON file.
        
        Returns:
            List of forbidden phrase dictionaries with categories and penalties
            
        Example:
            >>> phrases = RegulatoryDataLoader.load_forbidden_phrases()
            >>> len(phrases)
            52
        """
        return cls._load_json_file("forbidden_phrases.json")
    
    @classmethod
    @lru_cache(maxsize=1)
    def load_allowed_substances(cls) -> List[Dict]:
        """
        Load allowed substances from JSON file.
        
        Returns:
            List of allowed substance dictionaries with dosage limits
            
        Example:
            >>> substances = RegulatoryDataLoader.load_allowed_substances()
            >>> len(substances)
            35
        """
        return cls._load_json_file("allowed_substances.json")
    
    @classmethod
    @lru_cache(maxsize=1)
    def load_regulatory_acts(cls) -> List[Dict]:
        """
        Load regulatory acts from JSON file.
        
        Returns:
            List of regulatory act dictionaries
            
        Example:
            >>> acts = RegulatoryDataLoader.load_regulatory_acts()
            >>> len(acts)
            4
        """
        return cls._load_json_file("regulatory_acts.json")
    
    @classmethod
    def get_field_by_name(cls, field_name: str) -> Optional[Dict]:
        """
        Get mandatory field by field name.
        
        Args:
            field_name: Field name to search for
            
        Returns:
            Field dictionary or None if not found
            
        Example:
            >>> field = RegulatoryDataLoader.get_field_by_name("edrpou_code")
            >>> field['description']
            'Код ЄДРПОУ виробника/імпортера'
        """
        fields = cls.load_mandatory_fields()
        for field in fields:
            if field.get("field_name") == field_name:
                return field
        return None
    
    @classmethod
    def get_substance_by_name(cls, name: str) -> Optional[Dict]:
        """
        Get substance by name with fuzzy matching.
        
        Searches in:
        - substance_name
        - scientific_name
        - alternative_names (all variations)
        
        Args:
            name: Substance name to search for (case-insensitive)
            
        Returns:
            Substance dictionary or None if not found
            
        Example:
            >>> substance = RegulatoryDataLoader.get_substance_by_name("Вітамін C")
            >>> substance['scientific_name']
            'Аскорбінова кислота'
            
            >>> substance = RegulatoryDataLoader.get_substance_by_name("ascorbic acid")
            >>> substance['substance_name']
            'Вітамін C'
        """
        substances = cls.load_allowed_substances()
        name_lower = name.lower().strip()
        
        for substance in substances:
            # Check main name
            if substance.get("substance_name", "").lower() == name_lower:
                return substance
            
            # Check scientific name
            if substance.get("scientific_name", "").lower() == name_lower:
                return substance
            
            # Check alternative names
            alt_names = substance.get("alternative_names", [])
            for alt_name in alt_names:
                if alt_name.lower() == name_lower:
                    return substance
        
        return None
    
    @classmethod
    def get_critical_errors(cls) -> List[Dict]:
        """
        Get only mandatory fields with critical severity.
        
        Returns:
            List of critical mandatory fields
            
        Example:
            >>> critical = RegulatoryDataLoader.get_critical_errors()
            >>> all(f['criticality'] == 'critical' for f in critical)
            True
        """
        fields = cls.load_mandatory_fields()
        return [field for field in fields if field.get("criticality") == "critical"]
    
    @classmethod
    def get_forbidden_by_category(cls, category: str) -> List[Dict]:
        """
        Get forbidden phrases by category.
        
        Args:
            category: Category name (treatment, disease, medical, veiled)
            
        Returns:
            List of forbidden phrases in specified category
            
        Example:
            >>> treatment = RegulatoryDataLoader.get_forbidden_by_category("treatment")
            >>> len(treatment)
            10
        """
        phrases = cls.load_forbidden_phrases()
        return [phrase for phrase in phrases if phrase.get("category") == category]
    
    @classmethod
    def get_full_prompt_context(cls) -> str:
        """
        Generate full context for Claude AI prompts.
        
        Returns:
            Formatted string with all regulatory data for Claude
            
        Example:
            >>> context = RegulatoryDataLoader.get_full_prompt_context()
            >>> "НОРМАТИВНА БАЗА УКРАЇНИ" in context
            True
        """
        acts = cls.load_regulatory_acts()
        mandatory = cls.load_mandatory_fields()
        forbidden = cls.load_forbidden_phrases()
        substances = cls.load_allowed_substances()
        
        context_parts = []
        
        # Header
        context_parts.append("═" * 80)
        context_parts.append("📜 НОРМАТИВНА БАЗА УКРАЇНИ ДЛЯ ДІЄТИЧНИХ ДОБАВОК")
        context_parts.append("═" * 80)
        context_parts.append("")
        
        # Regulatory Acts
        context_parts.append("🏛️ РЕГУЛЯТОРНІ АКТИ:")
        context_parts.append("─" * 80)
        for act in acts:
            context_parts.append(f"\n📋 {act['name']}")
            context_parts.append(f"   Номер: {act['number']}")
            context_parts.append(f"   Дата: {act['date']}")
            context_parts.append(f"   Опис: {act['description']}")
            if act.get('key_requirements'):
                context_parts.append("   Ключові вимоги:")
                for req in act['key_requirements']:
                    context_parts.append(f"   • {req}")
        
        context_parts.append("\n" + "═" * 80)
        
        # Critical Mandatory Fields
        critical_fields = cls.get_critical_errors()
        context_parts.append(f"🔴 КРИТИЧНІ ОБОВ'ЯЗКОВІ ПОЛЯ (штраф 640,000 грн): {len(critical_fields)} полів")
        context_parts.append("─" * 80)
        for field in critical_fields:
            context_parts.append(f"\n{field['id']}. {field['description']}")
            context_parts.append(f"   📌 Поле: {field['field_name']}")
            context_parts.append(f"   📄 Джерело: {field['regulatory_source']}")
            context_parts.append(f"   ⚠️ Помилка: {field['error_message']}")
            context_parts.append(f"   💡 Рекомендація: {field['recommendation']}")
            if field.get('search_patterns'):
                patterns = ", ".join(field['search_patterns'])
                context_parts.append(f"   🔍 Шукати: {patterns}")
        
        # Warning Fields
        warning_fields = [f for f in mandatory if f.get("criticality") == "warning"]
        if warning_fields:
            context_parts.append(f"\n⚠️ ПОПЕРЕДЖЕННЯ (штраф 62,600 грн): {len(warning_fields)} полів")
            context_parts.append("─" * 80)
            for field in warning_fields:
                context_parts.append(f"\n{field['id']}. {field['description']}")
                context_parts.append(f"   📌 Поле: {field['field_name']}")
                context_parts.append(f"   💡 Рекомендація: {field['recommendation']}")
        
        context_parts.append("\n" + "═" * 80)
        
        # Forbidden Phrases by Category
        context_parts.append(f"❌ ЗАБОРОНЕНІ ФРАЗИ: {len(forbidden)} фраз")
        context_parts.append("─" * 80)
        
        categories = {
            "treatment": "🚫 ЛІКУВАННЯ",
            "disease": "🏥 ЗАХВОРЮВАННЯ",
            "medical": "💊 МЕДИЧНА ТЕРМІНОЛОГІЯ",
            "veiled": "🎭 ЗАВУАЛЬОВАНІ ТВЕРДЖЕННЯ"
        }
        
        for cat_key, cat_name in categories.items():
            cat_phrases = cls.get_forbidden_by_category(cat_key)
            context_parts.append(f"\n{cat_name}: {len(cat_phrases)} фраз")
            for phrase in cat_phrases[:5]:  # Show first 5 as examples
                variations = ", ".join(phrase.get('variations', [])[:3])
                context_parts.append(f"   • '{phrase['phrase']}' (варіації: {variations})")
                context_parts.append(f"     Пояснення: {phrase['explanation']}")
                context_parts.append(f"     Штраф: {phrase['penalty_amount']:,} грн")
            if len(cat_phrases) > 5:
                context_parts.append(f"   ... та ще {len(cat_phrases) - 5} фраз у цій категорії")
        
        context_parts.append("\n" + "═" * 80)
        
        # Allowed Substances by Category
        context_parts.append(f"✅ ДОЗВОЛЕНІ РЕЧОВИНИ: {len(substances)} речовин")
        context_parts.append("─" * 80)
        
        substance_categories = {}
        for substance in substances:
            cat = substance.get('category', 'other')
            if cat not in substance_categories:
                substance_categories[cat] = []
            substance_categories[cat].append(substance)
        
        cat_names = {
            'vitamin': '💊 ВІТАМІНИ',
            'mineral': '⚗️ МІНЕРАЛИ',
            'fatty_acid': '🐟 ЖИРНІ КИСЛОТИ',
            'coenzyme': '🔬 КОЕНЗИМИ',
            'amino_acid': '🧬 АМІНОКИСЛОТИ',
            'amino_sugar': '🍬 АМІНЦУКРИ',
            'glycosaminoglycan': '🦴 ГЛІКОЗАМІНОГЛІКАНИ',
            'carotenoid': '🥕 КАРОТИНОЇДИ',
            'probiotic': '🦠 ПРОБІОТИКИ'
        }
        
        for cat_key, cat_substances in substance_categories.items():
            cat_display = cat_names.get(cat_key, cat_key.upper())
            context_parts.append(f"\n{cat_display}: {len(cat_substances)} речовин")
            for substance in cat_substances[:3]:  # Show first 3 as examples
                context_parts.append(
                    f"   • {substance['substance_name']} ({substance['scientific_name']}): "
                    f"макс. {substance['max_daily_dose']} {substance['unit']}/добу"
                )
            if len(cat_substances) > 3:
                context_parts.append(f"   ... та ще {len(cat_substances) - 3} речовин")
        
        context_parts.append("\n" + "═" * 80)
        context_parts.append("📊 ПІДСУМОК:")
        stats = cls.get_summary_stats()
        context_parts.append(f"   • Нормативних актів: {stats['regulatory_acts']}")
        context_parts.append(f"   • Обов'язкових полів: {stats['mandatory_fields']} "
                            f"({stats['critical_fields']} критичних)")
        context_parts.append(f"   • Заборонених фраз: {stats['forbidden_phrases']}")
        context_parts.append(f"   • Дозволених речовин: {stats['allowed_substances']}")
        context_parts.append("═" * 80)
        
        return "\n".join(context_parts)
    
    @classmethod
    def get_summary_stats(cls) -> Dict:
        """
        Get summary statistics of all regulatory data.
        
        Returns:
            Dictionary with counts of each data type
            
        Example:
            >>> stats = RegulatoryDataLoader.get_summary_stats()
            >>> stats['mandatory_fields']
            18
            >>> stats['forbidden_phrases']
            52
        """
        mandatory = cls.load_mandatory_fields()
        critical = cls.get_critical_errors()
        
        return {
            "regulatory_acts": len(cls.load_regulatory_acts()),
            "mandatory_fields": len(mandatory),
            "critical_fields": len(critical),
            "warning_fields": len(mandatory) - len(critical),
            "forbidden_phrases": len(cls.load_forbidden_phrases()),
            "allowed_substances": len(cls.load_allowed_substances()),
        }
    
    @classmethod
    def _load_json_file(cls, filename: str) -> List[Dict]:
        """
        Load JSON file from regulatory directory.
        
        Args:
            filename: Name of JSON file to load
            
        Returns:
            List of dictionaries from JSON file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        file_path = cls.BASE_PATH / filename
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} items from {filename}")
                return data
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filename}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}", exc_info=True)
            return []
    
    @classmethod
    def clear_cache(cls):
        """
        Clear all cached data.
        
        Use this method when regulatory files are updated and need to be reloaded.
        
        Example:
            >>> RegulatoryDataLoader.clear_cache()
            >>> # Data will be reloaded on next access
        """
        cls.load_mandatory_fields.cache_clear()
        cls.load_forbidden_phrases.cache_clear()
        cls.load_allowed_substances.cache_clear()
        cls.load_regulatory_acts.cache_clear()
        logger.info("Cleared all regulatory data cache")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "REGULATORY DATA LOADER - DEMO" + " " * 28 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # 1. Load all data
    print("📚 Loading regulatory data...")
    mandatory = RegulatoryDataLoader.load_mandatory_fields()
    forbidden = RegulatoryDataLoader.load_forbidden_phrases()
    substances = RegulatoryDataLoader.load_allowed_substances()
    acts = RegulatoryDataLoader.load_regulatory_acts()
    print(f"✅ Loaded: {len(mandatory)} fields, {len(forbidden)} phrases, "
          f"{len(substances)} substances, {len(acts)} acts")
    print()
    
    # 2. Summary statistics
    print("📊 Summary Statistics:")
    print("─" * 80)
    stats = RegulatoryDataLoader.get_summary_stats()
    for key, value in stats.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    print()
    
    # 3. Search by field name
    print("🔍 Search Examples:")
    print("─" * 80)
    field = RegulatoryDataLoader.get_field_by_name("edrpou_code")
    if field:
        print(f"✓ Field 'edrpou_code':")
        print(f"  Description: {field['description']}")
        print(f"  Penalty: {field['penalty_amount']:,} грн")
    print()
    
    # 4. Fuzzy substance search
    print("🔬 Substance Search (fuzzy matching):")
    print("─" * 80)
    test_names = ["Вітамін C", "ascorbic acid", "Цинк", "zinc"]
    for name in test_names:
        substance = RegulatoryDataLoader.get_substance_by_name(name)
        if substance:
            print(f"✓ '{name}' → {substance['substance_name']} "
                  f"({substance['scientific_name']}): "
                  f"max {substance['max_daily_dose']} {substance['unit']}/день")
    print()
    
    # 5. Critical errors
    print("🔴 Critical Mandatory Fields:")
    print("─" * 80)
    critical = RegulatoryDataLoader.get_critical_errors()
    print(f"Found {len(critical)} critical fields:")
    for field in critical[:3]:
        print(f"   • {field['field_name']}: {field['description']}")
    print(f"   ... and {len(critical) - 3} more")
    print()
    
    # 6. Forbidden phrases by category
    print("❌ Forbidden Phrases by Category:")
    print("─" * 80)
    categories = ["treatment", "disease", "medical", "veiled"]
    for category in categories:
        phrases = RegulatoryDataLoader.get_forbidden_by_category(category)
        print(f"   {category.upper()}: {len(phrases)} phrases")
        if phrases:
            print(f"      Example: '{phrases[0]['phrase']}' → "
                  f"{phrases[0]['penalty_amount']:,} грн penalty")
    print()
    
    # 7. Generate full prompt context
    print("📝 Generating Full Prompt Context for Claude AI...")
    print("─" * 80)
    context = RegulatoryDataLoader.get_full_prompt_context()
    print(f"✅ Generated context: {len(context):,} characters")
    print()
    print("Preview (first 500 chars):")
    print(context[:500])
    print("...")
    print()
    
    # 8. Cache demonstration
    print("💾 Cache Management:")
    print("─" * 80)
    print("All data is cached with @lru_cache for performance")
    print("To reload data after file updates:")
    print(">>> RegulatoryDataLoader.clear_cache()")
    print()
    
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 32 + "DEMO COMPLETE" + " " * 32 + "║")
    print("╚" + "═" * 78 + "╝")
