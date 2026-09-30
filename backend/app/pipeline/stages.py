import time

from app.errors import DocuIntelError
from app.logging_setup import get_logger

log = get_logger(__name__)


class StageError(DocuIntelError):
    """A pipeline stage failed; the message is safe to show to the user."""


class StageRunner:
    """Runs one stage: logs start/end/duration and turns any failure into StageError."""

    def __init__(self):
        self.durations: dict[str, float] = {}

    def run(self, name: str, fn, *args):
        log.info("stage=%s started", name)
        started = time.perf_counter()
        try:
            result = fn(*args)
        except Exception as exc:
            log.error("stage=%s failed error=%s", name, type(exc).__name__)
            known = isinstance(exc, DocuIntelError)
            raise StageError(f"{name} failed: {exc}" if known
                             else f"{name} failed unexpectedly") from exc
        self.durations[name] = round(time.perf_counter() - started, 2)
        log.info("stage=%s finished in %.2fs", name, self.durations[name])
        return result
