"""Claude OCR Service for extracting label data from images"""

import anthropic
import base64
import json
from typing import Dict, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Prompts for Claude Vision API
SYSTEM_PROMPT = """
Ти - експерт з українського законодавства про дієтичні добавки.

Твоє завдання: проаналізувати зображення етикетки дієтичної добавки 
та витягти всю важливу інформацію.

КРИТИЧНО ВАЖЛИВО:
1. Витягни ВСІ інгредієнти зі складу з їх кількістю
2. Розпізнай одиниці виміру (мг, мкг, г, МО, КУО)
3. Визнач форми речовин (наприклад: "цинк глюконат", "аскорбінова кислота")
4. Розділи інгредієнти на активні та допоміжні (excipient)

ФОРМАТ ВІДПОВІДІ: JSON згідно схеми нижче
"""

USER_PROMPT = """
Проаналізуй це зображення етикетки дієтичної добавки.

Витягни:
1. Назва продукту
2. Форма випуску (tablets/capsules/powder/liquid)
3. Кількість в упаковці
4. СКЛАД - список ВСІХ інгредієнтів:
   - Назва інгредієнта (українською)
   - Кількість (число)
   - Одиниця виміру (мг/мкг/г/МО/КУО)
   - Форма речовини (якщо вказана)
   - Тип (active або excipient)
5. Рекомендована добова доза
6. Застереження до споживання
7. Відповідальна особа/Оператор ринку:
   - Назва
   - Код ЄДРПОУ
   - Адреса
8. Виробник (якщо відрізняється від оператора)
9. Термін придатності
10. Умови зберігання
11. ТУ У (якщо є)
11a. НОМЕР ПАРТІЇ:
    Знайди на етикетці будь-яку інформацію про партію:
    - Якщо є "Партія №: [число/дата]" → витягни це
    - Якщо написано що партія співпадає з датою - знайди цю дату (виробництва або "Вжити до")
    - Шукай в УСЬОМУ тексті етикетки
    Поверни в batch_number
11b. АЛЕРГЕНИ - проаналізуй інгредієнти:
    Перевір чи є алергени з 14 категорій:
    глютен, молоко, яйця, риба, ракоподібні, соя, арахіс, горіхи, селера, гірчиця, кунжут, сульфіти, люпин, молюски
    Якщо є - список назв, якщо немає - null
12. ОБОВ'ЯЗКОВІ ФРАЗИ - перевір наявність кожної фрази на етикетці (true/false):
    - Чи є точний напис "ДІЄТИЧНА ДОБАВКА" або "DIETARY SUPPLEMENT"?
    - Чи є фраза "Не є лікарським засобом"?
    - Чи є фраза про недопущення перевищення дози (будь-який варіант)?
    - Чи є фраза про заміну раціону харчування (будь-який варіант)?
    - Чи є фраза про зберігання в недоступному для дітей місці?
13. ПОВНИЙ ТЕКСТ: витягни весь текст з етикетки одним рядком, збережи всі слова

ВАЖЛИВО:
- Якщо щось не вказано на етикетці, використай null
- Одиниці виміру: залиш як є (мг, мкг, г)
- Будь максимально точним з цифрами

Поверни тільки JSON, без додаткового тексту.

JSON Schema:
{
  "product_name": string,
  "form": "tablets" | "capsules" | "powder" | "liquid",
  "quantity": number,
  "ingredients": [
    {
      "name": string,
      "quantity": number,
      "unit": string,
      "form": string | null,
      "type": "active" | "excipient"
    }
  ],
  "daily_dose": string,
  "warnings": string[],
  "operator": {
    "name": string,
    "edrpou": string | null,
    "address": string
  },
  "manufacturer": {
    "name": string,
    "address": string
  } | null,
  "shelf_life": string,
  "storage": string,
  "tech_specs": "ТУ У 10.8-41815746-002:2021" (or null),
  "batch_number": "17.09.2025" (or null),
  "allergens": ["глютен", "соя"] (or null),
  "mandatory_phrases": {
    "has_dietary_supplement_label": boolean,
    "has_not_medicine": boolean,
    "has_not_exceed_dose": boolean,
    "has_not_replace_diet": boolean,
    "has_keep_away_children": boolean
  },
  "full_text": string
}
"""


class ClaudeOCRService:
    """Service for extracting label data using Claude Vision API"""
    
    def __init__(self):
        """Initialize Claude OCR Service"""
        try:
            self.client = anthropic.Anthropic(
                api_key=settings.claude_api_key
            )
            # Using latest Claude Sonnet model with vision support
            # Note: Update to latest model name if needed
            self.model = "claude-sonnet-4-5-20250929"
            logger.info("ClaudeOCRService initialized")
        except Exception as e:
            logger.error(f"Error initializing ClaudeOCRService: {e}", exc_info=True)
            raise
    
    async def extract_full_text(self, image_bytes: bytes) -> str:
        """
        STAGE 1: Extract ALL text from label (pure OCR, no parsing)
        
        Args:
            image_bytes: Image file as bytes
            
        Returns:
            str: Complete raw text from label
        """
        prompt = """Прочитай ВЕСЬ текст з цієї етикетки дієтичної добавки.

# ГОЛОВНЕ ПРАВИЛО

ЧИТАЙ АБСОЛЮТНО ВСЕ що є текстом!

## ВКЛЮЧАЙ:

✅ **ВСЕ слова, фрази, речення**
✅ Навіть якщо здається неважливим
✅ Навіть дрібний шрифт внизу етикетки
✅ Все що можна прочитати як текст
✅ Цифри, коди, номери
✅ Абревіатури, скорочення
✅ Українську, англійську, будь-яку мову

**Приклад що ОБОВ'ЯЗКОВО включати:**
- Назви продуктів, речовин
- Дози, одиниці (мг, мкг, г)
- Застереження, інструкції
- Компанії, адреси, телефони
- Терміни, партії, коди (ТУ У, ЄДРПОУ)
- Фрази "Не є лікарським засобом"
- Температура зберігання
- Вжити до...
- ВСЕ ІНШЕ!

## НЕ ВКЛЮЧАЙ (тільки ці 2 типи):

❌ Штрих-коди (візуальні елементи, не текст)
❌ Логотипи, піктограми, значки

---

# ФОРМАТ ВИВОДУ

Просто весь текст підряд. Без структури, без аналізу.
Копіюй дослівно як бачиш (мг(mg), °C тощо).

Приклад початку:
"ДІЄТИЧНА ДОБАВКА МАГНІЙ 500+Б6+В12 Mg 500+B6+B12 120 ТАБЛЕТОК Склад: цитрат магнію – 500 мг(mg)..."

КРИТИЧНО: Якщо сумніваєшся чи включати щось - ВКЛЮЧАЙ!
"""
        
        try:
            # Encode image
            image_base64 = base64.standard_b64encode(image_bytes).decode("utf-8")
            media_type = self._detect_media_type(image_bytes)
            
            # Call Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )
            
            full_text = response.content[0].text.strip()
            logger.info(f"✅ Stage 1: Extracted {len(full_text)} characters")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error in Stage 1 (extract_full_text): {e}", exc_info=True)
            raise
    
    async def parse_structured_data(self, full_text: str) -> Dict:
        """
        STAGE 2: Parse full text into structured fields
        
        Args:
            full_text: Complete text from Stage 1
            
        Returns:
            Dict with structured data
        """
        prompt = f"""Витягни structured data з тексту етикетки дієтичної добавки.

# ВХІДНИЙ ТЕКСТ:
```
{full_text}
```

# ЯК ШУКАТИ КОЖНЕ ПОЛЕ:

## 1. OPERATOR (Замовник/Відповідальна особа)
Шукай фрази:
- "Замовник"
- "Відповідальна особа"
- "Оператор ринку"
- "відповідальний за інформацію"

Приклад у тексті:
"Замовник (відповідальний за інформацію): ТОВ «Українські вітаміни», Україна, Дніпропетровська обл..."
Витягни:
- legal_name: "ТОВ «Українські вітаміни»"
- address: "Україна, Дніпропетровська обл., м. Дніпро, вул. Сонячна Набережна, буд. 2"
- phone: "+38(097)106-32-75" (якщо є)

## 2. ЄДРПОУ (8 цифр)
Шукай:
- "ЄДРПОУ:" + 8 цифр
- "Код ЄДРПОУ:" + 8 цифр
- Іноді в ТУ У: "10.8-41815746-002" → ЄДРПОУ може бути "41815746"

Якщо не знайдено явно - пиши null.

## 3. ВИРОБНИК
Шукай фрази:
- "Виробник:"
- "Manufacturer:"
- "Вироблено:"

Приклад:
"Виробник: ТОВ «Біо Лайт» Україна, Запорізька обл., м. Запоріжжя..."
Витягни:
- name: "ТОВ «Біо Лайт»"
- address: "Україна, Запорізька обл., м. Запоріжжя, вул. Перемоги, буд. 135-А"

## 4. BATCH NUMBER (Номер партії)
Шукай фрази:
- "Партія №:"
- "Номер партії:"
- "Batch:"
- "Lot:"

Приклад:
"Партія №: 17.09.2025"
Витягни: "17.09.2025"

## 5. ІНГРЕДІЄНТИ
Шукай:
- "Склад:"
- Список речовин з дозами

Приклад:
"цитрат магнію – 500 мг(mg)"
Витягни:
- name: "цитрат магнію"
- quantity: 500
- unit: "мг"
- type: "active"

Допоміжні речовини (після "Допоміжні речовини:") → type: "excipient"

## 6. WARNINGS
Шукай:
- "Застереження:"
- Список протипоказань

Приклад:
"вагітність, годування груддю, індивідуальна непереносимість"

## 7. MANDATORY PHRASES
Шукай ТОЧНІ фрази:
- "Не є лікарським засобом"
- "Не перевищувати рекомендовану дозу"
- "не слід використовувати як заміну"
- "в недоступному для дітей"

# OUTPUT JSON:
{{
  "product_name": "МАГНІЙ 500+Б6+В12",
  "form": "tablets",
  "quantity": 120,
  "ingredients": [
    {{"name": "цитрат магнію", "quantity": 500, "unit": "мг", "type": "active"}},
    {{"name": "МКЦ", "quantity": null, "unit": null, "type": "excipient"}}
  ],
  "daily_dose": "1 таблетка на день",
  "operator": {{
    "name": "ТОВ «Українські вітаміни»",
    "edrpou": null,
    "address": "Україна, Дніпропетровська обл., м. Дніпро, вул. Сонячна Набережна, буд. 2"
  }},
  "manufacturer": {{
    "name": "ТОВ «Біо Лайт»",
    "address": "Україна, Запорізька обл., м. Запоріжжя, вул. Перемоги, буд. 135-А"
  }} або null,
  "batch_number": "17.09.2025",
  "warnings": ["вагітність", "годування груддю", "індивідуальна непереносимість"],
  "shelf_life": "2 роки",
  "storage": "зберігати в сухому місці",
  "tech_specs": "ТУ У 10.8-41815746-002:2021" або null,
  "allergens": ["глютен", "соя"] або null,
  "mandatory_phrases": {{
    "has_dietary_supplement_label": true,
    "has_not_medicine": true,
    "has_not_exceed_dose": true,
    "has_not_replace_diet": false,
    "has_keep_away_children": true
  }}
}}

# ВАЖЛИВО:
- Шукай ВСЮДИ в тексті, не тільки на початку
- Якщо не знайдено - пиши null (не вигадуй!)
- ЄДРПОУ може бути відсутнім - це нормально
- Поверни ТІЛЬКИ JSON, без коментарів

Проаналізуй текст і поверни JSON.
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # ============ ДОДАТИ ЛОГУВАННЯ ============
            raw_response = response.content[0].text
            logger.info("="*60)
            logger.info("🔍 RAW CLAUDE RESPONSE (Stage 2):")
            logger.info("="*60)
            logger.info(raw_response[:1000])  # Перші 1000 символів
            logger.info("="*60)
            # ============ КІНЕЦЬ ЛОГУВАННЯ ============
            
            # Parse JSON
            try:
                result = json.loads(raw_response)  # Використати raw_response
            except json.JSONDecodeError:
                # If Claude wrapped in markdown code blocks
                if "```json" in raw_response:
                    json_str = raw_response.split("```json")[1].split("```")[0].strip()
                    result = json.loads(json_str)
                elif "```" in raw_response:
                    parts = raw_response.split("```")
                    if len(parts) >= 2:
                        json_str = parts[1].strip()
                        if json_str.startswith("json"):
                            json_str = json_str[4:].strip()
                        result = json.loads(json_str)
                    else:
                        raise ValueError("Could not parse Claude response as JSON")
                else:
                    raise ValueError("Could not parse Claude response as JSON")
            
            logger.info(f"✅ Stage 2: Parsed {len(result.get('ingredients', []))} ingredients")
            return result
            
        except Exception as e:
            logger.error(f"Error in Stage 2 (parse_structured_data): {e}", exc_info=True)
            # Fallback - return minimal structure
            return {
                "error": "Failed to parse structured data",
                "full_text": full_text
            }
    
    async def analyze_label(self, image_bytes: bytes) -> Dict:
        """
        Complete 2-stage analysis: Extract text → Parse structure
        
        Args:
            image_bytes: Image bytes (JPEG/PNG)
            
        Returns:
            Dict with full_text + all structured fields
        """
        logger.info("🚀 Starting 2-stage OCR analysis")
        
        # ==========================================
        # STAGE 1: Extract full text (Pure OCR)
        # ==========================================
        full_text = await self.extract_full_text(image_bytes)
        
        if not full_text or len(full_text) < 50:
            raise ValueError("Failed to extract text from image")
        
        logger.info(f"📝 Full text extracted: {len(full_text)} characters")
        
        # ==========================================
        # STAGE 2: Parse structured data
        # ==========================================
        result = await self.parse_structured_data(full_text)
        
        # КРИТИЧНО: Ensure full_text в результаті
        result["full_text"] = full_text
        
        logger.info(f"✅ 2-stage OCR complete:")
        logger.info(f"  - Text: {len(full_text)} chars")
        logger.info(f"  - Ingredients: {len(result.get('ingredients', []))}")
        logger.info(f"  - Operator: {result.get('operator', {}).get('name')}")
        logger.info(f"  - Batch: {result.get('batch_number')}")
        
        return result
    
    async def extract_label_data(self, image_bytes: bytes) -> Dict:
        """
        Extract structured data from label image using Claude Vision
        
        DEPRECATED: Use analyze_label() instead (2-stage approach)
        Kept for backward compatibility
        
        Args:
            image_bytes: Image file as bytes
            
        Returns:
            Structured label data as dict
        """
        # Use new 2-stage approach
        return await self.analyze_label(image_bytes)
    
    def _detect_media_type(self, image_bytes: bytes) -> str:
        """
        Detect image format from magic bytes
        
        Args:
            image_bytes: Image file as bytes
            
        Returns:
            Media type string (image/jpeg, image/png, image/webp)
        """
        if len(image_bytes) < 12:
            logger.warning("Image too small to detect format, defaulting to image/jpeg")
            return "image/jpeg"
        
        # JPEG magic number: FF D8
        if image_bytes[:2] == b'\xff\xd8':
            return "image/jpeg"
        # PNG magic number: 89 50 4E 47 0D 0A 1A 0A
        elif image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            return "image/png"
        # WebP magic number: RIFF....WEBP
        elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
            return "image/webp"
        # Default to JPEG
        else:
            logger.warning("Unknown image format, defaulting to image/jpeg")
            return "image/jpeg"

