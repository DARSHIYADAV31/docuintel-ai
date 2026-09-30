from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Case:
    path: Path
    doc_type: str
    fields: dict[str, str]
    line_item_count: int | None = None
    handwritten: bool = False


@dataclass
class CaseResult:
    file: str
    status: str
    doc_type_ok: bool
    field_ok: dict[str, bool]
    items_ok: bool | None
    confidence: float | None
    cost_usd: float
    seconds: float
    mismatches: dict[str, dict] = field(default_factory=dict)
