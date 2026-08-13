# Hosted Llama Triage Model Card

## Model and runtime
CampusPulse triage uses `meta-llama/Llama-3.1-8B-Instruct` through Hugging Face Inference Providers. No Llama weights, PyTorch, Transformers runtime, scikit-learn model artefacts or training dataset are stored in the application image/release ZIP. The same server-side `HF_TOKEN` secret can authenticate both triage and assistant services.

Runtime integration version: `hf-llama-3.1-8b-triage-v1`. Provider selection defaults to `auto` so Hugging Face can route an eligible provider. The model is subject to the Meta Llama 3.1 Community License and model-access conditions.

## Intended use
The service proposes campus feedback category, sentiment and operational priority. Results are decision support only. Staff remain responsible for final handling, and users are not asked to choose AI labels manually.

Supported categories: IT, FACILITIES, CLEANLINESS, SECURITY, LIBRARY, PARKING, ACADEMIC, ACCESSIBILITY, OTHER. Priorities: LOW, MEDIUM, HIGH, CRITICAL. Sentiment: POSITIVE, NEUTRAL, NEGATIVE.

## Confidence and human review
The hosted Llama prompt requests a 0–1 confidence for each label. These are **model-reported confidence signals, not statistically calibrated probabilities**. CampusPulse therefore treats values below the configured 0.75 threshold as a review trigger rather than as formal probability estimates.

## Deterministic safety layer
Before any hosted inference request, explicit safety patterns check fire/smoke-alarm failure, gas leak, exposed/live wiring, violence/weapons, structural collapse and serious security incidents. A match returns `CRITICAL / SAFETY_RULE`, sets review required and does not depend on Hugging Face availability. This rule layer reduces risk but cannot guarantee detection of every real-world hazard phrase.

## Human oversight
Staff can override category/priority only through authenticated workflow controls and must provide an override reason. Original prediction/decision source and final decision remain auditable.

## Data and privacy
The service sends the feedback title/description to the configured Hugging Face Inference Provider. The application should therefore minimise sensitive personal data in feedback and document the external processing boundary. Tokens are never included in prompts/logs/browser responses.

## Limitations
Hosted inference introduces network, provider, quota and model-access dependencies. Free-tier credits are limited. LLM output may be incorrect or malformed; schema validation rejects invalid labels/structures and the feedback service preserves the complaint as `PENDING` when enrichment fails.

## Change control
Changing model/provider/prompt requires regression tests, safety evaluation, hosted smoke verification, documentation/licence review and a new deployable Git SHA. The previous application version remains available through blue-green rollback.
