import json
from pathlib import Path

from app.main import app

API_URL = "https://llm-eval-harness-fj40.onrender.com"
OUT = Path(__file__).resolve().parent.parent / "docs" / "openapi.json"


def build_spec():
    return {**app.openapi(), "servers": [{"url": API_URL}]}


if __name__ == "__main__":
    OUT.write_text(json.dumps(build_spec(), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", OUT)
