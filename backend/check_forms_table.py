import os
from supabase import create_client

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Структура таблиці
print("\n📋 СТРУКТУРА ТАБЛИЦІ substance_form_conversions:")
print("="*60)

result = supabase.table('substance_form_conversions').select('*').limit(3).execute()

if result.data:
    print(f"\nПриклад запису:")
    for key, value in result.data[0].items():
        print(f"  {key}: {value}")
    
    print(f"\n\nВсього записів: {len(result.data)}")
else:
    print("Таблиця порожня!")

# Пошук магнію
print("\n\n🔍 ЧИ Є МАГНІЙ?")
print("="*60)
result = supabase.table('substance_form_conversions').select('*').ilike('compound_name', '%магній%').execute()
print(f"Знайдено записів: {len(result.data)}")
for row in result.data[:3]:
    print(f"\n• {row.get('compound_name')}")
    print(f"  base_substance: {row.get('base_substance')}")
    print(f"  coefficient: {row.get('coefficient')}")
