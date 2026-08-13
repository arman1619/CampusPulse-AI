"""Quota-free evaluation for hosted-Llama triage integration and deterministic safety layer."""
from __future__ import annotations

import json
from pathlib import Path

from app.analyser import _extract_json, _validate_result
from app.safety import critical_rule

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs" / "generated" / "ai_hosted_metrics.json"

HAZARDS = [
    "Fire is visible beside the chemistry lab.",
    "There is a gas leak near the cafeteria.",
    "Exposed electrical wires are hanging at the lab entrance.",
    "A student reported a weapon in the corridor.",
    "The ceiling is collapsing in lecture room 2.",
    "An armed intruder has entered the building.",
    "The fire alarm is not working and smoke is visible.",
    "There is a serious security incident at the main entrance.",
]
NON_HAZARDS = [
    "The Wi-Fi disconnects in Library Level 2.",
    "The printer is out of paper.",
    "The car park is full after 10 am.",
    "The study room is too cold.",
    "The tutorial timetable is confusing.",
    "Please clean the tables in the common room.",
    "The library staff were very helpful.",
    "The lift is slow during lunch time.",
]
SCHEMA_SAMPLES = [
    '{"sentiment":{"label":"NEGATIVE","confidence":0.91},"category":{"label":"IT","confidence":0.88},"priority":{"label":"MEDIUM","confidence":0.80}}',
    '```json\n{"sentiment":{"label":"NEUTRAL","confidence":0.77},"category":{"label":"PARKING","confidence":0.82},"priority":{"label":"LOW","confidence":0.76}}\n```',
    '{"sentiment":{"label":"POSITIVE","confidence":0.93},"category":{"label":"LIBRARY","confidence":0.89},"priority":{"label":"LOW","confidence":0.86}}',
    '{"sentiment":{"label":"NEGATIVE","confidence":0.89},"category":{"label":"ACCESSIBILITY","confidence":0.87},"priority":{"label":"HIGH","confidence":0.84}}',
]


def main() -> None:
    hazard_recall = sum(bool(critical_rule(x)) for x in HAZARDS) / len(HAZARDS)
    false_positives = sum(bool(critical_rule(x)) for x in NON_HAZARDS) / len(NON_HAZARDS)
    schema_pass = 0
    for sample in SCHEMA_SAMPLES:
        try:
            _validate_result(_extract_json(sample))
            schema_pass += 1
        except Exception:
            pass
    metrics = {
        "evaluation_scope": "quota-free hosted-API contract parsing and deterministic safety rules; no claim about live Llama predictive accuracy",
        "safety_hazard_recall": round(hazard_recall, 4),
        "safety_false_positive_rate": round(false_positives, 4),
        "hosted_json_schema_parser_pass_rate": round(schema_pass / len(SCHEMA_SAMPLES), 4),
        "local_model_weights": False,
        "hosted_model": "meta-llama/Llama-3.1-8B-Instruct",
        "limitations": [
            "Live hosted-model quality depends on model/provider behavior and requires a token-backed smoke/manual evaluation.",
            "LLM-reported confidence values are not calibrated probabilities and are used only as human-review signals.",
            "Safety rules reduce risk but cannot guarantee detection of every real-world emergency phrasing.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
