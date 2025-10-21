# Backend Scripts

Утилітні скрипти для роботи з базою даних Supabase.

## 📂 Структура

```
scripts/
├── seed_database.py         # Початкове завантаження даних
├── update_regulations.py    # Оновлення регуляторних даних
└── README.md               # Ця документація
```

## 🚀 Використання

### 1. Початкове завантаження даних (`seed_database.py`)

Завантажує всі регуляторні дані з JSON файлів у Supabase.

**Що завантажується:**
- 📋 18 обов'язкових полів (`mandatory_fields`)
- ❌ 52 заборонені фрази (`forbidden_phrases`)
- 🏛️ 4 регуляторні акти (`regulatory_acts`)
- 💊 35 дозволених речовин (`allowed_substances`)

**Запуск:**

```bash
cd backend
python scripts/seed_database.py
```

**Інтерактивний режим:**

```
🗑️  Clear existing tables before seeding? (y/n): y

📋 Seeding mandatory_fields...
Mandatory Fields: 100%|████████████| 18/18 [00:02<00:00, 8.5field/s]
✅ Inserted 18 mandatory fields (0 failed)

❌ Seeding forbidden_phrases...
Forbidden Phrases: 100%|████████████| 52/52 [00:06<00:00, 8.2phrase/s]
✅ Inserted 52 forbidden phrases (0 failed)

🏛️  Seeding regulatory_acts...
Regulatory Acts: 100%|████████████| 4/4 [00:00<00:00, 12.1act/s]
✅ Inserted 4 regulatory acts (0 failed)

💊 Seeding allowed_substances...
Allowed Substances: 100%|████████████| 35/35 [00:04<00:00, 8.9substance/s]
✅ Inserted 35 allowed substances (0 failed)

🔍 Verifying seed data...
   ✅ mandatory_fields: 18/18 records
   ✅ forbidden_phrases: 52/52 records
   ✅ regulatory_acts: 4/4 records
   ✅ allowed_substances: 35/35 records

✅ All tables verified successfully!

════════════════════════════════════════════════════════════════════════════════
║                              SUMMARY                                          ║
════════════════════════════════════════════════════════════════════════════════

📊 Total records seeded: 109

Breakdown:
   • Mandatory Fields: 18
   • Forbidden Phrases: 52
   • Regulatory Acts: 4
   • Allowed Substances: 35
```

**Опції:**

- `y` - Очистити існуючі таблиці перед завантаженням (УВАГА: видалить всі дані!)
- `n` - Додати нові записи до існуючих (може призвести до дублікатів)

---

### 2. Оновлення регуляторних даних (`update_regulations.py`)

Синхронізує JSON файли з базою даних. Використовуйте коли оновлюєте нормативні дані.

**Запуск:**

```bash
cd backend
python scripts/update_regulations.py
```

**Приклад виводу:**

```
════════════════════════════════════════════════════════════════════════════════
║                        REGULATORY DATA UPDATER                                ║
════════════════════════════════════════════════════════════════════════════════

🔍 Checking for changes...
   📋 Mandatory fields: 18 in JSON vs 18 in DB
   ❌ Forbidden phrases: 52 in JSON vs 50 in DB
   🏛️  Regulatory acts: 4 in JSON vs 4 in DB
   💊 Allowed substances: 35 in JSON vs 35 in DB

📝 Changes detected in 1 table(s)

🔄 Update database with new data? (y/n): y

🔄 Syncing forbidden_phrases...
Syncing forbidden_phrases: 100%|████████████| 52/52 [00:02<00:00, 20.3record/s]
   ✅ forbidden_phrases: 2 inserted, 0 updated, 0 deleted

♻️  Reloading data cache...
   ✅ Cache reloaded

════════════════════════════════════════════════════════════════════════════════
║                              SUMMARY                                          ║
════════════════════════════════════════════════════════════════════════════════

✅ Update completed at 2025-10-20T18:30:45.123456

Changes:
   • Forbidden Phrases:
      + 2 inserted
      ~ 0 updated
      - 0 deleted
```

---

## 📊 Структура таблиць Supabase

### `mandatory_fields`

Обов'язкові поля для етикеток дієтичних добавок.

```sql
CREATE TABLE mandatory_fields (
  id SERIAL PRIMARY KEY,
  field_name TEXT NOT NULL,
  description TEXT NOT NULL,
  regulatory_source TEXT NOT NULL,
  article TEXT NOT NULL,
  criticality TEXT NOT NULL,
  error_message TEXT NOT NULL,
  recommendation TEXT NOT NULL,
  penalty_amount INTEGER NOT NULL,
  search_patterns JSONB NOT NULL
);
```

### `forbidden_phrases`

Заборонені фрази в маркетингу дієтичних добавок.

```sql
CREATE TABLE forbidden_phrases (
  id SERIAL PRIMARY KEY,
  phrase TEXT NOT NULL,
  category TEXT NOT NULL,
  variations JSONB NOT NULL,
  regulatory_source TEXT NOT NULL,
  article TEXT NOT NULL,
  explanation TEXT NOT NULL,
  severity TEXT NOT NULL,
  penalty_amount INTEGER NOT NULL
);
```

### `regulatory_acts`

Регуляторні акти України.

```sql
CREATE TABLE regulatory_acts (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  number TEXT NOT NULL,
  date DATE NOT NULL,
  description TEXT NOT NULL,
  key_requirements JSONB NOT NULL
);
```

### `allowed_substances`

Дозволені активні речовини для дієтичних добавок.

```sql
CREATE TABLE allowed_substances (
  id SERIAL PRIMARY KEY,
  substance_name TEXT NOT NULL,
  scientific_name TEXT NOT NULL,
  alternative_names JSONB NOT NULL,
  category TEXT NOT NULL,
  max_daily_dose NUMERIC NOT NULL,
  unit TEXT NOT NULL,
  three_times_limit NUMERIC NOT NULL,
  allowed_forms JSONB NOT NULL,
  regulatory_source TEXT NOT NULL
);
```

---

## 🔧 Налаштування

### Передумови

1. **Python 3.11+**
2. **Встановлені залежності:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Налаштований `.env` файл:**
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

### Перше налаштування Supabase

1. Створіть проєкт у [Supabase](https://supabase.com)
2. Створіть таблиці (SQL Editor або Dashboard)
3. Скопіюйте URL та API Key
4. Додайте до `.env` файлу
5. Запустіть `seed_database.py`

---

## ⚠️ Важливі примітки

### Безпека

- **НІКОЛИ** не використовуйте `seed_database.py` з опцією очищення (`y`) на production базі!
- Завжди робіть backup перед масовими операціями
- Використовуйте окремі Supabase проєкти для dev/staging/prod

### Продуктивність

- Скрипти використовують пакетну вставку для швидкості
- Progress bars (`tqdm`) показують прогрес у реальному часі
- Автоматична обробка помилок з логуванням

### Кешування

- `RegulatoryDataLoader` використовує `@lru_cache` для швидкості
- `update_regulations.py` автоматично очищає кеш після оновлення
- Якщо JSON файли змінилися вручну - перезапустіть додаток

---

## 🐛 Розв'язання проблем

### Помилка: "ModuleNotFoundError: No module named 'app'"

**Рішення:**
```bash
# Встановіть PYTHONPATH
export PYTHONPATH=/path/to/backend:$PYTHONPATH
python scripts/seed_database.py

# Або запускайте з кореня backend
cd backend
python scripts/seed_database.py
```

### Помилка: "supabase_client connection failed"

**Рішення:**
1. Перевірте `.env` файл
2. Переконайтеся що Supabase URL і Key правильні
3. Перевірте інтернет з'єднання
4. Перевірте що Supabase проєкт активний

### Помилка: "Table does not exist"

**Рішення:**
Створіть таблиці в Supabase SQL Editor:

```sql
-- Виконайте SQL команди зі структури вище
-- або використайте Supabase Dashboard → Table Editor
```

### Дублікати записів

**Причина:** Запустили `seed_database.py` без очищення таблиць

**Рішення:**
```bash
# Варіант 1: Очистити і перезапустити
python scripts/seed_database.py
# Введіть 'y' на запит про очищення

# Варіант 2: Видалити дублікати вручну через Supabase Dashboard
```

---

## 📚 Додаткові ресурси

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [Наказ МОЗ №1114](https://zakon.rada.gov.ua/) - офіційне джерело
- [Backend README](../README.md) - головна документація

---

## 🤝 Допомога

Якщо виникли проблеми:

1. Перевірте логи у консолі
2. Перевірте статус Supabase проєкту
3. Переконайтеся що JSON файли валідні
4. Зверніться до основного README

---

**Версія:** 1.0.0  
**Останнє оновлення:** 2025-10-20

