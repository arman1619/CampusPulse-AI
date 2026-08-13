# Database Architecture

## Ownership
A single PostgreSQL server/RDS instance hosts four logical databases:
- `campuspulse_auth` — users and identity/audit state;
- `campuspulse_feedback` — issues, comments, workflow/status history, AI decisions and feedback audit;
- `campuspulse_notifications` — in-app notification state;
- `campuspulse_assistant` — chat sessions/messages and retrieved-source metadata.

The hosted classification AI service is stateless and stores no local model artefacts. Cross-service IDs are UUIDs exchanged over APIs; no cross-database foreign keys couple service ownership.

## Migrations
Auth, feedback, notification and assistant services each include their own Alembic migration history and run `alembic upgrade head` during container startup. AWS uses an idempotent one-shot database bootstrap before those migrations so the logical databases exist on a fresh RDS instance.

## RDS design
Terraform places RDS in private subnets and limits port 5432 ingress to the application security group. Storage encryption and seven-day backup retention are enabled in the demonstration baseline. Multi-AZ and deletion protection are configurable because they materially increase resilience/cost and should be selected according to the demonstration/production objective.

## Trade-off
A database/server per microservice provides stronger blast-radius/isolation and independent scaling. One RDS instance with logical databases materially reduces university demonstration cost while retaining clear ownership boundaries. The architecture can split instances later because services do not query each other's tables directly.
