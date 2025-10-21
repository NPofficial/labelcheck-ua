# Label Check - Backend API 🚀

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python)](https://www.python.org/)
[![Claude AI](https://img.shields.io/badge/Claude-3.5%20Sonnet-8B5CF6?style=flat)](https://www.anthropic.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=flat&logo=supabase)](https://supabase.com/)

Backend API для генерації та валідації етикеток дієтичних добавок з використанням Claude AI.

## 🚀 Швидкий старт

```bash
python -m venv venv && source venv/bin/activate  # Створення venv
pip install -r requirements.txt                   # Встановлення
python scripts/seed_database.py                   # Завантаження даних
uvicorn app.main:app --reload                     # Запуск
```

API буде доступний на http://localhost:8000  
Документація: http://localhost:8000/docs

## 📦 Встановлення

### Передумови

- **Python** 3.11 або вище
- **pip** 23.0 або вище
- **Supabase** account (безкоштовний план)
- **Anthropic API** key (Claude AI)

### Кроки встановлення

1. **Клонування репозиторію**

```bash
git clone <repository-url>
cd label-check/backend
```

2. **Створення virtual environment**

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

3. **Встановлення залежностей**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Налаштування environment variables**

```bash
cp .env.example .env
```

Відредагуйте `.env`:

```env
# Application
APP_NAME="Label Check API"
ENVIRONMENT="development"
DEBUG=True

# Claude AI
CLAUDE_API_KEY=sk-ant-api03-xxxxx

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGci...

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

5. **Налаштування Supabase database**

Див. розділ [Database Setup](#-database-setup)

6. **Завантаження нормативних даних**

```bash
python scripts/seed_database.py
```

Введіть `y` для очищення таблиць (при першому запуску).

7. **Запуск development server**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API доступний на http://localhost:8000

## 🗄️ Database Setup

### Створення таблиць у Supabase

**1. Перейдіть у Supabase Dashboard → SQL Editor**

**2. Створіть таблиці:**

#### Table: `mandatory_fields`

```sql
CREATE TABLE mandatory_fields (
  id SERIAL PRIMARY KEY,
  field_name TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL,
  regulatory_source TEXT NOT NULL,
  article TEXT NOT NULL,
  criticality TEXT NOT NULL CHECK (criticality IN ('critical', 'warning')),
  error_message TEXT NOT NULL,
  recommendation TEXT NOT NULL,
  penalty_amount INTEGER NOT NULL,
  search_patterns JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_mandatory_fields_criticality ON mandatory_fields(criticality);
CREATE INDEX idx_mandatory_fields_field_name ON mandatory_fields(field_name);
```

#### Table: `forbidden_phrases`

```sql
CREATE TABLE forbidden_phrases (
  id SERIAL PRIMARY KEY,
  phrase TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('treatment', 'disease', 'medical', 'veiled')),
  variations JSONB NOT NULL DEFAULT '[]'::jsonb,
  regulatory_source TEXT NOT NULL,
  article TEXT NOT NULL,
  explanation TEXT NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('critical', 'warning')),
  penalty_amount INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_forbidden_phrases_category ON forbidden_phrases(category);
CREATE INDEX idx_forbidden_phrases_severity ON forbidden_phrases(severity);
```

#### Table: `allowed_substances`

```sql
CREATE TABLE allowed_substances (
  id SERIAL PRIMARY KEY,
  substance_name TEXT NOT NULL,
  scientific_name TEXT NOT NULL,
  alternative_names JSONB NOT NULL DEFAULT '[]'::jsonb,
  category TEXT NOT NULL,
  max_daily_dose NUMERIC(10, 3) NOT NULL,
  unit TEXT NOT NULL,
  three_times_limit NUMERIC(10, 3) NOT NULL,
  allowed_forms JSONB NOT NULL DEFAULT '[]'::jsonb,
  regulatory_source TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_allowed_substances_category ON allowed_substances(category);
CREATE INDEX idx_allowed_substances_name ON allowed_substances(substance_name);
```

#### Table: `regulatory_acts`

```sql
CREATE TABLE regulatory_acts (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  number TEXT NOT NULL,
  date DATE NOT NULL,
  description TEXT NOT NULL,
  key_requirements JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**3. Завантажте дані:**

```bash
python scripts/seed_database.py
```

Вивід:
```
🗑️  Clear existing tables before seeding? (y/n): y
📋 Seeding mandatory_fields...
✅ Inserted 18 mandatory fields
❌ Seeding forbidden_phrases...
✅ Inserted 52 forbidden phrases
📊 Total records seeded: 109
```

## 🔐 Environment Variables

| Змінна | Опис | Приклад | Обов'язкова |
|--------|------|---------|-------------|
| `CLAUDE_API_KEY` | Anthropic Claude API key | `sk-ant-api03-...` | ✅ Так |
| `SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` | ✅ Так |
| `SUPABASE_KEY` | Supabase anon/service key | `eyJhbGci...` | ✅ Так |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000` | ✅ Так |
| `DEBUG` | Debug mode | `True` або `False` | Ні (default: True) |
| `MAX_FILE_SIZE` | Max upload size (bytes) | `10485760` (10MB) | Ні |
| `SMTP_HOST` | Email SMTP host | `smtp.gmail.com` | Ні |
| `SMTP_PORT` | Email SMTP port | `587` | Ні |

### Повний файл `.env`

```env
# Application
APP_NAME="Label Check API"
APP_VERSION="1.0.0"
ENVIRONMENT="development"
DEBUG=True
HOST="0.0.0.0"
PORT=8000

# API Keys
CLAUDE_API_KEY=sk-ant-api03-xxxxx

# Database (Supabase)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads

# Email Service (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=noreply@labelcheck.com
```

## 📁 Структура проєкту

```
backend/
├── app/
│   ├── main.py                       # FastAPI app (CORS, routes, middleware)
│   ├── config.py                     # Settings (Pydantic Settings)
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py             # GET /health
│   │   │   ├── generate.py           # POST /api/labels/generate
│   │   │   ├── check.py              # POST /api/labels/check
│   │   │   └── dosage.py             # POST /api/dosage/calculate
│   │   │
│   │   └── schemas/
│   │       ├── label.py              # ProductInfo, Ingredient, LabelData
│   │       ├── validation.py         # ValidationResult, DosageCheckResult
│   │       └── response.py           # APIResponse, LabelGenerateResponse
│   │
│   ├── services/                     # Business logic
│   │   ├── claude_service.py         # Claude AI client (16k+6k prompts)
│   │   ├── validation_service.py     # Label validation (52 phrases, 18 fields)
│   │   ├── generation_service.py     # Label generation (PDF/DOCX/PNG)
│   │   ├── dosage_service.py         # Dosage checking (35 substances)
│   │   ├── document_service.py       # OCR, PDF extraction
│   │   └── email_service.py          # SMTP notifications
│   │
│   ├── db/
│   │   ├── supabase_client.py        # Supabase singleton client
│   │   ├── models.py                 # Pydantic database models
│   │   └── queries.py                # Database query functions
│   │
│   ├── utils/
│   │   ├── image_processing.py       # Pillow, OCR
│   │   ├── pdf_processing.py         # PyPDF2 text extraction
│   │   └── text_processing.py        # Text cleaning, tokenization
│   │
│   ├── prompts/
│   │   ├── system_prompts.py         # Claude system prompts
│   │   └── validation_prompts.py     # Validation-specific prompts
│   │
│   └── data/
│       ├── loader.py                 # RegulatoryDataLoader (@lru_cache)
│       └── regulatory/               # Normative data (JSON)
│           ├── mandatory_fields.json       # 18 fields
│           ├── forbidden_phrases.json      # 52 phrases
│           ├── allowed_substances.json     # 35 substances
│           └── regulatory_acts.json        # 4 acts
│
├── scripts/
│   ├── seed_database.py              # Initial data seeding
│   └── update_regulations.py         # Update regulatory data
│
├── tests/
│   └── test_main.py
│
├── requirements.txt                  # Python dependencies
├── Dockerfile                        # Production Docker image
├── .env.example                      # Environment template
└── README.md                         # This file
```

## 🔧 Services

### 1. ClaudeService

**Файл:** `app/services/claude_service.py`

**Використання:**

```python
from app.services.claude_service import ClaudeService

service = ClaudeService()

# Generate text
result = await service.generate_text(
    prompt="Analyze this label: ...",
    system_prompt=LABEL_VALIDATION_SYSTEM_PROMPT,
    max_tokens=4096,
    temperature=0.7
)

# Analyze label
analysis = await service.analyze_label(label_text)
```

**Claude AI Configuration:**
- Model: `claude-3-5-sonnet-20241022`
- Max tokens: 4096
- Temperature: 0.7

### 2. ValidationService

**Файл:** `app/services/validation_service.py`

**Використання:**

```python
from app.services.validation_service import ValidationService

service = ValidationService()

result = await service.validate_label(label_text)

# result:
# {
#   "id": "uuid",
#   "is_valid": False,
#   "errors": [...],  # Critical errors (640k грн штраф)
#   "warnings": [...],  # Recommendations
#   "score": 6.5,  # 0-100
#   "validated_at": "2025-01-20T12:00:00Z"
# }
```

**Перевірки:**
- 18 обов'язкових полів
- 52 заборонені фрази (контекстуальний пошук через Claude)
- Формат та структура
- Алергени та застереження

### 3. DosageService

**Файл:** `app/services/dosage_service.py`

**Використання:**

```python
from app.services.dosage_service import DosageService

service = DosageService()

ingredients = [
    {
        "name": "Вітамін C",
        "quantity": 1000.0,
        "unit": "мг",
        "form": "аскорбінова кислота"
    }
]

result = await service.check_dosages(ingredients)

# result:
# {
#   "errors": [],  # Critical dosage violations
#   "warnings": [...],  # Exceeds recommended but within 3x
#   "all_valid": False,
#   "total_ingredients_checked": 1
# }
```

**Перевірки:**
- 35 дозволених речовин
- Максимальні добові дози
- Потрійні ліміти (критичний рівень)
- Дозволені форми речовин

### 4. GenerationService

**Файл:** `app/services/generation_service.py`

**Використання:**

```python
from app.services.generation_service import GenerationService

service = GenerationService()

result = await service.generate_label(label_request)

# Formats: PDF, DOCX, PNG
```

### 5. DocumentService

**Файл:** `app/services/document_service.py`

**Використання:**

```python
from app.services.document_service import DocumentService

service = DocumentService()

# Extract text from uploaded file
text = await service.extract_text(file)

# Supports: JPG, PNG, PDF
```

## 🤖 Claude AI Integration

### Промпти

**Validation Prompt:** 16,634 символів
- Повна нормативна база (18+52+35+4 items)
- Інструкції для Claude
- JSON структура відповіді

**Generation Prompt:** 6,426 символів
- Шаблон етикетки
- Заборонені фрази
- Обов'язкові розділи

**Приклад використання:**

```python
from app.prompts.system_prompts import (
    LABEL_VALIDATION_SYSTEM_PROMPT,
    LABEL_GENERATION_SYSTEM_PROMPT
)
from app.services.claude_service import ClaudeService

service = ClaudeService()

# Validation
response = await service.generate_text(
    prompt=f"Analyze this label:\n\n{label_text}",
    system_prompt=LABEL_VALIDATION_SYSTEM_PROMPT,
    max_tokens=4096
)

# Parse JSON response
import json
result = json.loads(response)
```

### Витрати Claude AI

| Операція | Input Tokens | Output Tokens | Вартість (орієнтовна) |
|----------|-------------|---------------|------------------------|
| Validation | ~18,000 | ~2,000 | $0.10 - $0.15 |
| Generation | ~8,000 | ~3,000 | $0.08 - $0.12 |
| Analysis | ~20,000 | ~1,500 | $0.12 - $0.18 |

**Ціни Claude 3.5 Sonnet:**
- Input: $3.00 per 1M tokens
- Output: $15.00 per 1M tokens

**Місячний бюджет (приблизно):**
- 100 перевірок: ~$10-15
- 1000 перевірок: ~$100-150

## 🌐 API Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "healthy",
  "app": "Label Check API",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2025-01-20T12:00:00Z"
}
```

**HTTP Example:**

```bash
curl http://localhost:8000/health
```

---

### 2. Generate Label

**Endpoint:** `POST /api/labels/generate`

**Request Body:**

```json
{
  "product_info": {
    "name": "Вітамін C",
    "manufacturer": "ТОВ 'Компанія'",
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
  "dosages": [
    {
      "population": "Дорослі",
      "instruction": "По 1 таблетці",
      "frequency": "2 рази на день",
      "duration": "30 днів"
    }
  ],
  "warnings": [
    {
      "type": "contraindication",
      "severity": "high",
      "description": "Не застосовувати при алергії"
    }
  ],
  "operator_info": {
    "name": "ТОВ 'Виробник'",
    "license_number": "UA-123456",
    "production_date": "2025-01-01",
    "expiry_date": "2027-01-01",
    "batch_number": "BATCH-001"
  },
  "format": "pdf"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "label_text": "ДІЄТИЧНА ДОБАВКА\n\nВітамін C 500 мг...",
    "validation_status": "passed",
    "warnings": [],
    "metadata": {
      "total_ingredients": 1,
      "has_allergens": false,
      "allergen_list": [],
      "daily_dose_count": 2
    }
  }
}
```

**HTTP Example:**

```bash
curl -X POST http://localhost:8000/api/labels/generate \
  -H "Content-Type: application/json" \
  -d '{
    "product_info": {"name": "Вітамін C", "manufacturer": "ТОВ", "dosage_form": "Таблетки", "strength": "500 мг"},
    "ingredients": [{"name": "Аскорбінова кислота", "quantity": "500", "unit": "мг", "is_active": true}],
    "dosages": [],
    "warnings": [],
    "operator_info": {"name": "ТОВ", "license_number": "UA-123", "production_date": "2025-01-01", "expiry_date": "2027-01-01", "batch_number": "001"}
  }'
```

---

### 3. Check Label

**Endpoint:** `POST /api/labels/check`

**Request (File Upload):**

```bash
curl -X POST http://localhost:8000/api/labels/check \
  -F "file=@label.jpg"
```

**Request (Text):**

```bash
curl -X POST http://localhost:8000/api/labels/check \
  -F "text=ДІЄТИЧНА ДОБАВКА\n\nВітамін C 500 мг..."
```

**Response:**

```json
{
  "success": true,
  "data": {
    "critical_errors": [
      {
        "error_id": "ERR_001",
        "category": "forbidden_phrase",
        "title": "Заборонена фраза про лікування",
        "found_text": "лікує діабет",
        "regulatory_source": "Наказ МОЗ №1114, п.3.2-3.4",
        "article": "п.3.2-3.4",
        "explanation": "Дієтичні добавки не можуть лікувати захворювання згідно українського законодавства",
        "recommendation": "Замініть 'лікує діабет' на 'підтримує нормальний рівень глюкози в крові'",
        "penalty_amount": 640000
      }
    ],
    "warnings": [],
    "correct_items": [
      "Правильно вказано код ЄДРПОУ: 12345678",
      "Присутнє застереження про зберігання від дітей"
    ],
    "overall_score": 6.5,
    "risk_level": "high",
    "total_potential_fines": 640000,
    "regulatory_acts_used": ["Наказ МОЗ №1114"]
  }
}
```

---

### 4. Calculate Dosage

**Endpoint:** `POST /api/dosage/calculate`

**Request Body:**

```json
{
  "ingredients": [
    {
      "name": "Вітамін C",
      "quantity": 1000.0,
      "unit": "мг",
      "form": "аскорбінова кислота"
    },
    {
      "name": "Цинк",
      "quantity": 15.0,
      "unit": "мг",
      "form": "цинк цитрат"
    }
  ]
}
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
        "regulatory_source": "Наказ МОЗ №1114, Додаток 1",
        "recommendation": "НЕГАЙНО зменшіть дозування до 80.0 мг або нижче",
        "penalty_amount": 640000
      }
    ],
    "warnings": [
      {
        "ingredient": "Цинк",
        "message": "Дозування перевищує рекомендовану добову норму",
        "current_dose": "15.0 мг",
        "max_allowed": "10.0 мг",
        "recommendation": "Рекомендується зменшити дозування до 10.0 мг"
      }
    ],
    "all_valid": false,
    "total_ingredients_checked": 2,
    "substances_not_found": 0
  }
}
```

**HTTP Example:**

```bash
curl -X POST http://localhost:8000/api/dosage/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": [
      {"name": "Вітамін C", "quantity": 1000.0, "unit": "мг", "form": "аскорбінова кислота"}
    ]
  }'
```

## 🚀 Deployment

### Railway (рекомендовано)

1. **Встановлення Railway CLI**

```bash
npm install -g @railway/cli
railway login
```

2. **Ініціалізація проєкту**

```bash
railway init
```

3. **Додавання environment variables**

```bash
railway variables set CLAUDE_API_KEY=sk-ant-...
railway variables set SUPABASE_URL=https://xxx.supabase.co
railway variables set SUPABASE_KEY=eyJ...
railway variables set ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

4. **Deploy**

```bash
railway up
```

5. **Перегляд логів**

```bash
railway logs
```

### Render

1. **Підключення GitHub repo** через Dashboard

2. **Build Settings**

```
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

3. **Environment Variables** у Dashboard:

```
CLAUDE_API_KEY=sk-ant-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

4. **Deploy** автоматично при push

### Docker

**Build:**

```bash
docker build -t label-check-backend .
```

**Run:**

```bash
docker run -d -p 8000:8000 \
  -e CLAUDE_API_KEY=sk-ant-... \
  -e SUPABASE_URL=https://xxx.supabase.co \
  -e SUPABASE_KEY=eyJ... \
  -e ALLOWED_ORIGINS=http://localhost:3000 \
  label-check-backend
```

**Docker Compose:**

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - ALLOWED_ORIGINS=http://localhost:3000
    volumes:
      - ./uploads:/app/uploads
```

```bash
docker-compose up
```

## 🐛 Troubleshooting

### 1. `ModuleNotFoundError: No module named 'app'`

**Причина:** Python не бачить app module

**Рішення:**

```bash
# Встановіть PYTHONPATH
export PYTHONPATH=/path/to/backend:$PYTHONPATH

# Або запускайте з кореня backend
cd backend
python -m uvicorn app.main:app
```

### 2. `supabase_client connection failed`

**Причина:** Неправильні Supabase credentials

**Рішення:**

1. Перевірте `.env`:
```env
SUPABASE_URL=https://xxxxx.supabase.co  # Без "/" в кінці
SUPABASE_KEY=eyJhbGci...  # Anon key або Service key
```

2. Тест з'єднання:
```python
from app.db.supabase_client import SupabaseClient
client = SupabaseClient()
result = client.client.table("mandatory_fields").select("*").limit(1).execute()
print(result.data)
```

### 3. `anthropic.AuthenticationError`

**Причина:** Неправильний Claude API key

**Рішення:**

1. Перевірте `.env`:
```env
CLAUDE_API_KEY=sk-ant-api03-...  # Має починатися з sk-ant-
```

2. Перевірте баланс на https://console.anthropic.com/

3. Тест API:
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $CLAUDE_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-3-5-sonnet-20241022", "max_tokens": 10, "messages": [{"role": "user", "content": "Hi"}]}'
```

### 4. `CORS policy` error у frontend

**Причина:** Backend не дозволяє frontend origin

**Рішення:**

```env
# .env
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
```

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. `Failed to load regulatory data`

**Причина:** JSON файли не знайдені або пошкоджені

**Рішення:**

```bash
# Перевірте наявність файлів
ls -la app/data/regulatory/

# Перевірте валідність JSON
python -m json.tool app/data/regulatory/mandatory_fields.json

# Перезавантажте кеш
python -c "from app.data.loader import RegulatoryDataLoader; RegulatoryDataLoader.clear_cache()"
```

### 6. `Table does not exist` у Supabase

**Причина:** Таблиці не створені

**Рішення:**

1. Створіть таблиці через SQL Editor (див. [Database Setup](#-database-setup))
2. Або через `psql`:
```bash
psql postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres < schema.sql
```

### 7. `File upload fails` з 413 Request Entity Too Large

**Причина:** Файл перевищує MAX_FILE_SIZE

**Рішення:**

```env
# .env
MAX_FILE_SIZE=20971520  # 20MB
```

```python
# app/config.py
max_file_size: int = Field(default=20971520, alias="MAX_FILE_SIZE")
```

## 💻 Корисні команди

```bash
# Development
uvicorn app.main:app --reload              # Dev server з auto-reload
uvicorn app.main:app --reload --log-level debug  # З debug логами

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Database
python scripts/seed_database.py            # Seed initial data
python scripts/update_regulations.py       # Update regulatory data

# Testing
pytest                                     # Run all tests
pytest --cov=app tests/                    # With coverage
pytest -v tests/test_main.py               # Specific test

# Code Quality
black app/                                 # Format code
flake8 app/                                # Lint code
mypy app/                                  # Type check

# Dependencies
pip list --outdated                        # Check outdated packages
pip install -U package_name                # Update specific package

# Debugging
python -m pdb app/main.py                  # Python debugger
python -c "from app.data.loader import RegulatoryDataLoader; print(RegulatoryDataLoader.get_summary_stats())"

# Logs
tail -f logs/app.log                       # Follow logs (якщо налаштовано)
```

## 📚 Документація

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [Python 3.11](https://docs.python.org/3.11/)
- [ReportLab](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [python-docx](https://python-docx.readthedocs.io/)

## 🔗 Посилання

- **Frontend**: [../frontend/README.md](../frontend/README.md)
- **Main README**: [../README.md](../README.md)
- **Scripts**: [./scripts/README.md](./scripts/README.md)
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

## 📝 Ліцензія

© 2025 Label Check. Всі права захищені.

---

**Need help?** Відкрийте issue або напишіть на support@labelcheck.com
