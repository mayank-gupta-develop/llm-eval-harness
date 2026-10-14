def test_scorers_disagree_on_seventeen(anon_client):
    r = anon_client.post(
        "/demo/score",
        json={"expected": "7", "candidate": "There are 17 continents."},
    )
    assert r.status_code == 200
    assert r.json() == {"substring": 1.0, "whole_word": 0.0}


def test_bad_input_is_rejected(anon_client):
    r = anon_client.post("/demo/score", json={"expected": "!!!", "candidate": "x"})
    assert r.status_code == 422
    r = anon_client.post("/demo/score", json={"expected": "a", "candidate": "x" * 401})
    assert r.status_code == 422


def test_cors_allows_the_site(client):
    origin = "https://mayank-gupta-develop.github.io"
    r = client.options(
        "/demo/score",
        headers={"Origin": origin, "Access-Control-Request-Method": "POST"},
    )
    assert r.headers.get("access-control-allow-origin") == origin
