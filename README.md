# Label Check 🇺🇦

Система генерації та перевірки етикеток дієтичних добавок згідно з законодавством України.

[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688)](https://fastapi.tiangolo.com/)
[![Claude AI](https://img.shields.io/badge/Claude-3.5%20Sonnet-8B5CF6)](https://www.anthropic.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB)](https://www.python.org/)

## 📋 Зміст

- [Огляд](#огляд)
- [Структура проєкту](#структура-проєкту)
- [Швидкий старт](#швидкий-старт)
- [Нормативна база](#нормативна-база)
- [Технології](#технології)
- [Функціонал](#функціонал)
- [Deployment](#deployment)
- [Ліцензія](#ліцензія)

## 🎯 Огляд

**Label Check** - це професійна система для виробників та імпортерів дієтичних добавок в Україні, яка:

- ✅ **Генерує** комплаєнтні етикетки згідно Наказу МОЗ №1114
- 🔍 **Перевіряє** існуючі етикетки на відповідність законодавству
- ⚖️ **Виявляє** порушення з точними посиланнями на закони
- 💊 **Валідує** дозування 35 дозволених речовин
- 💰 **Розраховує** потенційні штрафи (до 640,000 грн за порушення)
- 🤖 **Використовує** Claude AI для глибокого аналізу завуальованих тверджень

### Чому це важливо?

- **Штрафи**: від 62,600 до 640,000 грн за кожне порушення (Закон №4122-IX)
- **Регуляція**: Суворі вимоги МОЗ України до маркування
- **Заборони**: 52+ заборонених фраз про "лікування" та "діагностику"
- **Безпека**: Контроль дозувань, форм речовин, алергенів

## 📂 Структура проєкту

```
label-check/
├── frontend/              # Next.js 14 (App Router)
│   ├── src/app/          # Pages (generator, checker, results)
│   ├── src/components/   # React components
│   ├── src/lib/          # API client, utilities
│   └── src/types/        # TypeScript types
│
├── backend/               # FastAPI + Claude AI
│   ├── app/api/          # API routes
│   ├── app/services/     # Business logic
│   ├── app/data/         # Regulatory data (18+52+35+4 items)
│   ├── app/db/           # Supabase integration
│   └── scripts/          # Database seeding
│
└── README.md             # Ця документація
```

## 🚀 Швидкий старт

### Передумови

- **Node.js** 18+ (для frontend)
- **Python** 3.11+ (для backend)
- **Supabase** account (безкоштовно)
- **Anthropic API** key (Claude AI)

### 1. Клонування репозиторію

```bash
git clone <repository-url>
cd label-check
```

### 2. Frontend setup

```bash
cd frontend

# Встановлення залежностей
npm install

# Конфігурація
cp .env.local.example .env.local
# Відредагуйте .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Запуск
npm run dev
```

Frontend буде доступний на http://localhost:3000

### 3. Backend setup

```bash
cd backend

# Створення virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# або
venv\Scripts\activate     # Windows

# Встановлення залежностей
pip install -r requirements.txt

# Конфігурація
cp .env.example .env
# Відредагуйте .env:
# CLAUDE_API_KEY=sk-ant-...
# SUPABASE_URL=https://xxx.supabase.co
# SUPABASE_KEY=eyJ...

# Seed database (завантаження нормативних даних)
python scripts/seed_database.py

# Запуск
uvicorn app.main:app --reload
```

Backend буде доступний на http://localhost:8000

API документація: http://localhost:8000/docs

### 4. Перевірка

```bash
# Health check
curl http://localhost:8000/api/health

# Frontend
open http://localhost:3000
```

## 📜 Нормативна база

Система містить повну нормативну базу України для дієтичних добавок:

### 18 Обов'язкових полів (`mandatory_fields.json`)

| Поле | Опис | Штраф |
|------|------|-------|
| product_name_label | Назва "ДІЄТИЧНА ДОБАВКА" | 640,000 грн |
| edrpou_code | Код ЄДРПОУ (8 цифр) | 640,000 грн |
| operator_full_address | Повна адреса з індексом | 640,000 грн |
| ingredients_list | Повний перелік інгредієнтів | 640,000 грн |
| not_medicinal_product | "Не є лікарським засобом" | 640,000 грн |
| ... | +13 інших полів | 640,000 / 62,600 грн |

### 52 Заборонені фрази (`forbidden_phrases.json`)

Категорії:
- **Treatment** (10): лікує, зцілює, терапія, виліковує...
- **Disease** (20): діабет, рак, гіпертонія, артрит...
- **Medical** (10): клінічно доведено, діагностика, замінює ліки...
- **Veiled** (12): допомагає при, боротьба з, усуває симптоми...

Всі фрази: **640,000 грн штраф**

### 35 Дозволених речовин (`allowed_substances.json`)

- **Вітаміни** (13): A, C, D, E, B1-B12, K
- **Мінерали** (15): Цинк, Магній, Кальцій, Залізо, Селен...
- **Інші** (7): Омега-3, CoQ10, L-карнітин, Глюкозамін...

Для кожної речовини:
- Максимальна добова доза
- Потрійний ліміт (критичний рівень)
- Дозволені форми
- Одиниці виміру

### 4 Нормативні акти (`regulatory_acts.json`)

- Закон України "Про лікарські засоби" (№123/96-ВР)
- Наказ МОЗ №1114 (маркування)
- GMP (виробнича практика)
- ICH Q6A (міжнародні стандарти)

## 🛠 Технології

### Frontend

| Технологія | Версія | Призначення |
|------------|--------|-------------|
| Next.js | 14.2+ | App Router, Server Components |
| React | 18+ | UI framework |
| TypeScript | 5+ | Type safety |
| Tailwind CSS | 3.4+ | Styling |
| shadcn/ui | latest | UI components |
| React Hook Form | latest | Form management |
| Zod | latest | Schema validation |

### Backend

| Технологія | Версія | Призначення |
|------------|--------|-------------|
| FastAPI | 0.100+ | Async web framework |
| Python | 3.11+ | Backend language |
| Pydantic | v2 | Data validation |
| Claude AI | 3.5 Sonnet | Text analysis |
| Supabase | latest | PostgreSQL database |
| ReportLab | latest | PDF generation |
| python-docx | latest | DOCX generation |
| Pillow | latest | Image processing |

## 💡 Функціонал

### 🎨 Генератор етикеток

1. **Крок 1**: Основна інформація про продукт
2. **Крок 2**: Склад (інгредієнти з дозуванням)
3. **Крок 3**: Спосіб застосування
4. **Крок 4**: Застереження та протипоказання
5. **Крок 5**: Інформація про виробника

**Результат**: Готовий текст етикетки з усіма обов'язковими розділами

**Формати**: PDF, DOCX, PNG

### 🔍 Перевірка етикеток

**Вхідні дані**:
- Завантаження файлу (JPG, PNG, PDF)
- Вставка тексту

**Перевірки**:
- ✅ Наявність 18 обов'язкових полів
- ❌ Пошук 52 заборонених фраз
- 💊 Валідація дозувань речовин
- 📋 Перевірка формату та структури

**Результат**:
```json
{
  "critical_errors": [
    {
      "title": "Заборонена фраза про лікування",
      "found_text": "лікує діабет",
      "regulatory_source": "Наказ МОЗ №1114, п.3.2-3.4",
      "penalty_amount": 640000,
      "recommendation": "Замініть на 'підтримує нормальний рівень глюкози'"
    }
  ],
  "overall_score": 6.5,
  "risk_level": "high",
  "total_potential_fines": 1920000
}
```

### 💊 Перевірка дозувань

**Вхідні дані**:
```json
{
  "ingredients": [
    {
      "name": "Вітамін C",
      "quantity": 1000.0,
      "unit": "мг",
      "form": "аскорбінова кислота"
    }
  ]
}
```

**Перевірки**:
- Речовина в базі дозволених
- Форма речовини дозволена
- Доза не перевищує максимум
- Доза не перевищує потрійний ліміт (критично!)

**Результат**:
- Критичні помилки (640,000 грн)
- Попередження (рекомендації)
- Статус валідації

## 🤖 Claude AI Integration

Система використовує Claude 3.5 Sonnet для:

### Аналіз етикеток
- Контекстуальний пошук завуальованих тверджень
- Виявлення натяків на лікувальні властивості
- Перевірка медичної термінології
- Аналіз структури та повноти

### Генерація текстів
- Створення комплаєнтних формулювань
- Автоматичне додавання обов'язкових застережень
- Форматування згідно вимог

### Промпти
- **Validation Prompt**: 16,634 символів (повна нормативна база + інструкції)
- **Generation Prompt**: 6,426 символів (шаблон + правила)

## 📊 API Endpoints

### Backend API

```
POST   /api/labels/generate          # Генерація етикетки
POST   /api/labels/check             # Перевірка етикетки
POST   /api/dosage/calculate         # Перевірка дозувань
GET    /api/health                   # Health check
GET    /api/labels/generate/{id}     # Отримати згенеровану
GET    /api/labels/results/{id}      # Результати перевірки
```

Документація: http://localhost:8000/docs

### Frontend Pages

```
/                    # Головна сторінка
/generator          # Генератор етикеток (5 кроків)
/checker            # Перевірка етикеток
/results/[id]       # Результати валідації
```

## 🚀 Deployment

### Frontend (Vercel)

```bash
cd frontend
vercel deploy
```

Environment variables:
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api
```

### Backend (Railway / Render)

```bash
cd backend

# Railway
railway login
railway init
railway up

# Render
# Connect GitHub repo
# Configure environment variables
```

Environment variables:
```
CLAUDE_API_KEY=sk-ant-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Docker

```bash
# Backend
cd backend
docker build -t label-check-backend .
docker run -p 8000:8000 --env-file .env label-check-backend

# Frontend
cd frontend
docker build -t label-check-frontend .
docker run -p 3000:3000 label-check-frontend
```

## 📝 Scripts

### Backend Scripts

```bash
# Seed database (initial load)
python scripts/seed_database.py

# Update regulatory data
python scripts/update_regulations.py

# Run tests
pytest
```

### Frontend Scripts

```bash
# Development
npm run dev

# Build
npm run build

# Start production
npm start

# Lint
npm run lint

# Format
npm run format
```

## 🔒 Security

- ✅ CORS налаштовано для production origins
- ✅ API keys зберігаються в `.env`
- ✅ Input validation через Pydantic
- ✅ File size limits (10MB)
- ✅ Accepted file types (JPG, PNG, PDF)
- 🔄 Rate limiting (planned)

## 🧪 Testing

### Frontend
```bash
npm run test          # Unit tests (planned)
npm run test:e2e      # E2E tests (planned)
```

### Backend
```bash
pytest                # All tests
pytest --cov          # With coverage
```

## 📚 Документація

- [Frontend README](./frontend/README.md)
- [Backend README](./backend/README.md)
- [Scripts README](./backend/scripts/README.md)
- [API Documentation](http://localhost:8000/docs)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 Ліцензія

© 2025 Label Check. Всі права захищені.

## 👥 Автори

- Backend Architecture & AI Integration
- Frontend Development & UX Design
- Regulatory Data Collection

## 🙏 Подяки

- **Anthropic** - Claude AI API
- **Supabase** - Database infrastructure
- **Vercel** - Next.js team
- **FastAPI** - Sebastian Ramirez
- **shadcn** - UI components

## 📧 Контакти

- **Email**: support@labelcheck.com
- **Website**: https://labelcheck.com
- **GitHub**: https://github.com/labelcheck

---

**Made with ❤️ in Ukraine 🇺🇦**

Створено для підтримки українських виробників дієтичних добавок у дотриманні законодавства та уникненні штрафів.

