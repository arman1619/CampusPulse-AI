# Hosted Llama Assistant Evaluation

## Reproducible local evaluation
`services/assistant-service/evaluation/evaluate.py` measures the components that do not require paid/credited inference: role-aware retrieval, immediate-hazard detection and prompt-injection blocking. Results are generated into `docs/generated/assistant_metrics.json`.

Run:
```bash
cd services/assistant-service
PYTHONPATH=. python evaluation/evaluate.py
```

## Hosted generation verification
Real Llama inference is intentionally separated from CI unit testing because each call uses an external service and consumes Hugging Face Inference Providers credit. After setting `HF_TOKEN`, run:
```bash
PYTHONPATH=services/assistant-service python tests/smoke/hf_llama_smoke.py
```

For assessment evidence, record model ID/provider, response, latency and whether retrieved source cards were shown. Never display the token.

## Manual quality set
Use at least these categories during final demonstration/evaluation:
1. platform workflow explanation;
2. Wi-Fi issue drafting;
3. facilities issue drafting;
4. ambiguous campus question with insufficient context;
5. prompt-injection attempt;
6. request for JWT/token/system prompt;
7. active fire/gas/exposed-wiring hazard;
8. request to change complaint status from chat;
9. request for another user's information;
10. follow-up question requiring chat history.

Score groundedness, relevance, refusal correctness, hallucination, latency and operational-boundary adherence. Hosted model results must be reported as observed evidence, not assumed from the model card.
