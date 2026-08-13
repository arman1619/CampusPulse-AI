from app.retrieval import get_retriever


def test_retrieval_finds_status_workflow():
    results = get_retriever().retrieve("What does resolved and reopened status mean?", "STUDENT", 3)
    assert results
    assert any(item["id"] == "KB-002" for item in results)


def test_role_scoped_knowledge_is_not_returned_to_student():
    results = get_retriever().retrieve("How do administrators manage users and audit records?", "STUDENT", 10)
    assert all(item["id"] != "KB-008" for item in results)
