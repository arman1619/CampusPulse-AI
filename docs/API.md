# API Reference Summary

All browser traffic normally enters through Nginx at `/api/...`. Protected endpoints require `Authorization: Bearer <JWT>`. Request correlation uses `X-Request-ID` and is generated when absent.

## Auth service
`POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`, `GET /api/auth/users` (admin), `PATCH /api/auth/users/{id}/role`, `PATCH /api/auth/users/{id}/active`, health/readiness/metrics.

## Feedback service
CRUD: `POST/GET /api/feedback`, `GET/PATCH/DELETE /api/feedback/{id}`. Workflow: `PATCH /api/feedback/{id}/status`. Comments: `POST/GET /api/feedback/{id}/comments`. AI override: `POST /api/feedback/{id}/override`. Analytics: summary/category/priority/sentiment/status/resolution-time endpoints. Students are server-side restricted to their permitted records.

## AI triage service
`POST /api/ai/analyse`, `GET /api/ai/model-info`, health/readiness/metrics. Output contains sentiment/category/priority labels, confidences, review flag, decision source and model version. Safety-critical matching can force `CRITICAL / SAFETY_RULE`.

## Notification service
`GET /api/notifications`, `GET /api/notifications/unread-count`, `PATCH /api/notifications/{id}/read`, `PATCH /api/notifications/read-all`. Internal creation requires the service token.

## Hosted Llama assistant
`GET /api/assistant/health`, `GET /api/assistant/ready`, `GET /api/assistant/model-info`, `POST /api/assistant/chat`, session list/detail/delete endpoints. The chat endpoint returns `session_id`, generated `answer`, source cards, `model_id`, effective `backend`, safety notice and timestamp.

Example:
```json
{
  "message": "How should I report Wi-Fi that disconnects in Library Level 2?",
  "session_id": null
}
```
The service retrieves role-eligible product knowledge, passes it to the configured Hugging Face-hosted Llama model and persists only the authenticated user's transcript.

## Error contract
Services use HTTP semantics: 400 domain/input errors, 401 missing/invalid authentication, 403 authorization failure, 404 missing resource, 409 conflicts, 422 schema validation, 500 unexpected error and 503 dependency/model readiness failure. Production clients receive safe JSON errors rather than raw stack traces.
