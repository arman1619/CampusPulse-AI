from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str | None = None

    @field_validator("message")
    @classmethod
    def meaningful_message(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("message cannot be blank")
        return text


class Citation(BaseModel):
    id: str
    title: str
    score: float


class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    answer: str
    citations: list[Citation]
    model_id: str
    backend: str
    safety_notice: str | None = None
    generated_at: datetime


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    backend: str | None = None
    model_id: str | None = None
    citations: list[dict] = []
    created_at: datetime


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class SessionDetail(SessionOut):
    messages: list[MessageOut]
