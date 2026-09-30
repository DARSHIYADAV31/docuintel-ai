import numpy as np
import pytest

from app.errors import VectorStoreError
from app.llm.types import LLMResult
from app.rag.answerer import NO_ANSWER, answer_question
from app.rag.citations import extract_citations
from app.vectorstore import embedder
from app.vectorstore.faiss_store import FaissStore
from app.vectorstore.indexer import index_document
from app.vectorstore.types import Hit

TEXT = "Payment is due within 30 days.\nShipping is handled by the vendor."


def _fake_embed(texts):
    """Bag-of-keywords vectors: deterministic and needs no model download."""
    keywords = ["payment", "days", "shipping", "vendor"]
    vecs = [[t.lower().count(k) + 0.01 for k in keywords] for t in texts]
    arr = np.array(vecs, dtype="float32")
    return arr / np.linalg.norm(arr, axis=1, keepdims=True)


class FakeRouter:
    def __init__(self, reply):
        self.reply, self.prompts = reply, []

    def generate(self, prompt, json_mode=False):
        self.prompts.append(prompt)
        return LLMResult(self.reply, "gemini", 1, 1)


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setattr(embedder, "embed_texts", _fake_embed)
    store = FaissStore(tmp_path)
    index_document(store, 1, TEXT)
    return store


def test_answer_includes_citations(store):
    answer = answer_question(FakeRouter("Due in 30 days [1]."), store, 1, "payment days?")
    assert answer.grounded and answer.citations[0].chunk_index == 0


def test_not_found_reply_has_no_citations(store):
    answer = answer_question(FakeRouter("NOT_FOUND"), store, 1, "colour of the moon?")
    assert answer.text == NO_ANSWER and not answer.grounded


def test_unknown_document_skips_the_llm(store):
    router = FakeRouter("should not be used")
    assert answer_question(router, store, 999, "anything").text == NO_ANSWER
    assert router.prompts == []


def test_invented_citation_numbers_are_ignored():
    hits = [Hit(0, "text", 0.9)]
    assert extract_citations("See [7] and [1] and [1].", hits)[0].chunk_index == 0
    assert len(extract_citations("See [7].", hits)) == 0


def test_empty_document_cannot_be_indexed(tmp_path):
    with pytest.raises(VectorStoreError):
        index_document(FaissStore(tmp_path), 2, "   ")


def test_json_reply_gives_short_answer_and_only_the_quoted_line(store):
    reply = '{"answer": "30 days", "sources": [1], "quote": "Payment is due within 30 days."}'
    answer = answer_question(FakeRouter(reply), store, 1, "payment days?")
    assert answer.text == "30 days" and "[" not in answer.text
    assert answer.citations[0].snippet == "Payment is due within 30 days."


def test_quote_not_found_in_chunk_falls_back_to_chunk_start(store):
    reply = '{"answer": "x", "sources": [1], "quote": "text the model invented"}'
    answer = answer_question(FakeRouter(reply), store, 1, "payment days?")
    assert answer.citations[0].snippet.startswith("Payment is due")


def test_json_not_found_reply_is_handled(store):
    reply = '{"answer": "NOT_FOUND", "sources": [], "quote": ""}'
    assert answer_question(FakeRouter(reply), store, 1, "moon colour?").text == NO_ANSWER
