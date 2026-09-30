import json
from pathlib import Path


def write_report(report: dict, report_dir: Path) -> Path:
    """Timestamped file for history, plus latest.json for quick comparison."""
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = report["created_at"][:19].replace(":", "-")
    path = report_dir / f"eval_{stamp}.json"
    text = json.dumps(report, indent=2)
    path.write_text(text, encoding="utf-8")
    (report_dir / "latest.json").write_text(text, encoding="utf-8")
    return path


def format_summary(report: dict) -> str:
    s = report["summary"]
    lines = [
        f"Documents: {s['documents']} (failed: {s['failed_documents']})",
        f"Overall field accuracy: {s['overall_accuracy']:.1%}",
        f"Document type accuracy: {s['doc_type_accuracy']}",
        f"Line item count accuracy: {s['line_item_count_accuracy']}",
        f"Average confidence: {s['average_confidence']}",
        f"Total cost: ${s['total_cost_usd']}",
        "Per field:",
    ]
    lines += [f"  {name}: {acc}" for name, acc in s["per_field_accuracy"].items()]
    return "\n".join(lines)
