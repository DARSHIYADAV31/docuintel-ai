from app.llm.types import LLMResult

# USD per 1M tokens (input, output); estimates only, update when pricing changes
PRICES = {
    "gemini-2.5-flash": (0.30, 2.50),
    "mistral-small-latest": (0.20, 0.60),
}


def estimate_cost(result: LLMResult) -> float:
    price_in, price_out = PRICES.get(result.model, (0.0, 0.0))
    return (result.input_tokens * price_in + result.output_tokens * price_out) / 1_000_000


class CostTracker:
    """Accumulates token usage and cost for one document."""

    def __init__(self):
        self.calls: list[tuple[str, int, int, float]] = []

    def record(self, result: LLMResult) -> None:
        cost = estimate_cost(result)
        self.calls.append((result.model, result.input_tokens, result.output_tokens, cost))

    def summary(self) -> dict:
        return {
            "calls": len(self.calls),
            "input_tokens": sum(c[1] for c in self.calls),
            "output_tokens": sum(c[2] for c in self.calls),
            "estimated_usd": round(sum(c[3] for c in self.calls), 6),
        }
