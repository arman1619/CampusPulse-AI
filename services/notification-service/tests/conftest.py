import os
os.environ["NOTIFICATION_DATABASE_URL"]="sqlite:///./test_notifications.db";os.environ["JWT_SECRET"]="test-secret-1234567890-abcdefghijklmnopqrstuvwxyz";os.environ["INTERNAL_SERVICE_TOKEN"]="internal-test"
from app.database import Base,engine
from app import models  # noqa
import pytest
@pytest.fixture(autouse=True)
def clean():
 Base.metadata.drop_all(engine);Base.metadata.create_all(engine);yield;Base.metadata.drop_all(engine)
