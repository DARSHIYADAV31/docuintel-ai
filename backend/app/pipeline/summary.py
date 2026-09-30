from dataclasses import asdict

from app.llm.cost_tracker import CostTracker


def build_summary(tracker: CostTracker, durations: dict, layout=None,
                  ocr_engine: str | None = None) -> dict:
    """Per-document totals: LLM tokens and cost, stage timings, layout. No content."""
    return {
        "llm": tracker.summary(),
        "stage_seconds": durations,
        "layout": asdict(layout) if layout else None,
        "ocr_engine": ocr_engine,
    }
