# Label Check - Complete Setup Guide 🚀

Покрокова інструкція для запуску всього проєкту з нуля.

## 📋 Передумови

Переконайтесь що встановлено:

- [x] **Node.js** 18+ ([Download](https://nodejs.org/))
- [x] **Python** 3.11+ ([Download](https://www.python.org/downloads/))
- [x] **Git** ([Download](https://git-scm.com/downloads))
- [x] **Code Editor** (VS Code рекомендовано)

## 🔑 Реєстрація сервісів

### 1. Anthropic (Claude AI)

1. Перейдіть на https://console.anthropic.com/
2. Створіть account
3. Settings → API Keys → Create Key
4. Скопіюйте ключ (формат: `sk-ant-api03-...`)
5. Додайте $5-10 credits для тестування

✅ **Отримано:** `CLAUDE_API_KEY`

### 2. Supabase (Database)

1. Перейдіть на https://supabase.com/
2. New Project → Оберіть назву, регіон, пароль
3. Дочекайтесь створення (~2 хвилини)
4. Project Settings → API
5. Скопіюйте:
   - **URL**: `https://xxxxx.supabase.co`
   - **anon/public key**: `eyJhbGci...`

✅ **Отримано:** `SUPABASE_URL`, `SUPABASE_KEY`

## 🛠️ Налаштування Backend

### Крок 1: Підготовка

```bash
cd "/Users/admin/Downloads/label check/backend"
```

### Крок 2: Virtual Environment

```bash
# Створення
python3 -m venv venv

# Активація (macOS/Linux)
source venv/bin/activate

# Активація (Windows)
venv\Scripts\activate

# Перевірка
which python  # Має показати шлях до venv
```

### Крок 3: Встановлення залежностей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

⏱️ Займе ~2-3 хвилини

### Крок 4: Environment Variables

```bash
cp .env.example .env
```

Відредагуйте `.env` (використовуйте nano, vim або VS Code):

```env
# ОБОВ'ЯЗКОВО заповніть:
CLAUDE_API_KEY=sk-ant-api03-YOUR_KEY_HERE
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=eyJhbGci_YOUR_KEY_HERE

# Опціонально (defaults OK):
ALLOWED_ORIGINS=http://localhost:3000
DEBUG=True
```

### Крок 5: Створення таблиць у Supabase

1. Відкрийте Supabase Dashboard → SQL Editor
2. Скопіюйте SQL з `backend/README.md` (розділ Database Setup)
3. Виконайте SQL для створення 4 таблиць:
   - `mandatory_fields`
   - `forbidden_phrases`
   - `allowed_substances`
   - `regulatory_acts`

**Швидкий SQL (все разом):**

```sql
-- Створіть всі 4 таблиці
-- (див. повний SQL у backend/README.md → Database Setup)
```

### Крок 6: Завантаження нормативних даних

```bash
python scripts/seed_database.py
```

**Інтерактивний режим:**
```
🗑️  Clear existing tables before seeding? (y/n): y  [Enter]
```

✅ **Результат:** 109 records (18+52+35+4)

### Крок 7: Запуск Backend

```bash
uvicorn app.main:app --reload
```

✅ **Backend працює:** http://localhost:8000  
📖 **API Docs:** http://localhost:8000/docs

**Тест:**

```bash
curl http://localhost:8000/health
```

Очікувана відповідь:
```json
{"status": "healthy", "app": "Label Check API", ...}
```

---

## 🎨 Налаштування Frontend

### Крок 1: Підготовка

```bash
cd "/Users/admin/Downloads/label check/frontend"
```

### Крок 2: Встановлення залежностей

```bash
npm install
```

⏱️ Займе ~3-5 хвилин

### Крок 3: Environment Variables

```bash
cp .env.local.example .env.local
```

Відредагуйте `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Крок 4: Запуск Frontend

```bash
npm run dev
```

✅ **Frontend працює:** http://localhost:3000

**Тест:**

Відкрийте http://localhost:3000 у браузері - повинна відкритись головна сторінка.

---

## ✅ Перевірка установки

### Backend Checklist

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. API docs доступні
open http://localhost:8000/docs

# 3. Database має дані
curl http://localhost:8000/api/health/db

# 4. Regulatory data завантажена
python -c "from app.data.loader import RegulatoryDataLoader; print(RegulatoryDataLoader.get_summary_stats())"
```

**Очікуваний вивід:**
```json
{
  "regulatory_acts": 4,
  "mandatory_fields": 18,
  "critical_fields": 16,
  "warning_fields": 2,
  "forbidden_phrases": 52,
  "allowed_substances": 35
}
```

### Frontend Checklist

```bash
# 1. Homepage відкривається
open http://localhost:3000

# 2. Generator сторінка
open http://localhost:3000/generator

# 3. Checker сторінка
open http://localhost:3000/checker

# 4. TypeScript компілюється без помилок
npm run build
```

### Integration Test

**Тест перевірки дозування через API:**

```bash
curl -X POST http://localhost:8000/api/dosage/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": [
      {
        "name": "Вітамін C",
        "quantity": 80.0,
        "unit": "мг",
        "form": "аскорбінова кислота"
      }
    ]
  }'
```

**Очікувана відповідь:**

```json
{
  "success": true,
  "data": {
    "errors": [],
    "warnings": [],
    "all_valid": true,
    "total_ingredients_checked": 1
  }
}
```

✅ Якщо отримали таку відповідь - все працює!

---

## 🎯 Наступні кроки

### 1. Протестуйте основний функціонал

**Frontend:**
- [ ] Відкрийте генератор: http://localhost:3000/generator
- [ ] Заповніть форму (5 кроків)
- [ ] Відкрийте checker: http://localhost:3000/checker
- [ ] Спробуйте завантажити тестовий файл

**Backend:**
- [ ] Перегляньте API docs: http://localhost:8000/docs
- [ ] Спробуйте endpoints через Swagger UI
- [ ] Перевірте Claude AI integration

### 2. Додайте тестові дані

```bash
# Backend
cd backend
python scripts/seed_database.py
# Введіть 'n' якщо дані вже є

# Перевірте
python -c "from app.db.supabase_client import supabase_client; print(supabase_client.client.table('mandatory_fields').select('id', count='exact').execute())"
```

### 3. Налаштуйте IDE (VS Code)

**Рекомендовані розширення:**

Frontend:
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- TypeScript and JavaScript Language Features

Backend:
- Python
- Pylance
- Black Formatter
- autoDocstring

**VS Code Settings:**

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### 4. Git setup

```bash
cd "/Users/admin/Downloads/label check"

git init
git add .
git commit -m "Initial commit: Label Check project with full regulatory database"

# Додайте remote
git remote add origin https://github.com/your-username/label-check.git
git push -u origin main
```

---

## 🚢 Production Deployment

### Backend → Railway

```bash
cd backend
railway login
railway init
railway variables set CLAUDE_API_KEY=sk-ant-...
railway variables set SUPABASE_URL=https://xxx.supabase.co
railway variables set SUPABASE_KEY=eyJ...
railway up
```

✅ Backend URL: `https://your-app.railway.app`

### Frontend → Vercel

```bash
cd frontend
vercel login
vercel
# Додайте env variable:
vercel env add NEXT_PUBLIC_API_URL
# Введіть: https://your-app.railway.app/api
vercel --prod
```

✅ Frontend URL: `https://your-app.vercel.app`

### Post-deployment

1. **Оновіть CORS у backend:**
```bash
railway variables set ALLOWED_ORIGINS=https://your-app.vercel.app
```

2. **Seed production database:**
```bash
railway run python scripts/seed_database.py
```

3. **Тест production:**
```bash
curl https://your-app.railway.app/health
open https://your-app.vercel.app
```

---

## 🎓 Навчання

### Для розробників

1. **Next.js 14 Tutorial**: https://nextjs.org/learn
2. **FastAPI Tutorial**: https://fastapi.tiangolo.com/tutorial/
3. **Claude AI Docs**: https://docs.anthropic.com/claude/docs
4. **Supabase Quickstart**: https://supabase.com/docs/guides/getting-started

### Для користувачів

1. Відкрийте http://localhost:3000
2. Перейдіть до **Генератор**
3. Заповніть 5 кроків
4. Отримайте згенеровану етикетку
5. Або використовуйте **Перевірка** для валідації існуючої етикетки

---

## 📞 Допомога

### Якщо щось не працює:

1. **Перевірте логи:**
   - Backend: консоль де запущений uvicorn
   - Frontend: браузер console (F12)

2. **Перезапустіть сервіси:**
   ```bash
   # Backend
   Ctrl+C, потім: uvicorn app.main:app --reload
   
   # Frontend
   Ctrl+C, потім: npm run dev
   ```

3. **Очистіть кеші:**
   ```bash
   # Frontend
   rm -rf .next
   
   # Backend
   find . -type d -name __pycache__ -exec rm -rf {} +
   ```

4. **Перевірте порти:**
   ```bash
   lsof -i :8000  # Backend
   lsof -i :3000  # Frontend
   ```

### Контакти

- **GitHub Issues**: https://github.com/your-repo/issues
- **Email**: support@labelcheck.com
- **Documentation**: Див. README файли

---

## 🎉 Готово!

Тепер у вас є повністю функціональна система для:

✅ Генерації комплаєнтних етикеток  
✅ Валідації існуючих етикеток  
✅ Перевірки дозувань 35 речовин  
✅ Виявлення 52 заборонених фраз  
✅ Перевірки 18 обов'язкових полів  
✅ Розрахунку штрафів (640,000 / 62,600 грн)  
✅ Інтеграції з Claude AI для глибокого аналізу  

**Happy coding! 🇺🇦**

Made with ❤️ for Ukrainian dietary supplement manufacturers.

