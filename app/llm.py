import os
import time

import httpx

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class LLMError(RuntimeError):
    pass


def chat(model: str, prompt: str, retries: int = 3) -> str:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise LLMError("GROQ_API_KEY is not set")
    for attempt in range(retries):
        r = httpx.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
            },
            timeout=60,
        )
        if r.status_code == 429:
            time.sleep(2 * 2**attempt)
            continue
        if r.status_code != 200:
            raise LLMError(f"{r.status_code}: {r.text[:200]}")
        return r.json()["choices"][0]["message"]["content"].strip()
    raise LLMError("rate limited after retries")
