from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from .auth import actor_from_request
from .config import settings
from .database import get_db
from .llm import backend_status
from .observability import RequestContextMiddleware, configure_logging, metrics_response
from .schemas import ChatRequest, ChatResponse, Citation, MessageOut, SessionDetail, SessionOut
from .service import chat, delete_session, list_sessions, session_detail

configure_logging(settings.log_level)
app = FastAPI(title="CampusPulse Hosted Llama Assistant Service", version="4.0.0")
app.add_middleware(RequestContextMiddleware, service_name="assistant-service")


@app.get("/health")
@app.get("/api/assistant/health")
def health():
    return {"status": "ok", "service": "assistant-service", "version": "4.0.0"}


@app.get("/ready")
@app.get("/api/assistant/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        model = backend_status()
        if not model["ready"]:
            raise HTTPException(
                status_code=503,
                detail={"database": "ready", "assistant": "HF_TOKEN/model/provider configuration required"},
            )
        return {"status": "ready", "database": "ready", **model}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Assistant database unavailable") from exc


@app.get("/metrics")
def metrics():
    return metrics_response()


@app.get("/api/assistant/model-info")
def model_info():
    return {
        **backend_status(),
        "provider_name": "Hugging Face Inference Providers",
        "model_id": settings.assistant_model_id,
        "license": "Llama 3.1 Community License",
        "runtime_mode": "hosted-api",
        "grounding": "Dependency-free TF-IDF retrieval over bundled CampusPulse knowledge base",
        "human_oversight": "required for policy, safety and operational decisions",
        "token_stored_in_application": False,
    }


@app.post("/api/assistant/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest, request: Request, db: Session = Depends(get_db)):
    actor = actor_from_request(request)
    session, message, safety_notice = chat(db, actor, request, payload.message, payload.session_id)
    return ChatResponse(
        session_id=session.id,
        message_id=message.id,
        answer=message.content,
        citations=[Citation(**item) for item in message.citations],
        model_id=message.model_id or settings.assistant_model_id,
        backend=message.backend or "unknown",
        safety_notice=safety_notice,
        generated_at=message.created_at,
    )


@app.get("/api/assistant/sessions", response_model=list[SessionOut])
def sessions_endpoint(request: Request, db: Session = Depends(get_db)):
    actor = actor_from_request(request)
    return [SessionOut(id=s.id, title=s.title, created_at=s.created_at, updated_at=s.updated_at) for s in list_sessions(db, actor)]


@app.get("/api/assistant/sessions/{session_id}", response_model=SessionDetail)
def session_endpoint(session_id: str, request: Request, db: Session = Depends(get_db)):
    actor = actor_from_request(request)
    session = session_detail(db, session_id, actor)
    return SessionDetail(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=[
            MessageOut(
                id=m.id,
                role=m.role,
                content=m.content,
                backend=m.backend,
                model_id=m.model_id,
                citations=m.citations,
                created_at=m.created_at,
            )
            for m in session.messages
        ],
    )


@app.delete("/api/assistant/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session_endpoint(session_id: str, request: Request, db: Session = Depends(get_db)):
    actor = actor_from_request(request)
    delete_session(db, session_id, actor)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
