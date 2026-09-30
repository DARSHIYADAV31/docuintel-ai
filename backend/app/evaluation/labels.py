import json
from pathlib import Path

from app.errors import DocuIntelError
from app.evaluation.types import Case


def load_cases(dataset_dir: Path) -> list[Case]:
    labels_path = dataset_dir / "labels.json"
    if not labels_path.exists():
        raise DocuIntelError(f"No labels.json in {dataset_dir}")
    cases = []
    for entry in json.loads(labels_path.read_text(encoding="utf-8"))["cases"]:
        path = dataset_dir / entry["file"]
        if not path.exists():
            raise DocuIntelError(f"Labeled file is missing: {entry['file']}")
        cases.append(Case(path, entry["doc_type"], entry["fields"],
                          entry.get("line_item_count"), entry.get("handwritten", False)))
    return cases
