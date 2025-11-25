#!/bin/bash
# Повний тест етикетки: Quick Check → Full Check → Звіт

cd "/Users/admin/Downloads/label check/backend"

# Перевірка аргументу
if [ -z "$1" ]; then
    echo "❌ Використання: ./test_label.sh <шлях_до_зображення>"
    echo "   Приклад: ./test_label.sh '/Users/admin/Downloads/етикетка.jpg'"
    exit 1
fi

IMAGE_PATH="$1"

if [ ! -f "$IMAGE_PATH" ]; then
    echo "❌ Файл не знайдено: $IMAGE_PATH"
    exit 1
fi

# Очистити старі файли
rm -f quick_final.json full_final.json

echo "🔄 Крок 1: Quick Check (OCR)..."
curl -s -X POST http://localhost:8000/api/check-label/quick \
  -F "file=@$IMAGE_PATH" \
  -o quick_final.json

# Перевірка помилки Quick Check
if grep -q '"detail"' quick_final.json; then
    echo "❌ Помилка Quick Check:"
    cat quick_final.json
    exit 1
fi

CHECK_ID=$(cat quick_final.json | python3 -c "import sys, json; print(json.load(sys.stdin)['check_id'])")
echo "✅ Quick Check OK! check_id: $CHECK_ID"

echo "🔄 Крок 2: Full Check (Валідація)..."
curl -s -X POST http://localhost:8000/api/check-label/full \
  -H "Content-Type: application/json" \
  -d "{\"check_id\": \"$CHECK_ID\"}" \
  -o full_final.json

# Перевірка помилки Full Check
if grep -q '"detail"' full_final.json; then
    echo "❌ Помилка Full Check:"
    cat full_final.json
    exit 1
fi

echo "✅ Full Check OK!"
echo ""

# Вивід звіту
cat full_final.json | python3 -c "
import sys, json

d = json.load(sys.stdin)

print('\n' + '='*70)
print('📋 ПОВНИЙ ЗВІТ ПЕРЕВІРКИ ЕТИКЕТКИ')
print('='*70)

# Перевірка на помилку API
if 'detail' in d:
    print(f'\n❌ ПОМИЛКА API: {d[\"detail\"]}')
    exit()

# 1. ПРОДУКТ
pi = d.get('product_info', {})
print(f'\n📦 ПРОДУКТ:')
print(f'   Назва: {pi.get(\"name\", \"N/A\")}')
print(f'   Форма: {pi.get(\"form\", \"N/A\")}')
print(f'   Кількість: {pi.get(\"quantity\", \"N/A\")}')
print(f'   Партія: {pi.get(\"batch_number\", \"N/A\")}')

# 2. СТАТИСТИКА
stats = d.get('stats', {})
print(f'\n📊 СТАТИСТИКА:')
print(f'   Всього інгредієнтів: {len(pi.get(\"ingredients\", []))}')
print(f'   Не знайдено: {stats.get(\"substances_not_found\", 0)}')

# 3. КРИТИЧНІ ПОМИЛКИ
errors = d.get('errors', [])
print(f'\n🔴 КРИТИЧНІ ПОМИЛКИ: {len(errors)}')
if errors:
    for e in errors:
        print(f'   ❌ {e.get(\"ingredient\", e.get(\"field\", \"?\"))}: {e.get(\"message\")}')
        if e.get('penalty_amount'):
            print(f'      Штраф: {e.get(\"penalty_amount\"):,} грн')
else:
    print('   ✅ Критичних помилок немає!')

# 4. ПОПЕРЕДЖЕННЯ
warnings = d.get('warnings', [])
print(f'\n🟡 ПОПЕРЕДЖЕННЯ: {len(warnings)}')
if warnings:
    for w in warnings:
        print(f'   ⚠️ {w.get(\"ingredient\", w.get(\"field\", \"?\"))}: {w.get(\"message\")}')
else:
    print('   ✅ Попереджень немає!')

# 5. ОБОВ'ЯЗКОВІ ПОЛЯ - ВИПРАВЛЕНО: mandatory_phrases замість mandatory_fields!
mf = d.get('mandatory_phrases', {})
print(f'\n📝 ОБОВ\\'ЯЗКОВІ ПОЛЯ:')
if mf:
    fields = [
        ('has_dietary_supplement_label', 'Напис \"ДІЄТИЧНА ДОБАВКА\"'),
        ('has_not_medicine', 'Напис \"Не є лікарським засобом\"'),
        ('has_not_exceed_dose', 'Попередження про дозу'),
        ('has_not_replace_diet', 'Не замінює раціон'),
        ('has_keep_away_children', 'Зберігати від дітей'),
    ]
    for key, name in fields:
        status = '✅' if mf.get(key) else '❌'
        print(f'   {status} {name}')
else:
    print('   ⚠️ Дані про обов\\'язкові поля не отримано')

# 6. ЗАБОРОНЕНІ ФРАЗИ (з compliance_errors)
compliance = d.get('compliance_errors', [])
forbidden = [e for e in compliance if e.get('type') == 'forbidden_phrase']
print(f'\n🚫 ЗАБОРОНЕНІ ФРАЗИ: {len(forbidden)}')
if forbidden:
    for p in forbidden[:5]:
        print(f'   ❌ \"{p.get(\"phrase\", p.get(\"message\"))}\"')
else:
    print('   ✅ Заборонених фраз не знайдено!')

# 7. ОПЕРАТОР
op = d.get('operator', {})
print(f'\n🏢 ОПЕРАТОР РИНКУ:')
if op:
    print(f'   Назва: {op.get(\"name\", \"N/A\")}')
    edrpou = op.get('edrpou')
    print(f'   ЄДРПОУ: {edrpou if edrpou else \"❌ НЕ ВКАЗАНО\"}')
    print(f'   Адреса: {op.get(\"address\", \"N/A\")}')
    phone = op.get('phone')
    if phone:
        print(f'   Телефон: {phone}')
else:
    print('   ⚠️ Дані про оператора відсутні')

# 8. ВИРОБНИК
mfr = d.get('manufacturer', {})
print(f'\n🏭 ВИРОБНИК:')
if mfr:
    print(f'   Назва: {mfr.get(\"name\", \"N/A\")}')
    print(f'   Адреса: {mfr.get(\"address\", \"N/A\")}')
else:
    print('   N/A (співпадає з оператором)')

# 9. ДОДАТКОВА ІНФОРМАЦІЯ
print(f'\n📋 ДОДАТКОВО:')
print(f'   Добова доза: {d.get(\"daily_dose\", \"N/A\")}')
storage = d.get('storage', 'N/A')
if storage and len(storage) > 60:
    storage = storage[:60] + '...'
print(f'   Зберігання: {storage}')
print(f'   Термін: {d.get(\"shelf_life\", \"N/A\")}')
print(f'   ТУ У: {d.get(\"tech_specs\", \"N/A\")}')
allergens = d.get('allergens', [])
allergens_str = ', '.join(allergens) if allergens else 'не виявлено'
print(f'   Алергени: {allergens_str}')

# 10. ЗАСТЕРЕЖЕННЯ З ЕТИКЕТКИ
label_warnings = d.get('label_warnings', [])
if label_warnings:
    print(f'\n⚠️ ЗАСТЕРЕЖЕННЯ:')
    for w in label_warnings[:3]:
        print(f'   • {w}')

# 11. ІНГРЕДІЄНТИ
ings = pi.get('ingredients', [])
print(f'\n🧪 ІНГРЕДІЄНТИ ({len(ings)}):')
for ing in ings:
    name = ing.get('name', 'N/A')
    base = ing.get('base_substance', name)
    qty = ing.get('quantity', '')
    unit = ing.get('unit', '')
    ing_type = ing.get('type', '')
    is_ext = '🌿' if ing.get('is_extract') else '  '
    dose = f'{qty} {unit}' if qty else ''
    found = '' if ing.get('found', True) else ' ⚠️'
    print(f'   {is_ext} {name} → {base} {dose} [{ing_type}]{found}')

# 12. ЗАГАЛЬНИЙ СТАТУС
print(f'\n' + '='*70)
total_errors = len(errors) + len(forbidden)
if total_errors == 0 and len(warnings) <= 2:
    print('🎉 СТАТУС: ЕТИКЕТКА ВІДПОВІДАЄ ВИМОГАМ!')
elif total_errors == 0:
    print('⚠️ СТАТУС: ЕТИКЕТКА ПОТРЕБУЄ УВАГИ')
else:
    print(f'❌ СТАТУС: ВИЯВЛЕНО ПОРУШЕННЯ ({total_errors})')

# 13. ШТРАФИ
penalties = d.get('penalties', {})
total = penalties.get('total_amount', 0)
if total > 0:
    print(f'\n💰 ПОТЕНЦІЙНИЙ ШТРАФ: {total:,} грн')

print('='*70 + '\n')
"

