from app.config import get_settings
from app.errors import ModelUnavailableError
from app.llm import gemini_client, mistral_client
from app.llm.cost_tracker import CostTracker
from app.llm.types import LLMResult
from app.logging_setup import get_logger
from app.retry import call_with_retry

log = get_logger(__name__)


class LLMRouter:
    """Gemini first; Mistral only if Gemini fails after retries."""

    def __init__(self, tracker: CostTracker | None = None, sleep=None):
        self.tracker = tracker or CostTracker()
        self._extra = {"sleep": sleep} if sleep else {}
        self._timeout = get_settings().llm_timeout_seconds

    def _call(self, name: str, fn, prompt: str, json_mode: bool = False) -> LLMResult:
        options = {"json_mode": True} if json_mode else {}
        result = call_with_retry(lambda: fn(prompt, **options), name=name,
                                 timeout=self._timeout, **self._extra)
        self.tracker.record(result)
        log.info("%s ok in=%d out=%d", name, result.input_tokens, result.output_tokens)
        return result

    def call_single(self, name: str, prompt: str, json_mode: bool = False) -> LLMResult:
        """Call one named model with retry, no fallback (used for dual-model work)."""
        clients = {"gemini": gemini_client.generate, "mistral": mistral_client.generate}
        return self._call(name, clients[name], prompt, json_mode)

    def generate(self, prompt: str, json_mode: bool = False) -> LLMResult:
        try:
            return self.call_single("gemini", prompt, json_mode)
        except Exception:
            log.warning("gemini failed, falling back to mistral")
        try:
            return self.call_single("mistral", prompt, json_mode)
        except Exception as exc:
            raise ModelUnavailableError(
                "The AI models are unavailable or over their usage limit. Please try again later."
            ) from exc
