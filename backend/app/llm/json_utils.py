import json
import re

from app.errors import LLMOutputError

_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _loads(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def parse_json_object(text: str) -> dict:
    cleaned = _FENCE.sub("", text.strip())
    data = _loads(cleaned)
    if data is None:  # the model added commentary around the JSON
        data = _loads(cleaned[cleaned.find("{"): cleaned.rfind("}") + 1])
    if not isinstance(data, dict):
        raise LLMOutputError("model reply is not a JSON object")
    return data
