# Hosted AI Triage Evaluation

CampusPulse intentionally separates **quota-free deterministic controls** from **live hosted-model quality verification**.

Executed command:
```bash
cd services/ai-service
PYTHONPATH=. python evaluation/evaluate.py
```

The generated `docs/generated/ai_hosted_metrics.json` evaluates safety-rule recall/false positives and strict hosted-response JSON parsing without consuming external inference credits. Current executed results are recorded in `docs/TEST_REPORT.md`.

The suite does **not** claim predictive accuracy for Meta Llama 3.1. A live LLM is non-deterministic and provider-dependent. Real verification is available through:
```bash
PYTHONPATH=services/ai-service python tests/smoke/hf_llama_triage_smoke.py
```
This requires `HF_TOKEN`, accepted Meta model access, available Hugging Face Inference Providers credit/quota and outbound Internet.

For assessment evidence, manually test representative IT/facilities/cleanliness/security/accessibility/positive/ambiguous complaints and record model output, decision source, review flag and any staff override. Treat model-reported confidence as a review signal, not calibrated probability.
