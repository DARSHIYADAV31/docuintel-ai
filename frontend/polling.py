import time

POLL_SECONDS = 3
MAX_WAIT_SECONDS = 180


def wait_for_result(client, document_id: int, on_wait=lambda: None) -> dict | None:
    """Polls until processing ends; returns None if it takes too long."""
    deadline = time.monotonic() + MAX_WAIT_SECONDS
    while time.monotonic() < deadline:
        document = client.get_document(document_id)
        if document["status"] != "processing":
            return document
        on_wait()
        time.sleep(POLL_SECONDS)
    return None
