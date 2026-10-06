# llm-eval-harness

Automated evaluation harness for LLM pipelines. It scores a pipeline's answers against a golden test set, stores run history, and fails CI when quality drops below a threshold.

## Status

Early build. The pipelines in `app/pipelines.py` are simulated stand-ins (one correct, one with a deliberate bug) used to prove the harness end to end. A real LLM pipeline and an LLM-as-judge scorer are next.

## What works today

- FastAPI service: create test cases, run an evaluation, fetch saved runs
- SQLAlchemy models (SQLite) for test cases, runs, and per-question results
- Rule-based scorer (case and punctuation insensitive)
- 12 pytest tests, run on every push with GitHub Actions
- Quality gate: `python -m app.gate` exits non-zero when the average score is below the threshold, which fails the CI build

## Run it locally

    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload
    python -m pytest -q
    python -m app.gate --pipeline good_pipeline

The API docs open at http://127.0.0.1:8000/docs once the server is running.

## Example: the gate catching a regression

Changing one answer in the pipeline drops the score below the 0.80 threshold:

    [PASS] What is the capital of France? -> 'Paris'
    [FAIL] What is the capital of Japan? -> 'Kyoto'
    Average score: 0.50 (threshold 0.80)
    GATE FAILED: quality below threshold

## Roadmap

- [ ] Real LLM pipeline and LLM-as-judge scoring
- [ ] Background job queue for long runs
- [x] Docker and Postgres
- [ ] Live deployment

## Run with Docker (API + Postgres)

    docker compose up --build -d
    curl http://127.0.0.1:8000/health
    docker compose down

Without Docker, the app uses a local SQLite file. Setting DATABASE_URL points it at Postgres instead.

## CI proof

[Pull request #1](https://github.com/mayank-gupta-develop/llm-eval-harness/pull/1) deliberately breaks one answer in the pipeline. CI runs the tests, which pass, then fails at the Quality gate step.
