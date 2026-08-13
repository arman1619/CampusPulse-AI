from fastapi import FastAPI, HTTPException

from .analyser import HostedTriageUnavailable, analyse, backend_status
from .config import settings
from .observability import RequestContextMiddleware, configure_logging, metrics_response
from .schemas import AnalyseRequest, AnalyseResponse

configure_logging(settings.log_level)
app = FastAPI(title="CampusPulse Hosted Llama Triage Service", version="3.0.0")
app.add_middleware(RequestContextMiddleware, service_name="ai-service")


@app.get("/api/ai/health")
@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-service", "version": "3.0.0"}


@app.get("/ready")
def ready():
    status = backend_status()
    if not status["ready"]:
        raise HTTPException(503, "hosted triage is not configured")
    return {"status": "ready", **status}


@app.get("/metrics")
def metrics():
    return metrics_response()


@app.post("/api/ai/analyse", response_model=AnalyseResponse)
def analyse_endpoint(payload: AnalyseRequest):
    try:
        return analyse(payload.title, payload.description)
    except HostedTriageUnavailable as exc:
        raise HTTPException(503, "hosted AI triage is temporarily unavailable") from exc


@app.get("/api/ai/model-info")
def model_info():
    return {
        **backend_status(),
        "provider_name": "Hugging Face Inference Providers",
        "runtime_mode": "hosted-api",
        "local_model_weights": False,
        "confidence_note": "LLM-reported confidence is a review signal, not a calibrated probability.",
        "safety_layer": "deterministic critical-hazard rules execute before hosted inference",
        "human_oversight": True,
    }
