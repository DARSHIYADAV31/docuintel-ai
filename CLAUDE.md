# DocuIntel AI — Document Intelligence Pipeline

## Purpose & Use Case
Automates first-pass review of invoices, purchase orders and contracts for a firm's
Accounts Payable (AP) and Legal teams. A user uploads a PDF / scan / handwritten page;
the system classifies it, extracts structured fields and line items, validates them
against business rules, and lets reviewers ask questions with source citations.
Humans review only what is flagged, instead of reading every document.

## Tech Stack
| Layer | Choice |
|---|---|
| API | Python, FastAPI, JWT (short-lived access token + refresh endpoint) |
| OCR / parsing | Docling (primary), PaddleOCR (fallback + all handwritten docs) |
| Embeddings | Sentence Transformers |
| Vector store | FAISS (primary), Chroma (secondary, swappable) |
| LLMs | Gemini `gemini-2.5-flash` (primary), Mistral (fallback / reconciliation) |
| Frontend | Streamlit, multi-page, talks to the API only (never the DB directly) |
| Database | PostgreSQL via SQLAlchemy ORM |
| Tests | pytest |

## Pipeline Flow
```
upload -> validate file (magic bytes, size) -> layout analysis -> OCR (Docling | PaddleOCR)
  -> classify (invoice/contract/PO) -> extract key-values + tables
  -> validation agent -> chunk + embed -> vector store -> RAG Q&A with citations
```
Every stage logs start/end/duration/status and writes its result to PostgreSQL.

## AI Model Routing, Retry & Fallback
All model calls go through `app/llm/router.py`. No other module imports a provider SDK.

**Routing by feature**
| Feature | Models | Why |
|---|---|---|
| Classification | Gemini alone | Cheap, single-label task |
| RAG answers | Gemini alone | Needs grounding in retrieved chunks, not consensus |
| Field extraction | Gemini AND Mistral, reconciled | Money/legal values are high-stakes |

**Retry (applies to every LLM and OCR call)**
- Max 3 attempts, exponential backoff with jitter (e.g. 1s, 2s, 4s).
- Explicit per-call timeout; a timeout counts as a failed attempt.
- Retry only transient errors (timeout, 429, 5xx, network). Never retry 4xx validation errors.

**Fallback (single-model features)**
1. Call Gemini with retry. Success -> done.
2. If Gemini exhausts retries (error, timeout, rate limit) -> call Mistral with the same retry policy.
3. If Mistral also fails -> raise `ModelUnavailableError`; the document is marked `failed` with a reason, never left hanging.
Mistral is NEVER called when Gemini succeeds.

**Reconciliation (dual-model features)**
- Run both models with retry; compare field by field after normalization (dates, currency, whitespace).
- Agree -> accept, high confidence. Disagree -> prefer the value that passes validation rules;
  otherwise keep Gemini's value, lower confidence, and flag the field for human review.
- If one model fails after retries, use the other, cap confidence, and log a WARNING.

**OCR routing**
- Handwriting detected -> PaddleOCR directly.
- Otherwise Docling; if Docling fails or returns empty/low-confidence text after retries -> PaddleOCR.
- Layout analysis runs before extraction; its output guides table extraction.

**Cost tracking**: every LLM call records model, input/output tokens, estimated USD
(price table in config). Totals are summarized per document and stored on the document row.

## Security & Data Handling
- Secrets only from environment / `.env`; never hardcoded, never logged.
- Logs contain IDs, stage names, durations, counts, token usage — never document text or raw fields.
- Sensitive extracted fields (e.g. account numbers) live only in PostgreSQL, behind JWT-protected
  endpoints; API responses mask them unless the role allows full access.
- Uploads validated by magic bytes (not extension or client MIME) and a max size before any processing.
- Every external call (OCR, LLM, DB) is wrapped: errors are logged, mapped to a clear API error, no silent failures, no unbounded waits.

## Evaluation Pipeline
- `eval/dataset/` holds a small labeled set: document files plus `labels.json` with expected fields.
- `python run_eval.py` (project root) processes each doc, compares fields (exact + normalized match),
  and writes per-field and overall accuracy to `eval/reports/` and the DB (shown on the dashboard).
- Re-run after every change; `pytest -m eval` runs it with a minimum-accuracy threshold.

## Code Style (strict)
- Keep every file under ~200 words of code; split into a new module and import when exceeded.
- Readable over clever: descriptive names, short functions, no deep nesting (use early returns).
- Comment (one line) only when the "why" is not obvious.
