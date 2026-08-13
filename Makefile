SHELL := /bin/bash
.PHONY: dev down test lint ai-evaluate ai-smoke assistant-evaluate assistant-smoke build smoke package observability

dev:
	./scripts/dev-up.sh

down:
	./scripts/dev-down.sh

test:
	./scripts/test-all.sh

lint:
	./scripts/lint-all.sh

ai-evaluate:
	cd services/ai-service && PYTHONPATH=. python evaluation/evaluate.py

ai-smoke:
	PYTHONPATH=services/ai-service python tests/smoke/hf_llama_triage_smoke.py

assistant-evaluate:
	cd services/assistant-service && PYTHONPATH=. python evaluation/evaluate.py

assistant-smoke:
	PYTHONPATH=services/assistant-service python tests/smoke/hf_llama_smoke.py

build:
	docker compose build

smoke:
	python tests/smoke/smoke.py

observability:
	docker compose -f docker-compose.yml -f docker-compose.observability.yml up -d prometheus grafana

package:
	./scripts/package-release.sh
