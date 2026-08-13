import pytest
from fastapi import HTTPException
from app.domain import validate_transition
def test_valid_transition():validate_transition("SUBMITTED","ASSIGNED")
def test_invalid_transition():
 with pytest.raises(HTTPException) as exc:validate_transition("SUBMITTED","RESOLVED")
 assert exc.value.status_code==409
