from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import EvaluationRun


def save_run(db: Session, summary: dict) -> EvaluationRun:
    run = EvaluationRun(overall_accuracy=summary["overall_accuracy"], summary=summary)
    db.add(run)
    db.commit()
    return run


def latest_run(db: Session) -> EvaluationRun | None:
    return db.scalar(select(EvaluationRun).order_by(EvaluationRun.id.desc()).limit(1))
