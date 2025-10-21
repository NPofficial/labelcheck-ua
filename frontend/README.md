# Label Check - Frontend 🎨

[![Next.js](https://img.shields.io/badge/Next.js-14.2-black?style=flat&logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-06B6D4?style=flat&logo=tailwind-css)](https://tailwindcss.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react)](https://react.dev/)

Веб-застосунок для генерації та перевірки етикеток дієтичних добавок згідно українського законодавства.

## 🚀 Швидкий старт

```bash
npm install                          # Встановлення залежностей
cp .env.local.example .env.local     # Конфігурація
npm run dev                          # Запуск у dev режимі
```

Відкрийте http://localhost:3000 у браузері.

## 📦 Встановлення

### Передумови

- **Node.js** 18.0 або вище
- **npm** 9.0 або вище (або **yarn** / **pnpm**)
- **Backend API** запущений на http://localhost:8000 (або інший URL)

### Кроки встановлення

1. **Клонування репозиторію**

```bash
git clone <repository-url>
cd label-check/frontend
```

2. **Встановлення залежностей**

```bash
npm install
```

3. **Налаштування environment variables**

```bash
cp .env.local.example .env.local
```

Відредагуйте `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

4. **Запуск development server**

```bash
npm run dev
```

Застосунок буде доступний на http://localhost:3000

## 🔐 Environment Variables

| Змінна | Опис | Приклад | Обов'язкова |
|--------|------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000/api` | ✅ Так |

### Файл `.env.local`

```env
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Optional: Analytics
# NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX

# Optional: Sentry
# NEXT_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/xxx
```

## 🎮 Запуск

### Development режим

```bash
npm run dev
```

- Hot reload увімкнено
- Доступ: http://localhost:3000
- API Proxy: автоматично проксується до backend

### Production build

```bash
npm run build
npm start
```

- Оптимізований production build
- Доступ: http://localhost:3000

### Linting та форматування

```bash
npm run lint           # ESLint перевірка
npm run format         # Prettier форматування
```

## 📁 Структура проєкту

```
frontend/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── layout.tsx                # Root layout з Header/Footer
│   │   ├── page.tsx                  # Головна сторінка
│   │   ├── globals.css               # Global styles (Tailwind)
│   │   ├── generator/                # Генератор етикеток
│   │   │   └── page.tsx              # 5-step wizard
│   │   ├── checker/                  # Перевірка етикеток
│   │   │   └── page.tsx              # Upload/Text input
│   │   └── results/[id]/             # Результати перевірки
│   │       └── page.tsx              # Детальний звіт
│   │
│   ├── components/
│   │   ├── ui/                       # shadcn/ui components
│   │   │   ├── button.tsx            # Button component
│   │   │   ├── input.tsx             # Input field
│   │   │   ├── card.tsx              # Card container
│   │   │   ├── badge.tsx             # Status badge
│   │   │   ├── alert.tsx             # Alert messages
│   │   │   ├── progress.tsx          # Progress bar
│   │   │   └── textarea.tsx          # Textarea field
│   │   │
│   │   ├── forms/                    # Form components
│   │   │   ├── ProductInfoForm.tsx   # Крок 1: Основна інформація
│   │   │   ├── IngredientsForm.tsx   # Крок 2: Склад
│   │   │   ├── DosageForm.tsx        # Крок 3: Дозування
│   │   │   ├── WarningsForm.tsx      # Крок 4: Застереження
│   │   │   └── OperatorForm.tsx      # Крок 5: Виробник
│   │   │
│   │   ├── checker/                  # Checker components
│   │   │   ├── FileUpload.tsx        # Drag & drop upload
│   │   │   └── TextInput.tsx         # Text paste input
│   │   │
│   │   ├── results/                  # Results components
│   │   │   ├── ValidationReport.tsx  # Повний звіт
│   │   │   ├── ErrorCard.tsx         # Error display
│   │   │   ├── WarningCard.tsx       # Warning display
│   │   │   └── SuccessCard.tsx       # Success state
│   │   │
│   │   ├── layout/                   # Layout components
│   │   │   ├── Header.tsx            # Site header
│   │   │   ├── Footer.tsx            # Site footer
│   │   │   └── Navigation.tsx        # Navigation menu
│   │   │
│   │   └── common/                   # Common components
│   │       ├── LoadingSpinner.tsx    # Loading indicator
│   │       └── ErrorBoundary.tsx     # Error boundary
│   │
│   ├── lib/                          # Utilities
│   │   ├── utils.ts                  # Helper functions (cn, dates)
│   │   ├── api-client.ts             # API client class
│   │   ├── validations.ts            # Form validation
│   │   └── constants.ts              # App constants
│   │
│   └── types/                        # TypeScript types
│       ├── label.ts                  # Label data types
│       ├── api.ts                    # API request/response types
│       └── forms.ts                  # Form component props
│
├── public/                           # Static assets
│   ├── images/                       # Images
│   └── fonts/                        # Custom fonts
│
├── .env.local.example                # Environment template
├── .eslintrc.json                    # ESLint config
├── .prettierrc                       # Prettier config
├── next.config.js                    # Next.js config
├── tailwind.config.ts                # Tailwind config
├── tsconfig.json                     # TypeScript config
└── package.json                      # Dependencies
```

## 🎯 Ключові компоненти

### 1. Генератор етикеток (5 кроків)

**Route:** `/generator`

**Wizard Flow:**

```typescript
// Крок 1: ProductInfoForm
{
  name: "Назва продукту",
  manufacturer: "Виробник",
  dosageForm: "Таблетки",
  strength: "500 мг"
}

// Крок 2: IngredientsForm
[
  { name: "Вітамін C", quantity: "80", unit: "мг", isActive: true }
]

// Крок 3: DosageForm
[
  { 
    population: "Дорослі", 
    instruction: "По 1 таблетці", 
    frequency: "2 рази на день",
    duration: "30 днів"
  }
]

// Крок 4: WarningsForm
[
  {
    type: "contraindication",
    severity: "high",
    description: "Не застосовувати при..."
  }
]

// Крок 5: OperatorForm
{
  name: "ТОВ 'Компанія'",
  licenseNumber: "UA-123456",
  productionDate: "2025-01-01",
  expiryDate: "2027-01-01",
  batchNumber: "BATCH-001"
}
```

**Використання:**

```typescript
import { ProductInfoForm } from "@/components/forms/ProductInfoForm"

<ProductInfoForm
  initialData={data}
  onSubmit={(data) => {
    console.log(data)
    goToNextStep()
  }}
  onNext={() => goToNextStep()}
/>
```

### 2. Перевірка етикеток

**Route:** `/checker`

**Два способи перевірки:**

#### A) Завантаження файлу

```typescript
import { FileUpload } from "@/components/checker/FileUpload"

<FileUpload
  onFileSelect={(file) => setSelectedFile(file)}
  onUpload={async (file) => {
    const result = await apiClient.checkLabel(file)
    // Handle result
  }}
/>
```

#### B) Вставка тексту

```typescript
import { TextInput } from "@/components/checker/TextInput"

<TextInput
  onSubmit={async (text) => {
    const result = await apiClient.checkLabelText(text)
    // Handle result
  }}
/>
```

### 3. Результати перевірки

**Route:** `/results/[id]`

**Компоненти результатів:**

```typescript
import { ValidationReport } from "@/components/results/ValidationReport"

<ValidationReport result={validationResult} />

// validationResult:
{
  id: "uuid",
  isValid: false,
  errors: [
    {
      field: "Заборонена фраза",
      message: "Знайдено заборонену фразу 'лікує'",
      severity: "error",
      code: "ERR_FORBIDDEN_PHRASE"
    }
  ],
  warnings: [...],
  validatedAt: "2025-01-20T12:00:00Z",
  score: 6.5
}
```

## 🔌 API Integration

### API Client

**Файл:** `src/lib/api-client.ts`

**Initialization:**

```typescript
import { apiClient } from "@/lib/api-client"
```

### Приклади використання

#### 1. Генерація етикетки

```typescript
const labelData = {
  product_info: {
    name: "Вітамін C",
    manufacturer: "ТОВ 'Компанія'",
    dosage_form: "Таблетки",
    strength: "500 мг"
  },
  ingredients: [
    { name: "Аскорбінова кислота", quantity: "500", unit: "мг", isActive: true }
  ],
  dosages: [...],
  warnings: [...],
  operator_info: {...}
}

const response = await apiClient.generateLabel({
  labelData,
  format: "pdf"
})

if (response.success) {
  console.log("Label ID:", response.data.id)
  console.log("Download URL:", response.data.downloadUrl)
}
```

#### 2. Перевірка етикетки (файл)

```typescript
const file = event.target.files[0]

const response = await apiClient.checkLabel(file)

if (response.success) {
  const result = response.data
  console.log("Is Valid:", result.isValid)
  console.log("Errors:", result.errors.length)
  console.log("Score:", result.score)
}
```

#### 3. Перевірка етикетки (текст)

```typescript
const text = "ДІЄТИЧНА ДОБАВКА\n\nВітамін C 500 мг..."

const response = await apiClient.checkLabelText(text)

if (response.success) {
  console.log("Validation result:", response.data)
}
```

#### 4. Отримання результату

```typescript
const resultId = "uuid-here"

const response = await apiClient.getValidationResult(resultId)

if (response.success) {
  console.log("Result:", response.data)
}
```

### Error Handling

```typescript
try {
  const response = await apiClient.checkLabel(file)
  
  if (!response.success) {
    // Handle API error
    console.error(response.error)
    showToast(response.error, "error")
  } else {
    // Handle success
    const result = response.data
  }
} catch (error) {
  // Handle network error
  console.error("Network error:", error)
  showToast("Помилка з'єднання з сервером", "error")
}
```

## 🎨 Дизайн-система

### Кольори

| Назва | Hex | Tailwind Class | Використання |
|-------|-----|----------------|--------------|
| **Primary** | `#3B82F6` | `blue-500` | Кнопки, посилання, акценти |
| **Success** | `#10B981` | `green-500` | Успішна валідація, позитивні дії |
| **Error** | `#EF4444` | `red-500` | Критичні помилки, штрафи 640k |
| **Warning** | `#F59E0B` | `amber-500` | Попередження, рекомендації |
| **Background** | `#FFFFFF` | `white` | Основний фон |
| **Secondary BG** | `#F8FAFC` | `slate-50` | Альтернативний фон |
| **Text Primary** | `#1E293B` | `slate-800` | Основний текст |
| **Text Secondary** | `#64748B` | `slate-500` | Вторинний текст |
| **Border** | `#E2E8F0` | `slate-200` | Рамки, роздільники |

### Кольорова палітра у коді

```typescript
// tailwind.config.ts
colors: {
  primary: {
    DEFAULT: "#3B82F6",
    50: "#EBF2FE",
    500: "#3B82F6",
    700: "#084BB8",
  },
  success: {
    DEFAULT: "#10B981",
    500: "#10B981",
  },
  error: {
    DEFAULT: "#EF4444",
    500: "#EF4444",
  },
  warning: {
    DEFAULT: "#F59E0B",
    500: "#F59E0B",
  }
}
```

### Типографіка

```css
/* Заголовки */
h1 { font-size: 32px; font-weight: 700; } /* text-3xl font-bold */
h2 { font-size: 24px; font-weight: 600; } /* text-2xl font-semibold */
h3 { font-size: 20px; font-weight: 600; } /* text-xl font-semibold */

/* Текст */
body { font-size: 16px; line-height: 1.6; } /* text-base */
small { font-size: 14px; } /* text-sm */

/* Шрифт */
font-family: 'Inter', system-ui, -apple-system, sans-serif;
```

### Компоненти

```typescript
// Button variants
<Button variant="default">Зберегти</Button>
<Button variant="primary">Перевірити</Button>
<Button variant="outline">Скасувати</Button>
<Button variant="ghost">Очистити</Button>
<Button variant="success">Підтвердити</Button>
<Button variant="error">Видалити</Button>

// Badge variants
<Badge variant="success">Валідний</Badge>
<Badge variant="error">Помилка</Badge>
<Badge variant="warning">Попередження</Badge>

// Alert variants
<Alert variant="success">Успішно!</Alert>
<Alert variant="error">Критична помилка</Alert>
<Alert variant="warning">Увага!</Alert>
```

## 🚀 Deployment

### Vercel (рекомендовано)

1. **Підключення до Vercel**

```bash
npm install -g vercel
vercel login
```

2. **Deploy**

```bash
vercel
```

3. **Production deploy**

```bash
vercel --prod
```

4. **Environment Variables у Vercel Dashboard**

```
NEXT_PUBLIC_API_URL = https://your-backend.railway.app/api
```

**Або через CLI:**

```bash
vercel env add NEXT_PUBLIC_API_URL production
```

### Netlify

1. **Підключення репозиторію**

```bash
npm install -g netlify-cli
netlify login
netlify init
```

2. **Build settings у `netlify.toml`**

```toml
[build]
  command = "npm run build"
  publish = ".next"

[[plugins]]
  package = "@netlify/plugin-nextjs"
```

3. **Environment Variables**

```bash
netlify env:set NEXT_PUBLIC_API_URL "https://your-backend.railway.app/api"
```

4. **Deploy**

```bash
netlify deploy --prod
```

### Docker

**Dockerfile:**

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
RUN npm ci --production
EXPOSE 3000
CMD ["npm", "start"]
```

**Build & Run:**

```bash
docker build -t label-check-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://backend:8000/api label-check-frontend
```

## 🐛 Troubleshooting

### 1. `Module not found: Can't resolve '@/components/...'`

**Причина:** TypeScript path mapping не налаштовано

**Рішення:**

```json
// tsconfig.json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### 2. `Failed to fetch` при API запитах

**Причина:** Backend не запущений або неправильний URL

**Рішення:**

1. Перевірте `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

2. Перевірте що backend запущений:
```bash
curl http://localhost:8000/api/health
```

3. Перевірте CORS у backend (`allowed_origins`)

### 3. Tailwind styles не працюють

**Причина:** Tailwind config або globals.css не підключені

**Рішення:**

```css
/* app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

```typescript
// app/layout.tsx
import "./globals.css"
```

### 4. `Error: Text content does not match server-rendered HTML`

**Причина:** Hydration mismatch (Server vs Client)

**Рішення:**

- Використовуйте `suppressHydrationWarning` для dynamic content
- Або рендеріть на клієнті: `{typeof window !== 'undefined' && ...}`

### 5. `Module parse failed: Unexpected token` для SVG/images

**Причина:** Next.js не налаштований для asset imports

**Рішення:**

```typescript
// next.config.js
module.exports = {
  webpack: (config) => {
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack']
    })
    return config
  }
}
```

### 6. Build fails з TypeScript errors

**Причина:** Type checking під час build

**Рішення:**

```json
// next.config.js
module.exports = {
  typescript: {
    // ⚠️ Тимчасово для production (не рекомендовано!)
    ignoreBuildErrors: true,
  }
}
```

**Краще:** Виправте TypeScript помилки локально:

```bash
npm run type-check
```

## 💻 Корисні команди

```bash
# Development
npm run dev              # Start dev server
npm run build            # Production build
npm run start            # Start production server
npm run lint             # Run ESLint
npm run format           # Run Prettier
npm run type-check       # TypeScript check

# Cleanup
rm -rf .next             # Clear build cache
rm -rf node_modules      # Clear dependencies
npm install              # Reinstall

# Debugging
npm run dev -- --turbo   # Dev with Turbopack (faster)
npm run build -- --debug # Debug build process

# Testing (майбутнє)
npm run test             # Run tests
npm run test:e2e         # E2E tests
npm run test:coverage    # Coverage report
```

## 📚 Документація

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [React Hook Form](https://react-hook-form.com/)
- [Zod](https://zod.dev/)

## 🔗 Посилання

- **Backend API**: [../backend/README.md](../backend/README.md)
- **Main README**: [../README.md](../README.md)
- **Scripts**: [../backend/scripts/README.md](../backend/scripts/README.md)

## 📝 Ліцензія

© 2025 Label Check. Всі права захищені.

---

**Need help?** Відкрийте issue або напишіть на support@labelcheck.com
