def test_every_endpoint_is_documented(anon_client):
    spec = anon_client.get("/openapi.json").json()
    for path, methods in spec["paths"].items():
        for method, op in methods.items():
            assert op.get("summary"), (method, path)
            assert op.get("description"), (method, path)
            assert op.get("tags"), (method, path)


def test_tags_are_described(anon_client):
    spec = anon_client.get("/openapi.json").json()
    names = {t["name"]: t.get("description") for t in spec["tags"]}
    assert set(names) == {"Test cases", "Runs", "Demo", "Health"}
    assert all(names.values())


def test_write_endpoints_list_their_errors(anon_client):
    spec = anon_client.get("/openapi.json").json()
    assert "401" in spec["paths"]["/test-cases"]["post"]["responses"]
    assert {"400", "401", "404"} <= set(spec["paths"]["/runs"]["post"]["responses"])
