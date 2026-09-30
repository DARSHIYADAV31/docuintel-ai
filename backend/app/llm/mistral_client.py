from app.config import get_settings
from app.llm.types import LLMResult


def generate(prompt: str, json_mode: bool = False) -> LLMResult:
    from mistralai.client import Mistral

    settings = get_settings()
    client = Mistral(api_key=settings.mistral_api_key)
    options = {"response_format": {"type": "json_object"}} if json_mode else {}
    resp = client.chat.complete(
        model=settings.mistral_model,
        messages=[{"role": "user", "content": prompt}],
        **options,
    )
    return LLMResult(
        text=resp.choices[0].message.content or "",
        model=settings.mistral_model,
        input_tokens=resp.usage.prompt_tokens,
        output_tokens=resp.usage.completion_tokens,
    )
