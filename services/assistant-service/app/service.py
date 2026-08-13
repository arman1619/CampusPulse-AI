import json
import time
from datetime import datetime, timezone
from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from .auth import Actor
from .config import settings
from .guardrails import evaluate_user_message
from .llm import get_backend
from .models import ChatMessage, ChatSession
from .observability import GUARDRAIL_EVENTS, LLM_LATENCY, LLM_REQUESTS
from .retrieval import get_retriever


def _get_session(db: Session, session_id: str, actor: Actor) -> ChatSession:
    session = db.get(ChatSession, session_id)
    if not session or session.user_id != actor.id:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


def list_sessions(db: Session, actor: Actor) -> list[ChatSession]:
    return list(db.scalars(select(ChatSession).where(ChatSession.user_id == actor.id).order_by(ChatSession.updated_at.desc())).all())


def session_detail(db: Session, session_id: str, actor: Actor) -> ChatSession:
    return _get_session(db, session_id, actor)


def delete_session(db: Session, session_id: str, actor: Actor) -> None:
    session = _get_session(db, session_id, actor)
    db.delete(session)
    db.commit()


def chat(db: Session, actor: Actor, request: Request, message: str, session_id: str | None) -> tuple[ChatSession, ChatMessage, str | None]:
    message = message.strip()[: settings.assistant_max_input_chars]
    if session_id:
        session = _get_session(db, session_id, actor)
    else:
        title = message[:72] + ("…" if len(message) > 72 else "")
        session = ChatSession(user_id=actor.id, user_role=actor.role, title=title)
        db.add(session)
        db.flush()
    user_message = ChatMessage(session_id=session.id, role="user", content=message, request_id=getattr(request.state, "request_id", None))
    db.add(user_message)
    db.flush()

    guard = evaluate_user_message(message)
    context = get_retriever().retrieve(message, actor.role, settings.assistant_top_k_context)
    backend = get_backend()
    safety_notice = guard.safety_notice
    if guard.blocked:
        GUARDRAIL_EVENTS.labels("prompt_injection").inc()
    if guard.safety_notice:
        GUARDRAIL_EVENTS.labels("safety_hazard").inc()

    if guard.direct_answer:
        answer = guard.direct_answer
        backend_name = "guardrail"
        model_id = "deterministic-safety-layer"
    else:
        history = [{"role": m.role, "content": m.content} for m in session.messages if m.id != user_message.id]
        started = time.perf_counter()
        try:
            answer = backend.generate(message=message, context=context, history=history)
            LLM_REQUESTS.labels(backend.name, "success").inc()
        except Exception as exc:
            LLM_REQUESTS.labels(backend.name, "failure").inc()
            if settings.assistant_require_llm:
                raise HTTPException(status_code=503, detail="Hosted Llama service is unavailable. Check HF_TOKEN, model access, provider quota, and network connectivity, then retry.") from exc
            from .llm import GroundedTemplateBackend
            fallback = GroundedTemplateBackend()
            answer = fallback.generate(message=message, context=context, history=history)
            backend = fallback
        finally:
            LLM_LATENCY.labels(backend.name).observe(time.perf_counter() - started)
        backend_name = backend.name
        model_id = backend.model_id

    citations = [{"id": c["id"], "title": c["title"], "score": c["score"]} for c in context]
    assistant_message = ChatMessage(
        session_id=session.id, role="assistant", content=answer, backend=backend_name, model_id=model_id,
        citations_json=json.dumps(citations), request_id=getattr(request.state, "request_id", None),
    )
    session.updated_at = datetime.now(timezone.utc)
    db.add(assistant_message)
    db.commit()
    db.refresh(session)
    db.refresh(assistant_message)
    return session, assistant_message, safety_notice
