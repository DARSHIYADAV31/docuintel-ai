from app.config import get_settings
from app.llm.types import LLMResult


def generate(prompt: str, json_mode: bool = False) -> LLMResult:
    from google import genai
    from google.genai import types

    settings = get_settings()
    client = genai.Client(api_key=settings.gemini_api_key)
    config = types.GenerateContentConfig(response_mime_type="application/json") \
        if json_mode else None
    resp = client.models.generate_content(model=settings.gemini_model,
                                          contents=prompt, config=config)
    usage = resp.usage_metadata
    return LLMResult(
        text=resp.text or "",
        model=settings.gemini_model,
        input_tokens=usage.prompt_token_count or 0,
        output_tokens=usage.candidates_token_count or 0,
    )
