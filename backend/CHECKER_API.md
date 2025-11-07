# Checker API Documentation

## Огляд

Checker API надає 2-кроковий процес перевірки етикеток дієтичних добавок:

1. **Quick Check** - швидке розпізнавання тексту з фото (OCR)
2. **Full Check** - повна перевірка через DosageService

## Endpoints

### 1. POST `/api/check-label/quick`

Швидке розпізнавання тексту з фото етикетки через Claude Vision API.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (image/jpeg, image/png, image/webp, application/pdf)
- Max file size: 10MB

**Response:**
```json
{
  "check_id": "uuid",
  "ingredients": [
    {
      "name": "Цинк глюконат",
      "quantity": 25.0,
      "unit": "мг",
      "form": "цинк глюконат",
      "type": "active"
    }
  ],
  "product_info": {
    "name": "ЦИНК",
    "form": "tablets",
    "quantity": 60
  },
  "extracted_at": "2024-11-06T12:00:00"
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/check-label/quick \
  -F "file=@test_label.jpg"
```

### 2. POST `/api/check-label/full`

Повна перевірка інгредієнтів через DosageService.

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
```json
{
  "check_id": "uuid-from-quick-check"
}
```

**Response:**
```json
{
  "check_id": "uuid",
  "is_valid": false,
  "product_info": {
    "name": "ЦИНК",
    "form": "tablets",
    "quantity": 60
  },
  "errors": [
    {
      "ingredient": "Цинк глюконат",
      "message": "Перевищує максимальну дозу",
      "level": 3,
      "source": "table1",
      "current_dose": "25.0 мг",
      "max_allowed": "15.0 мг",
      "regulatory_source": "Проєкт Змін до Наказу №1114",
      "recommendation": "Зменшіть дозування до 15.0 мг",
      "penalty_amount": 640000
    }
  ],
  "warnings": [
    {
      "ingredient": "Вітамін С",
      "message": "Доза не встановлена",
      "recommendation": "Перевірте дозування"
    }
  ],
  "stats": {
    "total_ingredients": 2,
    "substances_not_found": 0,
    "total_errors": 1,
    "total_warnings": 1
  },
  "penalties": {
    "total_amount": 640000,
    "currency": "UAH"
  },
  "checked_at": "2024-11-06T12:05:00"
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/check-label/full \
  -H "Content-Type: application/json" \
  -d '{"check_id": "uuid-from-quick-check"}'
```

### 3. GET `/api/check-label/{check_id}/report.pdf`

Завантаження PDF звіту про перевірку.

**Request:**
- Method: `GET`
- Path parameter: `check_id` (UUID)

**Response:**
- Content-Type: `application/pdf`
- File download

**Example (curl):**
```bash
curl http://localhost:8000/api/check-label/{check_id}/report.pdf \
  --output report.pdf
```

## Workflow

1. **Користувач завантажує фото** → `POST /api/check-label/quick`
   - Отримує `check_id` та список інгредієнтів
   
2. **Користувач запускає повну перевірку** → `POST /api/check-label/full`
   - Використовує `check_id` з кроку 1
   - Отримує детальний звіт з помилками та попередженнями
   
3. **Користувач завантажує PDF звіт** → `GET /api/check-label/{check_id}/report.pdf`
   - Отримує PDF файл з повним звітом

## Database

Таблиця `check_sessions` зберігає:
- `check_id` - UUID сесії
- `label_data` - JSON з витягнутими даними (OCR результат)
- `report` - JSON з повним звітом перевірки
- `status` - extracted / completed / failed
- `created_at` / `completed_at` - timestamps

**SQL Migration:**
```bash
# Виконати в Supabase SQL Editor
cat supabase_check_sessions_migration.sql
```

## Error Handling

- `400` - Invalid file type or file too large
- `404` - Check ID not found
- `500` - Internal server error (Claude API, Supabase, etc.)

## Testing

```bash
# Запустити тести
pytest tests/test_checker_api.py -v

# З покриттям
pytest tests/test_checker_api.py --cov=app.api.routes.checker --cov-report=html
```

## Notes

- Claude API key має бути налаштований в `.env` файлі
- Supabase таблиця `check_sessions` має бути створена перед використанням
- PDF генерація використовує ReportLab з підтримкою українських шрифтів (DejaVu Sans)

