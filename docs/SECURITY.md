# Security Architecture

## Identity and authorization
Passwords are bcrypt-hashed; JWTs carry user/role claims with expiry; inactive users are rejected. RBAC is enforced in FastAPI dependencies/domain logic, not merely hidden in React. Students cannot use staff/admin operations or retrieve another student's protected resources. Assistant sessions are similarly owner-scoped.

## Secret management
`.env` is excluded from source/release packaging. Local `.env.example` contains development placeholders only. AWS Terraform generates strong database/JWT/internal values and stores them in Secrets Manager. Elastic Beanstalk references individual secret JSON keys as runtime environment secrets, so the deployable Compose bundle contains variable names rather than credentials. ECR/account identifiers are configuration, not hard-coded secrets.

## Network/data boundaries
Nginx is the public application entry point. Service ports remain on the internal Compose network by default. RDS is private and its security group accepts PostgreSQL only from the application tier. Microservices do not directly query another service's database.

## LLM-specific controls
- only the minimum role-eligible retrieval context and user request are sent to the hosted inference provider;
- role-aware retrieval constrains which knowledge chunks can enter a prompt;
- prompt-injection patterns block common attempts to reveal secrets/system instructions;
- immediate-hazard patterns bypass generation and prioritise human emergency response;
- system prompt prohibits invented campus-specific policy/contacts/actions;
- assistant has no write/tool capability to mutate users/issues;
- session ownership is enforced server-side;
- source cards disclose retrieved grounding context;
- model/backend metadata is visible for audit/demo.

These are defence-in-depth controls, not proof against all prompt injection, hallucination or misuse. The hosted LLM can produce inaccurate or biased output and must remain assistive.

## Application security
Pydantic validates request schemas. SQLAlchemy/psycopg parameterisation is used for data values; the database bootstrap uses psycopg identifier quoting. CORS is environment configured. Errors avoid returning Python traces in the normal API. Request logs exclude passwords, tokens and DB passwords.

## CI/DevSecOps controls
Jenkins runs Ruff, ESLint, Bandit, `pip-audit`, `npm audit` and Trivy after functional tests and before cloud promotion. ECR repositories enable scan-on-push and immutable tags. Security findings require triage; the intended release policy blocks known critical findings rather than automatically ignoring them.

## Supply-chain considerations
The assistant invokes a third-party Hugging Face Inference Provider at runtime. `HF_TOKEN` is never logged, committed or rendered into deployment artefacts; locally it lives only in `.env`, while AWS injects it from Secrets Manager. Prompt/context data sent for inference crosses the application trust boundary, so only the minimum retrieved context is transmitted. Provider/model changes require renewed licence/privacy review, regression tests and evaluation.

## Remaining limitations / production hardening
Institutional deployment should add TLS/ACM, WAF/rate limiting, enterprise SSO/OIDC, secret rotation procedures, central SIEM retention, DB Multi-AZ/deletion protection, backup restore testing, formal privacy retention, dependency update automation, penetration testing and more comprehensive LLM red-team evaluation.
