from app.errors import LLMOutputError
from app.llm.json_utils import parse_json_object
from app.llm.prompts.rag import NOT_FOUND, build_rag_prompt
from app.logging_setup import get_logger
from app.rag.citations import MARKER, build_citations
from app.rag.retriever import retrieve
from app.rag.types import Answer

log = get_logger(__name__)
NO_ANSWER = "The document does not contain this information."


def _parse_reply(reply: str) -> tuple[str, list[int], str]:
    """(answer, source numbers, supporting quote); plain-text replies use [n] markers."""
    try:
        data = parse_json_object(reply)
    except LLMOutputError:
        return reply, [int(n) for n in MARKER.findall(reply)], ""
    sources = data.get("sources")
    numbers = [n for n in sources if isinstance(n, int)] if isinstance(sources, list) else []
    return str(data.get("answer", "")).strip(), numbers, str(data.get("quote") or "")


def answer_question(router, store, document_id: int, question: str) -> Answer:
    """Single-model task: Gemini, with Mistral only as fallback (inside router)."""
    hits = retrieve(store, document_id, question)
    if not hits:
        return Answer(NO_ANSWER)
    prompt = build_rag_prompt(question, [h.text for h in hits])
    reply = router.generate(prompt, json_mode=True).text.strip()
    text, numbers, quote = _parse_reply(reply)
    if not text or NOT_FOUND in text:
        return Answer(NO_ANSWER)
    citations = build_citations(numbers, quote, hits)
    log.info("rag answered document_id=%d citations=%d", document_id, len(citations))
    return Answer(text, citations, grounded=bool(citations))
