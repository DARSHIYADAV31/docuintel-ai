from dataclasses import dataclass


@dataclass
class LLMResult:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
