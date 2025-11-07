from app.config import settings
import anthropic

client = anthropic.Anthropic(api_key=settings.claude_api_key)

models = [
    "claude-3-5-sonnet-20241022",
    "claude-3-opus-20240229",
    "claude-3-haiku-20240307"
]

for model in models:
    try:
        message = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print(f"✅ {model} - WORKS!")
        print(f"   Use this model!")
        break
    except Exception as e:
        print(f"❌ {model} - {str(e)[:80]}")
