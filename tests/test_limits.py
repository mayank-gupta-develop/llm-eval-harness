def test_test_case_text_is_length_limited(client):
    too_long = "x" * 501
    assert client.post("/test-cases", json={"question": too_long, "expected_answer": "a"}).status_code == 422
    assert client.post("/test-cases", json={"question": "q", "expected_answer": too_long}).status_code == 422
    assert client.post("/test-cases", json={"question": "x" * 500, "expected_answer": "a"}).status_code == 201
