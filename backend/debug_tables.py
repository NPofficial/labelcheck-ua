#!/usr/bin/env python3
"""
Скрипт для перевірки до яких таблиць звертається система при перевірці інгредієнта
"""

import asyncio
import sys
from app.db.supabase_client import SupabaseClient

client = SupabaseClient().client

def check_table(table_name: str, search_field: str, search_value: str):
    """Перевіряє чи є запис в таблиці"""
    try:
        result = client.table(table_name).select("*").ilike(search_field, f"%{search_value}%").execute()
        return result.data
    except Exception as e:
        return f"ERROR: {e}"


def search_ingredient(ingredient_name: str):
    """Шукає інгредієнт у всіх таблицях"""
    
    print(f"\n{'='*70}")
    print(f"🔍 ПОШУК: '{ingredient_name}'")
    print('='*70)
    
    tables = [
        # Таблиця, поле для пошуку, опис
        ("substance_form_conversions", "substance_name_ua", "Форми речовин (вітаміни/мінерали)"),
        ("substance_form_conversions", "name_variations", "Варіанти назв форм"),
        ("substance_form_conversions", "base_substance", "Базові речовини"),
        ("allowed_vitamins_minerals", "name_ua", "Дозволені вітаміни/мінерали"),
        ("amino_acids", "name_ua", "Амінокислоти"),
        ("plants", "name_ua", "Рослини"),
        ("microorganisms", "name_ua", "Мікроорганізми"),
        ("max_doses_table1", "substance_name_ua", "Фізіологічні речовини (макс дози)"),
        ("novel_foods", "name_ua", "Нові продукти"),
        ("excipients", "name_ua", "Допоміжні речовини"),
        ("efsa_limits", "substance_name", "EFSA ліміти"),
    ]
    
    found_in = []
    
    for table_name, search_field, description in tables:
        result = check_table(table_name, search_field, ingredient_name)
        
        if isinstance(result, str) and result.startswith("ERROR"):
            print(f"\n❌ {table_name}.{search_field}")
            print(f"   {result}")
        elif result:
            found_in.append(table_name)
            print(f"\n✅ {table_name}.{search_field} - ЗНАЙДЕНО ({len(result)} записів)")
            print(f"   📋 {description}")
            for row in result[:3]:  # Показати перші 3
                # Показати ключові поля
                if 'base_substance' in row:
                    print(f"   → base_substance: {row.get('base_substance')}")
                if 'coefficient' in row:
                    print(f"   → coefficient: {row.get('coefficient')}")
                if 'name_ua' in row:
                    print(f"   → name_ua: {row.get('name_ua')}")
                if 'max_dose' in row:
                    print(f"   → max_dose: {row.get('max_dose')} {row.get('unit', '')}")
                if 'ul_value' in row:
                    print(f"   → ul_value: {row.get('ul_value')} {row.get('ul_unit', '')}")
        else:
            print(f"\n⬜ {table_name}.{search_field} - не знайдено")
    
    print(f"\n{'='*70}")
    if found_in:
        print(f"📊 РЕЗУЛЬТАТ: Знайдено в таблицях: {', '.join(found_in)}")
    else:
        print(f"⚠️ РЕЗУЛЬТАТ: НЕ ЗНАЙДЕНО в жодній таблиці!")
    print('='*70)


def list_all_magnesium_forms():
    """Показати всі форми магнію в БД"""
    print(f"\n{'='*70}")
    print("🧲 ВСІ ФОРМИ МАГНІЮ В БАЗІ ДАНИХ")
    print('='*70)
    
    result = client.table("substance_form_conversions").select("*").ilike("base_substance", "%магн%").execute()
    
    if result.data:
        print(f"\n📋 substance_form_conversions ({len(result.data)} записів):\n")
        for row in result.data:
            print(f"  • {row.get('substance_name_ua', 'N/A')}")
            print(f"    → base: {row.get('base_substance')}, коеф: {row.get('coefficient')}")
            vars = row.get('name_variations', [])
            if vars:
                vars_str = ', '.join(vars[:5]) if isinstance(vars, list) else str(vars)[:80]
                print(f"    → варіанти: {vars_str}")
            print()
    else:
        print("❌ Форми магнію не знайдено!")
    
    # Також перевірити allowed_vitamins_minerals
    result2 = client.table("allowed_vitamins_minerals").select("*").ilike("name_ua", "%магн%").execute()
    if result2.data:
        print(f"\n📋 allowed_vitamins_minerals ({len(result2.data)} записів):\n")
        for row in result2.data:
            print(f"  • {row.get('name_ua', 'N/A')}")
            print(f"    → allowed_forms: {row.get('allowed_forms', [])}")
            print()


def show_all_tables():
    """Показати список всіх таблиць які використовує система"""
    print(f"\n{'='*70}")
    print("📚 ТАБЛИЦІ БАЗИ ДАНИХ ДЛЯ ПЕРЕВІРКИ ЕТИКЕТОК")
    print('='*70)
    
    tables_info = [
        ("substance_form_conversions", "Конверсія форм речовин → елементарний вміст"),
        ("allowed_vitamins_minerals", "Дозволені вітаміни та мінерали (Наказ 1114)"),
        ("amino_acids", "Дозволені амінокислоти"),
        ("plants", "Дозволені рослини"),
        ("microorganisms", "Дозволені мікроорганізми"),
        ("max_doses_table1", "Максимальні дози фізіологічних речовин"),
        ("novel_foods", "Нові продукти (Novel Foods)"),
        ("excipients", "Допоміжні речовини (E-добавки)"),
        ("efsa_limits", "EFSA Upper Limits (макс безпечні дози)"),
        ("forbidden_phrases", "Заборонені фрази на етикетці"),
        ("check_sessions", "Сесії перевірок (Quick/Full Check)"),
    ]
    
    for table, description in tables_info:
        try:
            result = client.table(table).select("*", count="exact").limit(1).execute()
            count = result.count if hasattr(result, 'count') else len(result.data or [])
            print(f"\n✅ {table}")
            print(f"   📋 {description}")
            print(f"   📊 Записів: {count if count else '?'}")
        except Exception as e:
            print(f"\n❌ {table} - {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Використання:")
        print("  python debug_tables.py search <назва_інгредієнта>")
        print("  python debug_tables.py magnesium")
        print("  python debug_tables.py tables")
        print()
        print("Приклади:")
        print("  python debug_tables.py search 'гліцинат магнію'")
        print("  python debug_tables.py search 'цитрат магнію'")
        print("  python debug_tables.py search 'вітамін В6'")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "search" and len(sys.argv) > 2:
        ingredient = " ".join(sys.argv[2:])
        search_ingredient(ingredient)
    elif command == "magnesium":
        list_all_magnesium_forms()
    elif command == "tables":
        show_all_tables()
    else:
        print(f"Невідома команда: {command}")

