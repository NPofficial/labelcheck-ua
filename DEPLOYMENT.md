# 🚀 DEPLOYMENT GUIDE - Label Check UA

## 📊 Архітектура
**Frontend (Netlify) → Backend (Railway) → Supabase + Claude API**

- **Frontend**: Next.js додаток на Netlify
- **Backend**: FastAPI на Railway
- **База даних**: Supabase PostgreSQL
- **AI**: Claude API для аналізу етикеток

## ⏱️ Загальний час: ~45 хвилин

## 📋 Передумови
- ✅ GitHub акаунт
- ✅ Railway акаунт (https://railway.app/)
- ✅ Netlify акаунт (https://netlify.com/)
- ✅ Supabase акаунт (https://supabase.com/)
- ✅ Claude API акаунт (https://console.anthropic.com/)

---

## 🔑 КРОК 1: Отримання API ключів (10 хв)

### 1.1 Claude API Key
1. Перейдіть до https://console.anthropic.com/
2. Увійдіть або зареєструйтесь
3. Натисніть **"Create Key"**
4. Введіть назву: `labelcheck-production`
5. Скопіюйте ключ (формат: `sk-ant-api03-...`)
6. **⚠️ Збережіть ключ безпечно!**

### 1.2 Supabase Setup
1. Перейдіть до https://supabase.com/
2. Натисніть **"New Project"**
3. Назва проекту: `labelcheck`
4. Виберіть регіон (рекомендовано: Europe)
5. Створіть пароль для бази даних
6. Дочекайтесь завершення створення (~2 хв)

### 1.3 Supabase API Keys
1. В проекті перейдіть до **Settings → API**
2. Скопіюйте:
   - **Project URL** (формат: `https://xxx.supabase.co`)
   - **anon public key** (формат: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

---

## 🗄️ КРОК 2: Налаштування Supabase (5 хв)

### 2.1 SQL Editor
1. В Supabase Dashboard перейдіть до **SQL Editor**
2. Натисніть **"New Query"**
3. Скопіюйте та виконайте SQL з файлу `backend/scripts/seed_database.py`
4. Перевірте що таблиці створені в **Table Editor**

### 2.2 Database Tables
Перевірте наявність таблиць:
- `regulatory_acts`
- `allowed_substances` 
- `forbidden_phrases`
- `mandatory_fields`

---

## 🚂 КРОК 3: Deploy Backend на Railway (10 хв)

### 3.1 Railway Setup
1. Перейдіть до https://railway.app/
2. Натисніть **"New Project"**
3. Виберіть **"Deploy from GitHub repo"**
4. Виберіть ваш репозиторій `label-check`
5. Виберіть папку `backend`

### 3.2 Environment Variables
В Railway Dashboard → **Variables** додайте:

```bash
# API Keys
CLAUDE_API_KEY=sk-ant-api03-your_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# Application
APP_NAME=Label Check API
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000

# CORS
ALLOWED_ORIGINS=https://your-netlify-site.netlify.app

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=/tmp/uploads

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### 3.3 Railway Configuration
1. Railway автоматично виявить `railway.json`
2. Перевірте що **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Натисніть **"Deploy"**
4. Дочекайтесь завершення (~3-5 хв)

### 3.4 Отримання Backend URL
1. Після успішного deploy скопіюйте **Public URL**
2. Формат: `https://labelcheck-api-production.up.railway.app`
3. **⚠️ Збережіть цей URL!**

---

## 🌐 КРОК 4: Deploy Frontend на Netlify (5 хв)

### 4.1 Netlify Setup
1. Перейдіть до https://netlify.com/
2. Натисніть **"New site from Git"**
3. Виберіть **GitHub** → ваш репозиторій
4. Виберіть папку `frontend`

### 4.2 Build Settings
```
Build command: npm run build
Publish directory: .next
```

### 4.3 Environment Variables
В Netlify Dashboard → **Site settings → Environment variables**:

```bash
NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app/api
```

### 4.4 Deploy
1. Натисніть **"Deploy site"**
2. Дочекайтесь завершення (~2-3 хв)
3. Скопіюйте **Site URL** (формат: `https://amazing-name-123456.netlify.app`)

---

## ✅ КРОК 5: Тестування (5 хв)

### 5.1 Backend Health Check
```bash
curl https://your-railway-url.up.railway.app/health
```
**Очікуваний результат**: `{"status": "healthy"}`

### 5.2 Frontend Connection
1. Відкрийте ваш Netlify URL
2. Перевірте що сайт завантажується
3. Спробуйте відправити тестовий запит

### 5.3 API Endpoints
Перевірте доступність:
- `GET /health` - Health check
- `POST /api/check` - Label validation
- `POST /api/generate` - Label generation

---

## 🔧 Troubleshooting

### ❌ Backend не запускається
**Проблема**: Railway deployment failed
**Рішення**:
1. Перевірте environment variables
2. Переконайтесь що `CLAUDE_API_KEY` валідний
3. Перевірте логи в Railway Dashboard

### ❌ Frontend не підключається до Backend
**Проблема**: CORS errors або 404
**Рішення**:
1. Перевірте `NEXT_PUBLIC_API_URL` в Netlify
2. Переконайтесь що `ALLOWED_ORIGINS` містить ваш Netlify URL
3. Перевірте що backend URL закінчується на `/api`

### ❌ Supabase connection failed
**Проблема**: Database connection errors
**Рішення**:
1. Перевірте `SUPABASE_URL` та `SUPABASE_KEY`
2. Переконайтесь що Supabase проект активний
3. Перевірте що таблиці створені

### ❌ Claude API errors
**Проблема**: AI analysis не працює
**Рішення**:
1. Перевірте `CLAUDE_API_KEY` валідність
2. Переконайтесь що у вас є кредити в Anthropic
3. Перевірте rate limits

---

## 📞 Підтримка

### Корисні посилання:
- **Railway Docs**: https://docs.railway.app/
- **Netlify Docs**: https://docs.netlify.com/
- **Supabase Docs**: https://supabase.com/docs
- **Claude API Docs**: https://docs.anthropic.com/

### Логи та моніторинг:
- **Railway**: Dashboard → Logs
- **Netlify**: Site settings → Functions → Logs
- **Supabase**: Dashboard → Logs

---

## 🎉 Готово!

Ваш Label Check UA додаток тепер працює в production:
- ✅ Frontend: `https://your-site.netlify.app`
- ✅ Backend: `https://your-api.up.railway.app`
- ✅ Database: Supabase PostgreSQL
- ✅ AI: Claude API

**Наступні кроки:**
1. Налаштуйте custom domain (опціонально)
2. Налаштуйте SSL сертифікати
3. Налаштуйте моніторинг та алерти
4. Створіть backup стратегію

---

*Створено для Label Check UA проекту* 🇺🇦
