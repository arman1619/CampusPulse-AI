import os
os.environ["FEEDBACK_DATABASE_URL"]="sqlite:///./test_feedback.db";os.environ["JWT_SECRET"]="test-secret-1234567890-abcdefghijklmnopqrstuvwxyz";os.environ["AI_SERVICE_URL"]="http://127.0.0.1:9";os.environ["NOTIFICATION_SERVICE_URL"]="http://127.0.0.1:9"
from app.database import Base,engine
from app import models  # noqa
import pytest
@pytest.fixture(autouse=True)
def clean():
 Base.metadata.drop_all(engine);Base.metadata.create_all(engine);yield;Base.metadata.drop_all(engine)
