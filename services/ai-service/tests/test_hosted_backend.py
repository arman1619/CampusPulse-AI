from app import analyser


class Message:
    content = '{"sentiment":{"label":"negative","confidence":0.91},"category":{"label":"it","confidence":0.88},"priority":{"label":"medium","confidence":0.80}}'


class Choice:
    message = Message()


class Result:
    choices = [Choice()]


class FakeClient:
    def chat_completion(self, **kwargs):
        assert kwargs["model"] == analyser.settings.ai_model_id
        return Result()


def test_hosted_backend_parses_json_without_model_weights(monkeypatch):
    backend = analyser.HuggingFaceTriageBackend()
    monkeypatch.setattr(backend, "_client_instance", lambda: FakeClient())
    data = backend.classify("Library Wi-Fi disconnects frequently")
    assert data["category"]["label"] == "IT"
    assert data["priority"]["label"] == "MEDIUM"


def test_json_parser_rejects_invalid_labels():
    bad = '{"sentiment":{"label":"bad","confidence":1},"category":{"label":"IT","confidence":1},"priority":{"label":"LOW","confidence":1}}'
    try:
        analyser._validate_result(analyser._extract_json(bad))
    except analyser.HostedTriageUnavailable:
        return
    raise AssertionError("invalid hosted label was accepted")
