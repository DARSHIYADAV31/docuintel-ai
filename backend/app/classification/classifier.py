from dataclasses import dataclass

from app.errors import ModelUnavailableError
from app.llm.json_utils import parse_json_object
from app.llm.prompts.classify import build_classify_prompt
from app.logging_setup import get_logger

log = get_logger(__name__)
VALID_TYPES = {"invoice", "contract", "po"}
MIN_CONFIDENCE = 0.5  # below this we admit we do not know instead of guessing


@dataclass
class Classification:
    doc_type: str
    confidence: float


def _parse(raw_text: str) -> Classification:
    data = parse_json_object(raw_text)
    doc_type = str(data.get("doc_type", "")).lower()
    if doc_type not in VALID_TYPES:
        return Classification("unknown", 0.0)
    confidence = min(max(float(data.get("confidence", 0.0)), 0.0), 1.0)
    if confidence < MIN_CONFIDENCE:
        return Classification("unknown", confidence)
    return Classification(doc_type, confidence)


def classify_document(router, text: str) -> Classification:
    """Single-model task: Gemini, with Mistral only as fallback (inside router)."""
    try:
        result = _parse(router.generate(build_classify_prompt(text), json_mode=True).text)
    except ModelUnavailableError:
        raise  # an outage is not "unknown type"; let the pipeline report it as a failure
    except Exception as exc:
        log.error("classification failed: %s", type(exc).__name__)
        return Classification("unknown", 0.0)
    log.info("classified as %s confidence=%.2f", result.doc_type, result.confidence)
    return result
