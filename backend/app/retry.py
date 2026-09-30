import random
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

from app.errors import TransientError
from app.logging_setup import get_logger

log = get_logger(__name__)
_RETRYABLE_CODES = {408, 429, 500, 502, 503, 504}


def is_transient(exc: Exception) -> bool:
    if isinstance(exc, (TransientError, TimeoutError, ConnectionError)):
        return True
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    return code in _RETRYABLE_CODES


def _run_with_timeout(fn, timeout: float):
    pool = ThreadPoolExecutor(max_workers=1)
    try:
        return pool.submit(fn).result(timeout=timeout)
    except FutureTimeout:
        raise TimeoutError(f"call exceeded {timeout}s")
    finally:
        pool.shutdown(wait=False)  # never block on a hung call


def call_with_retry(fn, *, name: str, timeout: float, attempts: int = 3,
                    base_delay: float = 1.0, sleep=time.sleep):
    for attempt in range(1, attempts + 1):
        try:
            return _run_with_timeout(fn, timeout)
        except Exception as exc:
            if not is_transient(exc) or attempt == attempts:
                log.error("%s failed on attempt %d: %s code=%s", name, attempt,
                          type(exc).__name__, getattr(exc, "code", None) or getattr(exc, "status_code", None))
                raise
            delay = base_delay * 2 ** (attempt - 1) + random.uniform(0, 0.3)
            log.warning("%s attempt %d failed, retrying in %.1fs", name, attempt, delay)
            sleep(delay)
