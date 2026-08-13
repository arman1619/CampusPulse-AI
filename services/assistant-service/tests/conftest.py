import os
os.environ["ASSISTANT_DATABASE_URL"] = "sqlite:///./test_assistant.db"
os.environ["ASSISTANT_BACKEND"] = "template"
os.environ["ASSISTANT_REQUIRE_LLM"] = "false"
os.environ["JWT_SECRET"] = "test-secret-0123456789abcdef-0123456789abcdef"

from pathlib import Path
import jwt
import pytest
from fastapi.testclient import TestClient
from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def token():
    return jwt.encode({"sub": "11111111-1111-1111-1111-111111111111", "role": "STUDENT", "email": "student@example.com"}, "test-secret-0123456789abcdef-0123456789abcdef", algorithm="HS256")
