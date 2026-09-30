"""Entry point so evaluation runs from the project root: python run_eval.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.evaluation.run import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
