import json

from app.export_openapi import OUT, build_spec


def test_saved_spec_matches_the_app():
    saved = json.loads(OUT.read_text(encoding="utf-8"))
    assert saved == json.loads(json.dumps(build_spec())), "docs/openapi.json is stale: run python -m app.export_openapi"


def test_saved_spec_points_at_the_live_server():
    saved = json.loads(OUT.read_text(encoding="utf-8"))
    assert saved["servers"] == [{"url": "https://llm-eval-harness-fj40.onrender.com"}]
