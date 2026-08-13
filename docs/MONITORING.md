# Monitoring and Logging

## Request correlation and structured logs
FastAPI middleware accepts or generates `X-Request-ID`, returns it to callers and records it in JSON-compatible request logs with service, method, path, status and latency. Inter-service clients propagate the request ID so a feedback submission can be followed across feedback → AI → notification. Sensitive authentication/database values must never be emitted.

## Prometheus metrics
Each backend exposes `/metrics`. Key families include request count, latency and failures. AI triage exposes inference volume/latency. The assistant additionally emits generation count/latency and guardrail-event counters split by event type. `devops/monitoring/prometheus.yml` scrapes all five backend services.

## Grafana
The provisioned local dashboard visualises service request volume/error/latency, triage inference and assistant generation/guardrail activity. Charts are operational evidence only; production SLOs/thresholds should be derived from measured workloads rather than invented numbers.

## AWS CloudWatch
Elastic Beanstalk enhanced health and log streaming are enabled by Terraform. CloudWatch alarms cover degraded Beanstalk environment health and sustained RDS CPU, with an SNS alarm topic and optional email subscription. Gateway/container logs are available to the Beanstalk host logging path and should be collected/retained according to the environment policy.

Recommended production extensions include ALB 5xx/target-response-time alarms, RDS free storage/connections, synthetic external checks and alert routing. Those should be enabled after confirming the exact production load-balancer/resources rather than hard-coding guessed identifiers.

## Demonstration evidence
Show Prometheus targets UP, Grafana panels changing after requests, an assistant guardrail counter increasing, `X-Request-ID` in API/log output, and CloudWatch/Beanstalk enhanced health in AWS. Do not claim CloudWatch evidence until a real environment exists.
