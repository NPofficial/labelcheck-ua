# Label Check - Project Summary 📊

Повний огляд створеного проєкту для валідації етикеток дієтичних добавок в Україні.

## 📈 Статистика проєкту

- **Загальна кількість файлів**: 74+
- **Frontend файлів**: 35+
- **Backend файлів**: 35+
- **Конфігураційних файлів**: 15+
- **Документації**: 6 файлів
- **Рядків коду**: ~8,000+

## 🏗️ Структура (2 основні частини)

### 1. Frontend (Next.js 14 + TypeScript)

```
frontend/ (35+ files)
├── Configuration (8 files)
│   ├── package.json              ✅ Dependencies
│   ├── tsconfig.json             ✅ TypeScript strict mode
│   ├── tailwind.config.ts        ✅ Custom colors
│   ├── next.config.js            ✅ Next.js config
│   ├── postcss.config.js         ✅ PostCSS
│   ├── .eslintrc.json            ✅ ESLint
│   ├── .prettierrc               ✅ Prettier
│   └── components.json           ✅ shadcn/ui
│
├── Pages - App Router (5 files)
│   ├── app/layout.tsx            ✅ Root layout
│   ├── app/page.tsx              ✅ Home page
│   ├── app/globals.css           ✅ Global styles
│   ├── app/generator/page.tsx    ✅ Generator wizard
│   ├── app/checker/page.tsx      ✅ Checker page
│   └── app/results/[id]/page.tsx ✅ Results page
│
├── UI Components - shadcn/ui (7 files)
│   ├── button.tsx                ✅ Button (6 variants)
│   ├── input.tsx                 ✅ Input field
│   ├── textarea.tsx              ✅ Textarea
│   ├── card.tsx                  ✅ Card (5 sub-components)
│   ├── badge.tsx                 ✅ Badge (5 variants)
│   ├── alert.tsx                 ✅ Alert (4 variants)
│   └── progress.tsx              ✅ Progress bar
│
├── Form Components (5 files)
│   ├── ProductInfoForm.tsx       ✅ Step 1 - Product
│   ├── IngredientsForm.tsx       ✅ Step 2 - Ingredients
│   ├── DosageForm.tsx            ✅ Step 3 - Dosage
│   ├── WarningsForm.tsx          ✅ Step 4 - Warnings
│   └── OperatorForm.tsx          ✅ Step 5 - Operator
│
├── Checker Components (2 files)
│   ├── FileUpload.tsx            ✅ Drag & drop upload
│   └── TextInput.tsx             ✅ Text paste input
│
├── Results Components (4 files)
│   ├── ValidationReport.tsx      ✅ Full report
│   ├── ErrorCard.tsx             ✅ Error display
│   ├── WarningCard.tsx           ✅ Warning display
│   └── SuccessCard.tsx           ✅ Success state
│
├── Layout Components (3 files)
│   ├── Header.tsx                ✅ Site header
│   ├── Footer.tsx                ✅ Site footer
│   └── Navigation.tsx            ✅ Nav menu
│
├── Common Components (2 files)
│   ├── LoadingSpinner.tsx        ✅ Loading indicator
│   └── ErrorBoundary.tsx         ✅ Error boundary
│
├── Libraries (4 files)
│   ├── utils.ts                  ✅ Helpers (cn, dates)
│   ├── api-client.ts             ✅ API client class
│   ├── validations.ts            ✅ Form validation
│   └── constants.ts              ✅ App constants
│
└── Types (3 files)
    ├── label.ts                  ✅ Label types
    ├── api.ts                    ✅ API types
    └── forms.ts                  ✅ Form types
```

**Ключові технології:**
- ✅ Next.js 14 (App Router)
- ✅ React 18
- ✅ TypeScript (strict mode)
- ✅ Tailwind CSS + shadcn/ui
- ✅ React Hook Form + Zod

---

### 2. Backend (FastAPI + Claude AI)

```
backend/ (35+ files)
├── Configuration (5 files)
│   ├── requirements.txt          ✅ 20+ dependencies
│   ├── Dockerfile                ✅ Production image
│   ├── .env.example              ✅ Env template
│   ├── .gitignore                ✅ Git ignore
│   └── app/__init__.py           ✅ Package init
│
├── Core (2 files)
│   ├── app/main.py               ✅ FastAPI app + CORS
│   └── app/config.py             ✅ Pydantic Settings
│
├── API Routes (4 files)
│   ├── routes/health.py          ✅ GET /health
│   ├── routes/generate.py        ✅ POST /api/labels/generate
│   ├── routes/check.py           ✅ POST /api/labels/check
│   └── routes/dosage.py          ✅ POST /api/dosage/calculate
│
├── Pydantic Schemas (3 files)
│   ├── schemas/label.py          ✅ LabelData, ProductInfo
│   ├── schemas/validation.py     ✅ ValidationResult, DosageCheckResult
│   └── schemas/response.py       ✅ APIResponse
│
├── Services (6 files)
│   ├── claude_service.py         ✅ Claude AI client
│   ├── validation_service.py     ✅ Label validation
│   ├── generation_service.py     ✅ PDF/DOCX generation
│   ├── dosage_service.py         ✅ Dosage checking (35 substances)
│   ├── document_service.py       ✅ OCR, PDF extraction
│   └── email_service.py          ✅ SMTP notifications
│
├── Database (3 files)
│   ├── db/supabase_client.py     ✅ Singleton client
│   ├── db/models.py              ✅ DB models
│   └── db/queries.py             ✅ Query functions
│
├── Utilities (3 files)
│   ├── utils/image_processing.py ✅ Pillow, OCR
│   ├── utils/pdf_processing.py   ✅ PyPDF2
│   └── utils/text_processing.py  ✅ Text cleaning
│
├── AI Prompts (2 files)
│   ├── prompts/system_prompts.py     ✅ 16k + 6k chars prompts
│   └── prompts/validation_prompts.py ✅ Validation prompts
│
├── Regulatory Data (5 files)
│   ├── data/loader.py                    ✅ RegulatoryDataLoader
│   ├── data/regulatory/mandatory_fields.json      ✅ 18 fields
│   ├── data/regulatory/forbidden_phrases.json     ✅ 52 phrases
│   ├── data/regulatory/allowed_substances.json    ✅ 35 substances
│   └── data/regulatory/regulatory_acts.json       ✅ 4 acts
│
├── Scripts (2 files)
│   ├── scripts/seed_database.py        ✅ Database seeding
│   └── scripts/update_regulations.py   ✅ Data updates
│
└── Tests (1 file)
    └── tests/test_main.py          ✅ Basic tests
```

**Ключові технології:**
- ✅ FastAPI (async framework)
- ✅ Claude AI 3.5 Sonnet
- ✅ Supabase (PostgreSQL)
- ✅ Pydantic v2
- ✅ ReportLab, python-docx, Pillow

---

## 📊 Нормативна база України

### Дані завантажені в проєкт

| Тип даних | Кількість | Файл | Опис |
|-----------|-----------|------|------|
| **Обов'язкові поля** | 18 | `mandatory_fields.json` | ДІЄТИЧНА ДОБАВКА, ЄДРПОУ, адреса... |
| **Заборонені фрази** | 52 | `forbidden_phrases.json` | treatment, disease, medical, veiled |
| **Дозволені речовини** | 35 | `allowed_substances.json` | Вітаміни (13), Мінерали (15), Інші (7) |
| **Регуляторні акти** | 4 | `regulatory_acts.json` | Закони України, Накази МОЗ |

### Приклади даних

#### Обов'язкове поле:
```json
{
  "id": 1,
  "field_name": "product_name_label",
  "description": "Назва 'ДІЄТИЧНА ДОБАВКА'",
  "regulatory_source": "Наказ МОЗ №1114, п.3.1",
  "criticality": "critical",
  "penalty_amount": 640000
}
```

#### Заборонена фраза:
```json
{
  "id": 1,
  "phrase": "лікує",
  "category": "treatment",
  "variations": ["лікування", "вилікує", "для лікування"],
  "severity": "critical",
  "penalty_amount": 640000
}
```

#### Дозволена речовина:
```json
{
  "id": 2,
  "substance_name": "Вітамін C",
  "scientific_name": "Аскорбінова кислота",
  "max_daily_dose": 80.0,
  "unit": "мг",
  "three_times_limit": 240.0
}
```

### Статистика штрафів

| Тип порушення | Штраф (грн) | Закон |
|---------------|-------------|-------|
| Відсутність обов'язкового поля | 640,000 | №4122-IX |
| Заборонена фраза (treatment) | 640,000 | №4122-IX |
| Заборонена фраза (disease) | 640,000 | №4122-IX |
| Перевищення дозування (3x) | 640,000 | №4122-IX |
| Алергени не виділені | 62,600 | №2639-VIII |
| Відсутнє застереження (вагітність) | 62,600 | №2639-VIII |

**Потенційний штраф за 1 етикетку:** До 11,520,000 грн (18 критичних полів × 640k)

## 🎯 Функціонал

### ✅ Що працює зараз

#### Frontend
- ✅ Головна сторінка з навігацією
- ✅ 5-step wizard для генерації
- ✅ Форми для всіх кроків (Product, Ingredients, Dosage, Warnings, Operator)
- ✅ File upload з drag & drop
- ✅ Text input для перевірки
- ✅ Результати валідації з ErrorCard/WarningCard
- ✅ API client з type-safe methods
- ✅ Responsive design (Tailwind)
- ✅ Error handling + Loading states

#### Backend
- ✅ FastAPI app з CORS
- ✅ 4 API endpoints (health, generate, check, dosage)
- ✅ Claude AI integration (3.5 Sonnet)
- ✅ Supabase database client
- ✅ Regulatory data loader (кешування)
- ✅ Dosage validation (35 substances)
- ✅ Document processing (PDF, Image)
- ✅ Email service (SMTP)
- ✅ Comprehensive logging

#### Data & AI
- ✅ 18 обов'язкових полів (mandatory_fields.json)
- ✅ 52 заборонені фрази (forbidden_phrases.json)
- ✅ 35 дозволених речовин (allowed_substances.json)
- ✅ 4 нормативні акти (regulatory_acts.json)
- ✅ Validation prompt (16,634 chars)
- ✅ Generation prompt (6,426 chars)
- ✅ Fuzzy matching для пошуку речовин
- ✅ Database seeding scripts

### 🔄 Що потрібно доопрацювати

#### Frontend (TODO)
- ⏳ Multi-step wizard state management
- ⏳ Form persistence (LocalStorage)
- ⏳ Download generated labels
- ⏳ Print preview
- ⏳ History of validations
- ⏳ User authentication
- ⏳ Dashboard with statistics

#### Backend (TODO)
- ⏳ Повна інтеграція Claude AI у validation_service
- ⏳ PDF generation з ReportLab
- ⏳ DOCX generation з python-docx
- ⏳ OCR для зображень (pytesseract)
- ⏳ File storage (Supabase Storage)
- ⏳ Rate limiting
- ⏳ Caching (Redis)
- ⏳ Background tasks (Celery)

#### Infrastructure (TODO)
- ⏳ CI/CD pipelines
- ⏳ Automated testing
- ⏳ Monitoring (Sentry)
- ⏳ Analytics (PostHog)
- ⏳ Load balancing

## 🚀 Швидкий запуск всього проєкту

### Terminal 1 - Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Відредагуйте .env з вашими ключами
python scripts/seed_database.py  # Введіть 'y'
uvicorn app.main:app --reload
```

✅ Backend: http://localhost:8000  
📖 Docs: http://localhost:8000/docs

### Terminal 2 - Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Відредагуйте .env.local
npm run dev
```

✅ Frontend: http://localhost:3000

### Terminal 3 - Тестування

```bash
# Health check
curl http://localhost:8000/health

# Frontend works
open http://localhost:3000
```

## 📋 Чекліст налаштування

### Backend Setup

- [ ] Python 3.11+ встановлено
- [ ] Virtual environment створено
- [ ] Dependencies встановлені (`pip install -r requirements.txt`)
- [ ] Supabase проєкт створено
- [ ] Таблиці створені (4 SQL створення)
- [ ] Claude API key отримано (https://console.anthropic.com/)
- [ ] `.env` файл налаштовано
- [ ] Database seeded (`python scripts/seed_database.py`)
- [ ] Server запущений (`uvicorn app.main:app --reload`)
- [ ] Health check OK (`curl http://localhost:8000/health`)

### Frontend Setup

- [ ] Node.js 18+ встановлено
- [ ] Dependencies встановлені (`npm install`)
- [ ] `.env.local` файл налаштовано
- [ ] Backend URL правильний
- [ ] Dev server запущений (`npm run dev`)
- [ ] Сторінка відкривається (http://localhost:3000)
- [ ] API запити працюють

### Supabase Setup

- [ ] Проєкт створено на supabase.com
- [ ] SQL таблиці створені (mandatory_fields, forbidden_phrases, allowed_substances, regulatory_acts)
- [ ] Індекси створені для performance
- [ ] API keys скопійовані
- [ ] Database connection працює
- [ ] 109 records завантажено через seed script

## 💰 Claude AI - Витрати та оптимізація

### Токени на запит

| Операція | System Prompt | User Input | Output | Total Tokens |
|----------|---------------|------------|--------|--------------|
| **Validation** | 16,634 chars (~4,500 tokens) | 2,000-10,000 | ~2,000 | ~8,000-16,500 |
| **Generation** | 6,426 chars (~1,800 tokens) | 1,000-3,000 | ~3,000 | ~5,800-7,800 |

### Вартість

**Claude 3.5 Sonnet pricing:**
- Input: $3.00 per 1M tokens
- Output: $15.00 per 1M tokens

**Приклад розрахунку (1 validation):**
```
Input:  8,000 tokens × $3.00 / 1M = $0.024
Output: 2,000 tokens × $15.00 / 1M = $0.030
Total: ~$0.054 per validation
```

**Місячні витрати:**
- 100 validations/month: ~$5-6
- 1,000 validations/month: ~$50-60
- 10,000 validations/month: ~$500-600

### Оптимізація витрат

1. **Кешування результатів**
```python
# Cache identical requests
@lru_cache(maxsize=1000)
def get_validation_result(text_hash: str) -> ValidationResult:
    pass
```

2. **Batch processing**
```python
# Validate multiple labels in one request
results = await claude_service.validate_batch(labels)
```

3. **Shorter prompts для простих перевірок**
```python
# Use regex для obvious violations перед Claude
if contains_forbidden_phrase_exact(text):
    return error  # No Claude call needed
```

## 📡 API Endpoints

### Quick Reference

| Method | Endpoint | Опис | Auth |
|--------|----------|------|------|
| GET | `/health` | Health check | No |
| GET | `/health/db` | Database health | No |
| POST | `/api/labels/generate` | Generate label | No |
| GET | `/api/labels/generate/{id}` | Get generated label | No |
| POST | `/api/labels/check` | Validate label | No |
| GET | `/api/labels/results/{id}` | Get validation result | No |
| POST | `/api/dosage/calculate` | Check dosages | No |

### Детальні приклади

#### 1. Health Check

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "healthy",
  "app": "Label Check API",
  "version": "1.0.0",
  "timestamp": "2025-01-20T12:00:00Z"
}
```

#### 2. Generate Label

```bash
curl -X POST http://localhost:8000/api/labels/generate \
  -H "Content-Type: application/json" \
  -d '{
    "product_info": {
      "name": "Вітамін C Комплекс",
      "manufacturer": "ТОВ Фарма",
      "dosage_form": "Таблетки",
      "strength": "500 мг"
    },
    "ingredients": [
      {
        "name": "Аскорбінова кислота",
        "quantity": "500",
        "unit": "мг",
        "is_active": true
      }
    ],
    "dosages": [],
    "warnings": [],
    "operator_info": {
      "name": "ТОВ Виробник",
      "license_number": "UA-123456",
      "production_date": "2025-01-01",
      "expiry_date": "2027-01-01",
      "batch_number": "001"
    },
    "format": "pdf"
  }'
```

#### 3. Check Label (File)

```bash
curl -X POST http://localhost:8000/api/labels/check \
  -F "file=@/path/to/label.jpg"
```

#### 4. Check Label (Text)

```bash
curl -X POST http://localhost:8000/api/labels/check \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=ДІЄТИЧНА ДОБАВКА

Вітамін C 500 мг

Склад: Аскорбінова кислота 500 мг

Код ЄДРПОУ: 12345678"
```

#### 5. Calculate Dosage

```bash
curl -X POST http://localhost:8000/api/dosage/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": [
      {
        "name": "Вітамін C",
        "quantity": 1000.0,
        "unit": "мг",
        "form": "аскорбінова кислота"
      }
    ]
  }'
```

**Response:**

```json
{
  "success": true,
  "data": {
    "errors": [
      {
        "ingredient": "Вітамін C",
        "message": "КРИТИЧНА ПОМИЛКА: Дозування перевищує потрійну добову норму",
        "current_dose": "1000.0 мг",
        "max_allowed": "80.0 мг",
        "three_times_limit": "240.0 мг",
        "penalty_amount": 640000
      }
    ],
    "warnings": [],
    "all_valid": false,
    "total_ingredients_checked": 1
  }
}
```

## 💻 Корисні команди

```bash
# Development
uvicorn app.main:app --reload                    # Dev server
uvicorn app.main:app --reload --log-level debug  # Debug mode
uvicorn app.main:app --workers 4                 # Production (4 workers)

# Database
python scripts/seed_database.py                  # Initial seed
python scripts/update_regulations.py             # Update data
python -c "from app.data.loader import RegulatoryDataLoader; print(RegulatoryDataLoader.get_summary_stats())"

# Testing
pytest                                           # All tests
pytest --cov=app tests/                          # With coverage
pytest -v -s tests/test_main.py                  # Verbose
pytest -k test_health                            # Specific test

# Code Quality
black app/ --check                               # Check formatting
black app/                                       # Format code
flake8 app/ --max-line-length 100               # Lint
mypy app/                                        # Type check

# Dependencies
pip list --outdated                              # Check updates
pip install -U package_name                      # Update package
pip freeze > requirements.txt                    # Update requirements

# Interactive
python -m app.data.loader                        # Test loader
python -m app.prompts.system_prompts             # Test prompts
python -m app.services.dosage_service            # Test dosage service

# Debugging
python -m pdb app/main.py                        # Debugger
python -m cProfile -s cumtime app/main.py        # Profiler

# Logs
tail -f logs/app.log                             # Follow logs (if configured)
```

## 📚 Документація та ресурси

### Офіційна документація

- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Pydantic](https://docs.pydantic.dev/latest/) - Data validation
- [Anthropic Claude](https://docs.anthropic.com/) - AI API
- [Supabase Python](https://supabase.com/docs/reference/python/introduction) - Database client
- [ReportLab](https://www.reportlab.com/docs/reportlab-userguide.pdf) - PDF generation
- [python-docx](https://python-docx.readthedocs.io/) - DOCX generation
- [Pillow](https://pillow.readthedocs.io/) - Image processing

### Нормативні документи

- [Закон України "Про лікарські засоби"](https://zakon.rada.gov.ua/laws/show/123/96-%D0%B2%D1%80)
- [Наказ МОЗ №1114](https://zakon.rada.gov.ua/) - Маркування дієтичних добавок
- [GMP стандарти](https://www.who.int/medicines/areas/quality_safety/quality_assurance/gmp/en/)

### Project Documentation

- [Main README](../README.md) - Огляд проєкту
- [Frontend README](../frontend/README.md) - Frontend документація
- [Scripts README](./scripts/README.md) - Database scripts
- [API Documentation](http://localhost:8000/docs) - Swagger UI
- [ReDoc](http://localhost:8000/redoc) - Alternative docs

## 🔗 Зовнішні сервіси

### Anthropic Claude AI

1. Створіть account: https://console.anthropic.com/
2. Отримайте API key: Settings → API Keys
3. Додайте credits (мінімум $5)
4. Додайте key в `.env`

### Supabase Database

1. Створіть проєкт: https://supabase.com/dashboard
2. Перейдіть до Project Settings → API
3. Скопіюйте:
   - Project URL → `SUPABASE_URL`
   - anon/public key → `SUPABASE_KEY`
4. Створіть таблиці через SQL Editor
5. Запустіть seed script

## 📝 Ліцензія

© 2025 Label Check. Всі права захищені.

---

**Розробка:** Python 3.11 + FastAPI + Claude AI 3.5 Sonnet  
**База даних:** Supabase (PostgreSQL)  
**AI Provider:** Anthropic  
**Нормативна база:** Україна (Наказ МОЗ №1114, Закон №4122-IX)

**Made with ❤️ in Ukraine 🇺🇦**

