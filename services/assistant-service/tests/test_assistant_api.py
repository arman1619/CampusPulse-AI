def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_chat_requires_authentication(client):
    response = client.post("/api/assistant/chat", json={"message": "How do I submit feedback?"})
    assert response.status_code == 401


def test_chat_creates_persistent_session(client, token):
    response = client.post("/api/assistant/chat", headers=auth(token), json={"message": "How do I submit feedback?"})
    assert response.status_code == 200
    body = response.json()
    assert body["session_id"]
    assert body["citations"]
    assert body["backend"] == "grounded-template"
    detail = client.get(f"/api/assistant/sessions/{body['session_id']}", headers=auth(token))
    assert detail.status_code == 200
    assert [m["role"] for m in detail.json()["messages"]] == ["user", "assistant"]


def test_safety_message_bypasses_llm(client, token):
    response = client.post("/api/assistant/chat", headers=auth(token), json={"message": "There is an active fire in the library"})
    assert response.status_code == 200
    body = response.json()
    assert body["backend"] == "guardrail"
    assert body["safety_notice"]


def test_sessions_are_user_isolated(client, token):
    created = client.post("/api/assistant/chat", headers=auth(token), json={"message": "Explain AI review"}).json()
    import jwt
    other = jwt.encode({"sub": "22222222-2222-2222-2222-222222222222", "role": "STUDENT"}, "test-secret-0123456789abcdef-0123456789abcdef", algorithm="HS256")
    response = client.get(f"/api/assistant/sessions/{created['session_id']}", headers=auth(other))
    assert response.status_code == 404
