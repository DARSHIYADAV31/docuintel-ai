from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import DashboardOut, DocumentSummary, EvaluationOut
from app.auth.dependencies import get_current_user
from app.db.models import User
from app.db.repositories import dashboard_repo, document_repo, eval_repo
from app.db.session import get_db

router = APIRouter(tags=["dashboard"])


def _total_cost(documents) -> float:
    costs = ((d.processing_summary or {}).get("llm", {}).get("estimated_usd", 0)
             for d in documents)
    return round(sum(costs), 6)


def _latest_evaluation(db: Session) -> EvaluationOut | None:
    run = eval_repo.latest_run(db)
    if run is None:
        return None
    s = run.summary
    return EvaluationOut(created_at=run.created_at, overall_accuracy=run.overall_accuracy,
                         doc_type_accuracy=s.get("doc_type_accuracy"),
                         per_field_accuracy=s.get("per_field_accuracy", {}))


@router.get("/dashboard")
def dashboard(user: User = Depends(get_current_user),
              db: Session = Depends(get_db)) -> DashboardOut:
    documents = document_repo.list_owned(db, user.id)
    flagged = dashboard_repo.flagged_documents(db, user.id)
    return DashboardOut(
        total_documents=len(documents),
        by_status=dashboard_repo.status_counts(db, user.id),
        average_confidence=dashboard_repo.average_confidence(db, user.id),
        issue_counts=dashboard_repo.issue_counts(db, user.id),
        total_cost_usd=_total_cost(documents),
        flagged_documents=[DocumentSummary.model_validate(d) for d in flagged],
        latest_evaluation=_latest_evaluation(db),
    )
