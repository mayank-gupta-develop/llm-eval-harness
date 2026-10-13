def test_write_without_key_is_rejected(anon_client):
    r = anon_client.post("/test-cases", json={"question": "q", "expected_answer": "a"})
    assert r.status_code == 401


def test_write_with_wrong_key_is_rejected(anon_client):
    r = anon_client.post("/runs", json={}, headers={"x-api-key": "wrong"})
    assert r.status_code == 401


def test_reads_stay_open(anon_client):
    assert anon_client.get("/test-cases").status_code == 200
    assert anon_client.get("/health").status_code == 200


def test_writes_rejected_when_server_has_no_key(client, monkeypatch):
    monkeypatch.delenv("API_KEY")
    r = client.post("/test-cases", json={"question": "q", "expected_answer": "a"})
    assert r.status_code == 401
