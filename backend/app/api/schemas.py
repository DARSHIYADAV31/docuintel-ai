from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FieldOut(BaseModel):
    name: str
    value: str | None
    confidence: float
    flagged: bool


class IssueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    field_name: str
    rule: str
    severity: str
    message: str


class DocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    filename: str
    status: str
    doc_type: str | None
    confidence: float | None
    created_at: datetime


class DocumentDetail(DocumentSummary):
    error_message: str | None
    ocr_engine: str | None
    handwritten: bool
    line_items: list[dict]
    processing_summary: dict | None
    fields: list[FieldOut]
    issues: list[IssueOut]


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class CitationOut(BaseModel):
    chunk_index: int
    snippet: str
    score: float


class AskResponse(BaseModel):
    answer: str
    grounded: bool
    citations: list[CitationOut]


class EvaluationOut(BaseModel):
    created_at: datetime
    overall_accuracy: float
    doc_type_accuracy: float | None
    per_field_accuracy: dict[str, float | None]


class DashboardOut(BaseModel):
    total_documents: int
    by_status: dict[str, int]
    average_confidence: float | None
    issue_counts: dict[str, int]
    total_cost_usd: float
    flagged_documents: list[DocumentSummary]
    latest_evaluation: EvaluationOut | None
