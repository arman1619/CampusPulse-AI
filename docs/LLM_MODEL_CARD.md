# Model Card — CampusPulse Hosted Llama Assistant

## Model
Default: `meta-llama/Llama-3.1-8B-Instruct`, served through Hugging Face Inference Providers.

The application does not redistribute model weights. Operators remain responsible for complying with the upstream Meta Llama 3.1 Community License and Acceptable Use Policy. The user interface displays **Built with Llama** attribution.

Upstream model card: https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct

## Intended use
CampusPulse uses the model for low-risk conversational assistance: explaining platform workflow, improving issue wording, and answering questions grounded in the bundled CampusPulse knowledge corpus.

## Non-intended use
The model is not an emergency service, disciplinary authority, policy source of record, autonomous administrator, medical/legal adviser, or system with permission to change complaints/users/workflow state.

## System architecture
The LLM is wrapped by role-aware retrieval, a constrained system prompt, deterministic prompt-injection/hazard rules, JWT authentication, request correlation, persistence and metrics. Those controls are part of the deployed AI system and should be evaluated together rather than treating the foundation model alone as the application.

## External dependency
Hosted inference requires outbound Internet access, a valid Hugging Face token with Inference Providers permission, accepted access to the gated Meta Llama model, provider capacity and available account credit. These dependencies can cause latency, 429 throttling, 4xx access errors or 5xx provider failures.

## Data handling
Only the user message, limited conversation history, and retrieved CampusPulse context are sent to the hosted inference route. Passwords, access tokens and unnecessary personal information are explicitly prohibited in the UI. The HF token itself is never inserted into prompt content.

## Human oversight
All operational decisions remain outside the LLM. Staff/admin actions use authenticated deterministic APIs with audit records. The chatbot cannot call tools that mutate application data.

## Known limitations
- hallucination and instruction-following errors remain possible;
- external provider behaviour/availability can change;
- Free-tier inference credit is limited and unsuitable as a production capacity guarantee;
- the small authored retrieval corpus may not answer institution-specific questions;
- deterministic injection/hazard rules can miss paraphrases;
- hosted processing introduces privacy/data-residency considerations that must be reviewed for a real institution.

## Change control
Treat changes to model ID, provider, prompt, guardrails, retrieval corpus, generation parameters or API client version as AI-system changes. Rerun assistant unit tests, retrieval/guardrail evaluation, hosted smoke test and selected manual quality/red-team prompts before promotion.
