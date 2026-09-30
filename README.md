# DocuIntel AI

Document intelligence pipeline for invoices, purchase orders and contracts. It automates first-pass review for accounts-payable and legal teams: upload a PDF, scan or handwritten page, and the system classifies it, extracts the key fields and line items, checks them against business rules, and answers questions about it with the source line cited.

## Features

- **OCR:** Docling first, PaddleOCR as fallback and for handwritten documents, with layout analysis before extraction.
- **Multi-model AI with fallback:** Gemini 2.5 Flash is the primary model. Mistral takes over only if Gemini fails. Every call has a timeout and retries with exponential backoff (3 attempts).
- **Dual-model extraction:** Gemini and Mistral both extract the fields. Answers are reconciled field by field with a confidence score, and disagreements are flagged for review.
- **Validation agent:** subtotal plus tax equals total, line items add up, dates are in order, required fields are present.
- **RAG Q&A with citations:** FAISS retrieval (Chroma optional), short answers, and the exact source line shown.
- **Evaluation pipeline:** a labeled test set and a re-runnable command that reports per-field accuracy.
- **Security:** JWT auth with refresh tokens, upload validation by file contents, sensitive fields masked, structured logs that never contain document contents, token and cost tracking per document.

## Tech stack

Python, FastAPI, SQLAlchemy (PostgreSQL or SQLite), Streamlit, Docling, PaddleOCR, Gemini, Mistral, FAISS, Chroma, pytest.

## Setup

1. Install Python 3.11 to 3.13.
2. Create and activate a virtual environment:
   ```
   python -m venv myenv
   myenv\Scripts\Activate.ps1          # Windows PowerShell
   source myenv/bin/activate           # Mac / Linux
   ```
3. Install the packages (large: torch and PaddlePaddle, allow 10 to 30 minutes):
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in:
   ```
   GEMINI_API_KEY=...        # aistudio.google.com/apikey
   MISTRAL_API_KEY=...       # console.mistral.ai
   DATABASE_URL=sqlite:///dev.db
   JWT_SECRET_KEY=...        # python -c "import secrets;print(secrets.token_urlsafe(48))"
   ```
   For PostgreSQL use `postgresql+psycopg://user:password@localhost:5432/docuintel`.

## Run

Backend (terminal 1, from the project folder):
```
uvicorn app.main:app --app-dir backend --port 8000
```

Frontend (terminal 2):
```
streamlit run frontend/Home.py
```

Open http://localhost:8501, create an account, and upload a file from `sample_docs/`. The first upload is slow because the OCR models download once.

## Tests and evaluation

```
pytest                                  # unit and integration tests
python run_eval.py --save-to-db         # accuracy on the labeled set (needs API keys)
```

The bundled dataset in `eval/dataset/` is small and synthetic, so its scores are optimistic. Add real labeled documents to measure real-world accuracy.

## Notes

- Free-tier API keys hit rate limits quickly. Go slowly when testing.
- Embeddings use Gemini by default. Set `EMBEDDING_BACKEND=local` and run `python download_models.py` to use Sentence Transformers instead.
- Never commit `.env`. It is listed in `.gitignore`.
