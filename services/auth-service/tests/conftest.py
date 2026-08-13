import os
os.environ["AUTH_DATABASE_URL"]="sqlite:///./test_auth.db"
os.environ["JWT_SECRET"]="test-secret-that-is-long-enough-1234567890"
os.environ["SEED_DEMO"]="false"
from app.database import Base, engine
from app import models  # noqa
Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
import pytest
@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(engine); Base.metadata.create_all(engine); yield
