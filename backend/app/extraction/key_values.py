from app.errors import DocuIntelError, LLMOutputError, ModelUnavailableError
from app.extraction.reconcile import reconcile_fields
from app.extraction.schemas import FIELDS, ExtractionResult
from app.extraction.tables import clean_rows, reconcile_line_items
from app.llm.json_utils import parse_json_object
from app.llm.prompts.extract import build_extract_prompt
from app.logging_setup import get_logger

log = get_logger(__name__)


def _ask(router, model: str, prompt: str) -> dict | None:
    for attempt in (1, 2):  # models sometimes return malformed JSON; one re-ask is cheap
        try:
            return parse_json_object(router.call_single(model, prompt, json_mode=True).text)
        except LLMOutputError:
            log.warning("%s returned invalid JSON (attempt %d)", model, attempt)
        except Exception as exc:
            log.warning("%s extraction failed: %s", model, type(exc).__name__)
            return None
    return None


def _fields_of(reply: dict | None) -> dict | None:
    if reply is None:
        return None
    fields = reply.get("fields")
    return fields if isinstance(fields, dict) else {}


def _items_of(reply: dict | None) -> list[dict] | None:
    return None if reply is None else clean_rows(reply.get("line_items"))


def extract_document(router, text: str, doc_type: str) -> ExtractionResult:
    """Runs Gemini AND Mistral, then reconciles (high-stakes values)."""
    if doc_type not in FIELDS:
        raise DocuIntelError(f"Unsupported document type: {doc_type}")
    prompt = build_extract_prompt(doc_type, text)
    gemini, mistral = _ask(router, "gemini", prompt), _ask(router, "mistral", prompt)
    if gemini is None and mistral is None:
        raise ModelUnavailableError("Both models failed to extract fields")
    fields = reconcile_fields(FIELDS[doc_type], _fields_of(gemini), _fields_of(mistral))
    subtotal = fields["subtotal"].value if "subtotal" in fields else None
    items, flagged = reconcile_line_items(_items_of(gemini), _items_of(mistral), subtotal)
    log.info("extracted doc_type=%s fields=%d rows=%d", doc_type, len(fields), len(items))
    return ExtractionResult(fields, items, flagged)
