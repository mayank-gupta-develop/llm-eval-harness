def add_case(client, question, expected):
    response = client.post(
        "/test-cases", json={"question": question, "expected_answer": expected}
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_run_scores_pass_and_fail(client):
    france_id = add_case(client, "What is the capital of France?", "Paris")
    japan_id = add_case(client, "What is the capital of Japan?", "Tokyo")

    response = client.post("/runs", json={})
    assert response.status_code == 202
    assert response.json()["status"] == "pending"

    run = client.get(f"/runs/{response.json()['id']}").json()
    assert run["status"] == "completed"
    assert run["avg_score"] == 0.5

    passed = {r["test_case_id"]: r["passed"] for r in run["results"]}
    assert passed[france_id] is True
    assert passed[japan_id] is False


def test_good_pipeline_scores_perfect(client):
    add_case(client, "What is the capital of France?", "Paris")
    add_case(client, "What is the capital of Japan?", "Tokyo")

    run_id = client.post("/runs", json={"pipeline_name": "good_pipeline"}).json()["id"]
    assert client.get(f"/runs/{run_id}").json()["avg_score"] == 1.0


def test_run_with_no_test_cases_returns_400(client):
    response = client.post("/runs", json={})
    assert response.status_code == 400


def test_unknown_pipeline_returns_404(client):
    add_case(client, "What is the capital of France?", "Paris")
    response = client.post("/runs", json={"pipeline_name": "does_not_exist"})
    assert response.status_code == 404


def test_get_run_returns_saved_run(client):
    add_case(client, "What is the capital of France?", "Paris")
    run_id = client.post("/runs", json={}).json()["id"]

    response = client.get(f"/runs/{run_id}")
    assert response.status_code == 200
    assert response.json()["avg_score"] == 1.0


def test_get_missing_run_returns_404(client):
    assert client.get("/runs/999").status_code == 404
