from app.evaluation.types import CaseResult


def _ratio(correct: int, total: int) -> float | None:
    return round(correct / total, 3) if total else None


def _per_field(results: list[CaseResult]) -> dict[str, float | None]:
    counts: dict[str, list[int]] = {}
    for result in results:
        for name, ok in result.field_ok.items():
            pair = counts.setdefault(name, [0, 0])
            pair[0] += ok
            pair[1] += 1
    return {name: _ratio(c, t) for name, (c, t) in sorted(counts.items())}


def aggregate(results: list[CaseResult]) -> dict:
    total_fields = sum(len(r.field_ok) for r in results)
    correct_fields = sum(sum(r.field_ok.values()) for r in results)
    item_checks = [r.items_ok for r in results if r.items_ok is not None]
    confidences = [r.confidence for r in results if r.confidence is not None]
    return {
        "documents": len(results),
        "failed_documents": sum(r.status == "failed" for r in results),
        "overall_accuracy": _ratio(correct_fields, total_fields) or 0.0,
        "doc_type_accuracy": _ratio(sum(r.doc_type_ok for r in results), len(results)),
        "line_item_count_accuracy": _ratio(sum(item_checks), len(item_checks)),
        "per_field_accuracy": _per_field(results),
        "average_confidence": _ratio(sum(confidences), len(confidences)),
        "total_cost_usd": round(sum(r.cost_usd for r in results), 6),
        "average_seconds": round(sum(r.seconds for r in results) / max(len(results), 1), 1),
    }
