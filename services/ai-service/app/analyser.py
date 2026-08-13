from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Protocol

from huggingface_hub import InferenceClient

from .config import settings
from .observability import AI_INFERENCE, AI_LATENCY
from .safety import critical_rule

CATEGORIES = {"IT", "FACILITIES", "CLEANLINESS", "SECURITY", "LIBRARY", "PARKING", "ACADEMIC", "ACCESSIBILITY", "OTHER"}
PRIORITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
SENTIMENTS = {"POSITIVE", "NEUTRAL", "NEGATIVE"}
MODEL_VERSION = "hf-llama-3.1-8b-triage-v1"

SYSTEM_PROMPT = """You are the CampusPulse issue-triage classifier. Return ONLY valid JSON, no Markdown.
Classify campus feedback using exactly these labels:
category: IT, FACILITIES, CLEANLINESS, SECURITY, LIBRARY, PARKING, ACADEMIC, ACCESSIBILITY, OTHER
sentiment: POSITIVE, NEUTRAL, NEGATIVE
priority: LOW, MEDIUM, HIGH, CRITICAL
For each prediction provide a confidence number from 0.0 to 1.0. Do not invent campus facts.
CRITICAL should be reserved for plausible immediate danger or severe security/safety incidents.
Required JSON shape:
{"sentiment":{"label":"NEGATIVE","confidence":0.90},"category":{"label":"IT","confidence":0.90},"priority":{"label":"MEDIUM","confidence":0.85}}
"""


class HostedTriageUnavailable(RuntimeError):
    pass


class TriageBackend(Protocol):
    name: str
    model_id: str

    def classify(self, text: str) -> dict: ...
    def is_ready(self) -> bool: ...


def _confidence(value: object) -> float:
    try:
        return round(min(1.0, max(0.0, float(value))), 4)
    except (TypeError, ValueError):
        raise HostedTriageUnavailable("invalid confidence") from None


def _validate_result(data: dict) -> dict:
    try:
        sentiment = str(data["sentiment"]["label"]).upper()
        category = str(data["category"]["label"]).upper()
        priority = str(data["priority"]["label"]).upper()
        if sentiment not in SENTIMENTS or category not in CATEGORIES or priority not in PRIORITIES:
            raise ValueError("invalid label")
        return {
            "sentiment": {"label": sentiment, "confidence": _confidence(data["sentiment"]["confidence"])},
            "category": {"label": category, "confidence": _confidence(data["category"]["confidence"])},
            "priority": {"label": priority, "confidence": _confidence(data["priority"]["confidence"])},
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise HostedTriageUnavailable("invalid hosted triage response") from exc


def _extract_json(text: str) -> dict:
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end <= start:
        raise HostedTriageUnavailable("hosted triage returned no JSON")
    try:
        return json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError as exc:
        raise HostedTriageUnavailable("hosted triage returned invalid JSON") from exc


@dataclass
class DeterministicTestBackend:
    """Quota-free deterministic backend used only in tests/CI, never the production default."""

    name: str = "deterministic-ci"
    model_id: str = "no-local-model"

    def is_ready(self) -> bool:
        return True

    def classify(self, text: str) -> dict:
        t = text.lower()
        if any(k in t for k in ("wi-fi", "wifi", "internet", "network", "computer", "printer", "login")):
            category = "IT"
        elif any(k in t for k in ("library", "book", "study room")):
            category = "LIBRARY"
        elif any(k in t for k in ("dirty", "rubbish", "trash", "clean", "toilet")):
            category = "CLEANLINESS"
        elif any(k in t for k in ("parking", "car park", "vehicle")):
            category = "PARKING"
        elif any(k in t for k in ("security", "threat", "unsafe", "assault")):
            category = "SECURITY"
        elif any(k in t for k in ("lecture", "class", "assessment", "tutor", "course")):
            category = "ACADEMIC"
        elif any(k in t for k in ("wheelchair", "accessible", "accessibility", "lift")):
            category = "ACCESSIBILITY"
        elif any(k in t for k in ("building", "door", "light", "air conditioning", "facility", "wire")):
            category = "FACILITIES"
        else:
            category = "OTHER"
        if any(k in t for k in ("thank you", "helpful", "excellent", "working well", "great service")):
            sentiment = "POSITIVE"
        elif any(k in t for k in ("broken", "failed", "not working", "unsafe", "frustrating", "disconnect")):
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"
        priority = "HIGH" if any(k in t for k in ("urgent", "cannot access", "major outage")) else "MEDIUM"
        conf = 0.92 if category != "OTHER" else 0.60
        return {
            "sentiment": {"label": sentiment, "confidence": 0.90 if sentiment != "NEUTRAL" else 0.72},
            "category": {"label": category, "confidence": conf},
            "priority": {"label": priority, "confidence": 0.82 if priority == "HIGH" else 0.78},
        }


class HuggingFaceTriageBackend:
    name = "huggingface-inference-api"

    def __init__(self) -> None:
        self.model_id = settings.ai_model_id
        self._client: InferenceClient | None = None

    def is_ready(self) -> bool:
        return bool(settings.hf_token.strip() and self.model_id.strip() and settings.ai_provider.strip())

    def _client_instance(self) -> InferenceClient:
        if not self.is_ready():
            raise HostedTriageUnavailable("HF triage is not configured")
        if self._client is None:
            self._client = InferenceClient(
                provider=settings.ai_provider,
                token=settings.hf_token,
                timeout=settings.ai_api_timeout_seconds,
            )
        return self._client

    def classify(self, text: str) -> dict:
        client = self._client_instance()
        attempts = max(0, settings.ai_max_retries) + 1
        retryable = {429, 500, 502, 503, 504}
        for attempt in range(attempts):
            try:
                result = client.chat_completion(
                    model=self.model_id,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Campus feedback:\n{text[:5200]}"},
                    ],
                    max_tokens=settings.ai_max_tokens,
                    temperature=settings.ai_temperature,
                )
                content = str(result.choices[0].message.content or "")
                return _validate_result(_extract_json(content))
            except HostedTriageUnavailable:
                raise
            except Exception as exc:
                status = getattr(getattr(exc, "response", None), "status_code", None)
                if status in retryable and attempt < attempts - 1:
                    time.sleep(settings.ai_retry_backoff_seconds * (2**attempt))
                    continue
                raise HostedTriageUnavailable("hosted triage unavailable") from exc
        raise HostedTriageUnavailable("hosted triage unavailable")


_hf = HuggingFaceTriageBackend()
_ci = DeterministicTestBackend()


def get_backend() -> TriageBackend:
    if settings.ai_backend == "deterministic":
        return _ci
    if _hf.is_ready() or settings.ai_require_llm:
        return _hf
    return _ci


def backend_status() -> dict:
    backend = get_backend()
    configured = _hf.is_ready()
    return {
        "ready": backend.is_ready(),
        "backend": backend.name,
        "provider": settings.ai_provider if backend is _hf else "none",
        "model_id": settings.ai_model_id if backend is _hf else backend.model_id,
        "hosted_model_configured": configured,
        "runtime_network_required": backend is _hf,
        "model_version": MODEL_VERSION,
    }


def analyse(title: str, description: str) -> dict:
    start = time.perf_counter()
    text = f"{title}. {description}".strip()
    rule = critical_rule(text)
    try:
        # Safety-critical wording never depends on external LLM availability.
        if rule:
            AI_INFERENCE.labels("safety_rule").inc()
            return {
                "sentiment": {"label": "NEGATIVE", "confidence": 1.0},
                "category": {"label": "SECURITY" if "SECURITY" in rule or "VIOLENCE" in rule else "FACILITIES", "confidence": 1.0},
                "priority": {"label": "CRITICAL", "confidence": 1.0},
                "needs_review": True,
                "decision_source": "SAFETY_RULE",
                "model_version": MODEL_VERSION,
                "safety_rule": rule,
            }
        result = get_backend().classify(text)
        threshold = settings.ai_confidence_threshold
        needs_review = min(
            result["sentiment"]["confidence"],
            result["category"]["confidence"],
            result["priority"]["confidence"],
        ) < threshold
        AI_INFERENCE.labels("success").inc()
        return {
            **result,
            "needs_review": needs_review,
            "decision_source": "MODEL",
            "model_version": MODEL_VERSION,
            "safety_rule": None,
        }
    except Exception:
        AI_INFERENCE.labels("error").inc()
        raise
    finally:
        AI_LATENCY.observe(time.perf_counter() - start)
