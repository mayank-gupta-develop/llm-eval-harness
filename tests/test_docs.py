def test_docs_page_is_themed(anon_client):
    r = anon_client.get("/docs")
    assert r.status_code == 200
    assert "swagger-ui" in r.text
    assert "API reference" in r.text
    assert "#c9f542" in r.text


def test_openapi_json_still_available(anon_client):
    assert anon_client.get("/openapi.json").status_code == 200
