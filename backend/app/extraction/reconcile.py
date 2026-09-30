from app.extraction.normalizers import is_well_formed, normalize_value
from app.extraction.schemas import FieldValue

AGREE, SINGLE_MODEL, ONE_SIDE_MISSING, DISAGREE_PICKED, DISAGREE = 0.95, 0.7, 0.5, 0.5, 0.4


def _text(value) -> str | None:
    if value is None or not str(value).strip():
        return None
    return str(value).strip()


def _single(value) -> FieldValue:
    text = _text(value)
    return FieldValue(text, SINGLE_MODEL if text else 0.0, False)


def _agree(name: str, gemini: str, mistral: str) -> bool:
    normalized = normalize_value(name, gemini)
    return normalized is not None and normalized == normalize_value(name, mistral)


def _reconcile(name: str, gemini_raw, mistral_raw) -> FieldValue:
    gemini, mistral = _text(gemini_raw), _text(mistral_raw)
    if gemini is None and mistral is None:
        return FieldValue(None, 0.0, False)
    if gemini is None or mistral is None:
        return FieldValue(gemini or mistral, ONE_SIDE_MISSING, True)
    if _agree(name, gemini, mistral):
        return FieldValue(gemini, AGREE, False)
    if is_well_formed(name, mistral) and not is_well_formed(name, gemini):
        return FieldValue(mistral, DISAGREE_PICKED, True)
    return FieldValue(gemini, DISAGREE, True)  # Gemini is the primary model


def reconcile_fields(names: list[str], gemini: dict | None,
                     mistral: dict | None) -> dict[str, FieldValue]:
    if gemini is None or mistral is None:
        only = gemini if gemini is not None else mistral
        return {n: _single(only.get(n)) for n in names}
    return {n: _reconcile(n, gemini.get(n), mistral.get(n)) for n in names}
