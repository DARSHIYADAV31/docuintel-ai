"""CLI: python run_eval.py [--min-accuracy 0.85] [--save-to-db]"""
import argparse
import sys
from pathlib import Path

from app.config import get_settings
from app.db.base import Base
from app.db.repositories import eval_repo
from app.db.session import get_engine, get_session_factory
from app.evaluation.labels import load_cases
from app.evaluation.report import format_summary, write_report
from app.evaluation.runner import evaluate
from app.llm.router import LLMRouter
from app.logging_setup import setup_logging

ROOT = Path(__file__).resolve().parents[3]


def _parse(argv):
    parser = argparse.ArgumentParser(description="Measure extraction accuracy")
    parser.add_argument("--dataset", type=Path, default=ROOT / "eval" / "dataset")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "eval" / "reports")
    parser.add_argument("--min-accuracy", type=float, default=0.85)
    parser.add_argument("--save-to-db", action="store_true")
    return parser.parse_args(argv)


def _save_to_db(summary: dict) -> None:
    Base.metadata.create_all(get_engine())
    db = get_session_factory()()
    try:
        eval_repo.save_run(db, summary)
    finally:
        db.close()


def main(argv=None) -> int:
    args = _parse(argv)
    settings = get_settings()
    setup_logging(settings.log_level)
    if not (settings.gemini_api_key and settings.mistral_api_key):
        print("GEMINI_API_KEY and MISTRAL_API_KEY must be set in .env")
        return 2
    report = evaluate(load_cases(args.dataset), LLMRouter)
    path = write_report(report, args.report_dir)
    print(format_summary(report))
    print(f"Report: {path}")
    if args.save_to_db:
        _save_to_db(report["summary"])
    return 0 if report["summary"]["overall_accuracy"] >= args.min_accuracy else 1


if __name__ == "__main__":
    sys.exit(main())
