# CampusPulse AI Architecture

## Overall cloud-native application
```mermaid
flowchart LR
 U[Student / Staff / Admin] --> UI[React + Vite + TypeScript]
 UI --> GW[Nginx Gateway]
 GW --> AUTH[Auth :8001]
 GW --> FB[Feedback :8002]
 GW --> AI[AI Triage :8003]
 GW --> N[Notification :8004]
 GW --> AS[LLM Assistant :8005]
 FB -->|analyse| AI
 FB -->|notify| N
 AUTH --> ADB[(campuspulse_auth)]
 FB --> FDB[(campuspulse_feedback)]
 N --> NDB[(campuspulse_notifications)]
 AS --> CDB[(campuspulse_assistant)]
 AS --> KB[(Versioned knowledge corpus)]
 AS --> HF[Hugging Face Inference Providers\nMeta Llama 3.1 8B Instruct]
 ADB & FDB & NDB & CDB --> PG[(PostgreSQL / private RDS)]
```

The gateway is the default ingress. Application services are independently containerised and own their schemas/data. The triage and conversational assistant are intentionally different microservices even though both use hosted Llama: triage has strict schema validation and safety-rule semantics, while free-form assistance has retrieval grounding and conversational guardrails. This preserves independent scaling, failure isolation and testability.

## Feedback submission sequence
```mermaid
sequenceDiagram
 participant S as Student
 participant G as Gateway
 participant F as Feedback Service
 participant D as Feedback DB
 participant A as AI Service
 participant N as Notification Service
 S->>G: POST /api/feedback + JWT + X-Request-ID
 G->>F: Forward request
 F->>D: Persist SUBMITTED issue first
 F->>A: POST /api/ai/analyse (bounded timeout)
 alt AI available
   A-->>F: category/sentiment/priority/confidence/version
   F->>D: Persist AI decision
 else AI unavailable
   F->>D: Preserve issue with PENDING analysis
 end
 F->>N: Internal notification event
 F-->>S: Persisted issue response
```

The reliability invariant is **persist first, enrich second**. AI failure must not destroy a student submission.

## AI triage decision
```mermaid
flowchart TD
 Text[Title + description] --> Rule{Critical safety phrase?}
 Rule -- yes --> Critical[CRITICAL / SAFETY_RULE]
 Rule -- no --> HF[Hugging Face Inference Providers]
 HF --> L[Llama 3.1 8B structured triage]
 L --> C[Category + sentiment + priority]
 C --> Validate[Schema / enum validation]
 Validate --> Conf{Reported confidence < 0.75?}
 Conf -- yes --> Review[needs_review=true]
 Conf -- no --> Auto[needs_review=false]
 Critical --> Review
 Review & Auto --> Store[Persist original hosted outputs]
 Store --> Human[Staff override with reason]
 Human --> Audit[Audit entry]
```

## LLM assistant sequence
```mermaid
sequenceDiagram
 participant U as Authenticated user
 participant A as Assistant Service
 participant G as Guardrails
 participant R as TF-IDF Retriever
 participant K as Knowledge Base
 participant L as HF Llama API
 participant D as Assistant DB
 U->>A: POST /api/assistant/chat
 A->>G: inspect input
 alt prompt injection
   G-->>A: deterministic refusal
 else immediate hazard
   G-->>A: deterministic human-safety guidance
 else ordinary support question
   A->>R: role-scoped retrieval
   R->>K: rank chunks
   K-->>R: top verified context
   A->>L: context + constrained prompt + history
   L-->>A: hosted generated answer
 end
 A->>D: persist user/assistant messages + source metadata
 A-->>U: answer + backend + citations + safety notice
```

## Data architecture
One PostgreSQL server may host four logical databases for the demonstration. This preserves service ownership while avoiding four RDS instances. There are no cross-service database foreign keys. A deployment bootstrap command creates logical databases before data-owning containers execute Alembic migrations.

## CI/CD and AWS deployment
```mermaid
flowchart LR
 Git[GitHub / Git] --> Jenkins[Jenkins Pipeline]
 Git --> CC[Optional CodeCommit mirror]
 CC --> CB[Optional CodeBuild verification]
 Jenkins --> Q[Lint + tests + AI eval + security]
 Q --> Build[Docker build]
 Build --> Trivy[Container scan]
 Trivy --> ECR[ECR immutable SHA tags]
 ECR --> Inactive[Elastic Beanstalk inactive env]
 Inactive --> Smoke[Ready + functional smoke]
 Smoke --> Approval[Promotion gate]
 Approval --> Swap[CNAME swap]
 Swap --> Prod[Production smoke]
 Prod --> CW[CloudWatch logs/health/alarms]
```

Jenkins is the primary release orchestrator because the brief explicitly requires it and its stages are easy to demonstrate. CodeCommit/CodeBuild are provided as an AWS-native mirror/independent verification path so the project demonstrates the named AWS services without replacing the Jenkins learning outcome.

## Blue-green availability model
Version B is deployed to the inactive environment while Version A continues serving production. Traffic switches only after candidate health/smoke verification and a controlled promotion gate. The previous environment is retained long enough for fast CNAME reversal. This uses more temporary capacity than rolling deployment but makes rollback state explicit and demonstrable.

## Observability
All FastAPI services expose liveness/readiness and Prometheus metrics. Structured logs carry `request_id`, service, path, status and latency while excluding passwords/JWT/secrets. Local Prometheus/Grafana gives application-level telemetry; Elastic Beanstalk log streaming and CloudWatch alarms provide the AWS operational path.

## Deliberate trade-offs
- **Elastic Beanstalk vs ECS/EKS:** Beanstalk satisfies the assessed AWS deployment requirement with lower orchestration overhead; ECS/EKS would provide more control but add scope and operational surface.
- **One RDS instance vs database per service:** logical databases retain ownership at lower demonstration cost; stronger isolation/independent scaling may justify separate data platforms in production.
- **Synchronous HTTP vs broker:** HTTP keeps flows inspectable; a broker would improve event decoupling/delivery semantics at higher complexity.
- **Hosted Llama 3.1 8B vs local LLM:** hosted inference avoids shipping multi-GB weights and GPU/CPU runtime dependencies in CampusPulse images, but introduces provider quota, network latency and third-party availability dependencies.
- **TF-IDF RAG vs vector database:** version-controlled TF-IDF retrieval is reproducible and sufficient for a small knowledge corpus; semantic vector search becomes stronger as corpus size/linguistic variability grows.
- **Hugging Face hosted API vs self-hosting:** hosted inference sharply reduces image size and Beanstalk memory pressure; self-hosting provides greater runtime independence/data control but would require model lifecycle, accelerators or substantially larger CPU/RAM capacity.
