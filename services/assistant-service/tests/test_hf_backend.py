from types import SimpleNamespace

from app.config import settings
from app.llm import HuggingFaceAPIBackend


class FakeInferenceClient:
    def __init__(self, answer: str = "Use the feedback form and include the affected location."):
        self.answer = answer
        self.calls = []

    def chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        message = SimpleNamespace(content=self.answer)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


def test_hosted_hf_backend_builds_grounded_chat_request(monkeypatch):
    monkeypatch.setattr(settings, "hf_token", "hf_test_token_not_real")
    monkeypatch.setattr(settings, "assistant_model_id", "meta-llama/Llama-3.1-8B-Instruct")
    monkeypatch.setattr(settings, "assistant_provider", "auto")
    backend = HuggingFaceAPIBackend()
    fake = FakeInferenceClient()
    backend._client = fake
    answer = backend.generate(
        message="How do I report Wi-Fi issues?",
        context=[{"id": "kb-wifi", "title": "Wi-Fi reporting", "content": "Include building and floor."}],
        history=[],
    )
    assert "feedback form" in answer
    assert fake.calls[0]["model"] == "meta-llama/Llama-3.1-8B-Instruct"
    prompt = fake.calls[0]["messages"][-1]["content"]
    assert "Verified CampusPulse context" in prompt
    assert "Include building and floor" in prompt


def test_hosted_hf_backend_requires_runtime_token(monkeypatch):
    monkeypatch.setattr(settings, "hf_token", "")
    backend = HuggingFaceAPIBackend()
    assert backend.is_ready() is False
