"""Deterministic assistant evaluation that does not consume hosted LLM quota.

It evaluates retrieval quality and guardrail coverage. Hosted Llama generation is a
separate opt-in smoke test because it requires network access, model permission and
provider quota.
"""
from __future__ import annotations

import json
from pathlib import Path

from app.guardrails import evaluate_user_message
from app.retrieval import KnowledgeRetriever

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evaluation" / "assistant_eval_cases.json"
OUTPUT = ROOT.parents[1] / "docs" / "generated" / "assistant_metrics.json"


def reciprocal_rank(ids: list[str], expected: str) -> float:
    try:
        return 1.0 / (ids.index(expected) + 1)
    except ValueError:
        return 0.0


def main() -> None:
    cases = json.loads(CASES.read_text())
    from app.config import settings
    retriever = KnowledgeRetriever(settings.knowledge_path)
    hits = 0
    rr_total = 0.0
    retrieval_results = []
    for case in cases["retrieval"]:
        results = retriever.retrieve(case["query"], role=case["role"], top_k=3)
        ids = [r["id"] for r in results]
        hit = case["expected"] in ids
        hits += int(hit)
        rr_total += reciprocal_rank(ids, case["expected"])
        retrieval_results.append({**case, "top3": ids, "hit": hit})

    hazard_hits = sum(bool(evaluate_user_message(text).safety_notice) for text in cases["hazards"])
    injection_hits = sum(bool(evaluate_user_message(text).blocked) for text in cases["prompt_injection"])
    metrics = {
        "evaluation_scope": "deterministic retrieval and guardrail evaluation; no LLM generation scoring",
        "retrieval_cases": len(cases["retrieval"]),
        "retrieval_hit_at_3": round(hits / len(cases["retrieval"]), 4),
        "retrieval_mrr_at_3": round(rr_total / len(cases["retrieval"]), 4),
        "safety_hazard_recall": round(hazard_hits / len(cases["hazards"]), 4),
        "prompt_injection_block_rate": round(injection_hits / len(cases["prompt_injection"]), 4),
        "retrieval_details": retrieval_results,
        "limitations": [
            "Synthetic evaluation prompts are small and are not evidence of production safety.",
            "Hosted-model factuality, latency and groundedness require a real Hugging Face inference smoke/manual evaluation with valid access and quota."
        ]
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(metrics, indent=2))
    print(json.dumps({k: v for k, v in metrics.items() if k != "retrieval_details"}, indent=2))


if __name__ == "__main__":
    main()
