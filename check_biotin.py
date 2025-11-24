import os
from supabase import create_client

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Пошук біотину
result = supabase.table("substance_form_conversions").select("*").or_(
    "substance_name_ua.ilike.%біотин%,substance_name_ua.ilike.%В7%,base_substance_ua.ilike.%біотин%"
).execute()

print(f"\nЗнайдено записів: {len(result.data)}")
for row in result.data:
    print(f"\nID: {row['id']}")
    print(f"Назва: {row['substance_name_ua']}")
    print(f"База: {row['base_substance_ua']}")
    print(f"Варіації: {row.get('name_variations', [])}")
