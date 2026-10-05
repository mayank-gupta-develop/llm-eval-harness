def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_list_test_cases(client):
    payload = {"question": "What is 2+2?", "expected_answer": "4"}
    created = client.post("/test-cases", json=payload)
    assert created.status_code == 201
    assert created.json()["question"] == "What is 2+2?"

    listed = client.get("/test-cases")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
