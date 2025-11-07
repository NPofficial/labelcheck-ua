import anthropic
import os

# Твій API key з .env
api_key = os.getenv("CLAUDE_API_KEY") or "твій_ключ_тут"

client = anthropic.Anthropic(api_key=api_key)

# Тест Sonnet 4.5
print("Тестуємо Claude Sonnet 4.5...")
try:
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=100,
        messages=[{"role": "user", "content": "Привіт! Яка ти модель?"}]
    )
    print(f"✅ ПРАЦЮЄ! Модель: claude-sonnet-4-5-20250929")
    print(f"Відповідь: {message.content[0].text}")
except Exception as e:
    print(f"❌ ПОМИЛКА: {e}")
    print("\nСпробуємо Sonnet 3.5...")
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": "Привіт! Яка ти модель?"}]
        )
        print(f"✅ ПРАЦЮЄ! Модель: claude-3-5-sonnet-20241022")
        print(f"Відповідь: {message.content[0].text}")
    except Exception as e2:
        print(f"❌ ПОМИЛКА: {e2}")

