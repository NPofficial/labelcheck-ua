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
    
    async def extract_label_data(self, image_bytes: bytes) -> Dict:
        """
        Extract structured data from label image using Claude Vision
        
        Args:
            image_bytes: Image file as bytes
            
        Returns:
            Structured label data as dict
        """
        try:
            # Convert to base64
            image_base64 = base64.standard_b64encode(image_bytes).decode("utf-8")
            
            # Detect media type from bytes
            media_type = self._detect_media_type(image_bytes)
            
            logger.info(f"Calling Claude Vision API with model {self.model}, media_type: {media_type}")
            
            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64,
                                },
                            },
                            {
                                "type": "text",
                                "text": USER_PROMPT
                            }
                        ],
                    }
                ],
                system=SYSTEM_PROMPT
            )
            
            # Extract JSON from response
            response_text = message.content[0].text
            # Зберегти у файл для дебагу
            with open("/tmp/claude_response.txt", "w", encoding="utf-8") as f:
                f.write(response_text)
            print("=" * 80)
            print("CLAUDE RAW RESPONSE:")
            print(response_text[:2000])
            print("=" * 80)
            
            # Parse JSON (Claude should return clean JSON)
            try:
                label_data = json.loads(response_text)
            except json.JSONDecodeError:
                # If Claude wrapped in markdown code blocks
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                    label_data = json.loads(json_str)
                elif "```" in response_text:
                    # Try to extract from any code block
                    parts = response_text.split("```")
                    if len(parts) >= 2:
                        json_str = parts[1].strip()
                        if json_str.startswith("json"):
                            json_str = json_str[4:].strip()
                        label_data = json.loads(json_str)
                    else:
                        raise ValueError("Could not parse Claude response as JSON")
                else:
                    raise ValueError("Could not parse Claude response as JSON")
            
            logger.info(f"Successfully extracted label data: {label_data.get('product_name')}")
            return label_data
            
        except Exception as e:
            logger.error(f"Error extracting label data: {e}", exc_info=True)
            raise
    
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

