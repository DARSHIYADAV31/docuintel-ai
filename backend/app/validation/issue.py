from dataclasses import dataclass


@dataclass
class Issue:
    field: str
    rule: str
    severity: str  # "error" needs a fix, "warning" needs a look
    message: str
