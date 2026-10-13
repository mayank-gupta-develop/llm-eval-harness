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
- [x] Runs execute in the background (in-process; a separate worker with a queue is still to do)
- [x] Docker and Postgres
- [x] Live deployment on free Render and Neon tiers

## Run with Docker (API + Postgres)

    docker compose up --build -d
    curl http://127.0.0.1:8000/health
    docker compose down

Without Docker, the app uses a local SQLite file. Setting DATABASE_URL points it at Postgres instead.

## CI proof

[Pull request #1](https://github.com/mayank-gupta-develop/llm-eval-harness/pull/1) deliberately breaks one answer in the pipeline. CI runs the tests, which pass, then fails at the Quality gate step.

## Running an evaluation

POST /runs returns 202 with a pending run and scores the test cases in the background. Poll GET /runs/{id} until its status is completed. A run interrupted by a server restart stays in the running state.

## Live demo

https://llm-eval-harness-fj40.onrender.com/docs

Free tier: the service sleeps after about 15 minutes idle, so the first request can take 50 seconds or more. Data is stored in a free Neon Postgres database.

## Scorer comparison

Evaluated on 16 hand-labeled answers. The set deliberately includes tricky wrong answers and I wrote the labels, so treat it as a stress test, not an accuracy estimate. One run only; models can vary between runs.

| Scorer | Matches labels | False positives | False negatives |
|---|---|---|---|
| Substring match (first version) | 10/16 | 4 | 2 |
| Whole-word match | 13/16 | 2 | 1 |
| LLM judge (gpt-oss-120b) | 16/16 | 0 | 0 |

The whole-word scorer still misses negation ("is not Tokyo"), numbers written as words ("Seven" for 7), and wrong sentences that mention the right word. Raw results are in results/judge_eval.json.

On a separate 15-question golden set, the real pipeline (gpt-oss-20b) was judged correct on all 15. The first substring scorer marked 2 of those wrong: a number written as a word, and a Unicode space bug that the comparison exposed and that is now fixed with a test.
