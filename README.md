# llm-eval-harness

Automated evaluation harness for LLM pipelines. It scores a pipeline's answers against a golden test set, stores run history, and fails CI when quality drops below a threshold.

## Status

Working end to end and deployed on free tiers. CI runs against simulated pipelines (one correct, one with a deliberate bug), so it needs no API key. The real LLM pipeline (gpt-oss-20b) and the LLM-as-judge scorer (gpt-oss-120b) run in a manual GitHub Actions workflow, described below.

## What works today

- FastAPI service: create test cases, run an evaluation in the background, fetch saved runs
- SQLAlchemy models for test cases, runs and per-question results (SQLite locally, Postgres in Docker and on Neon)
- Scorers: whole-word match and an LLM judge
- 31 pytest tests, run on every push with GitHub Actions
- Quality gate: python -m app.gate exits non-zero when the average score is below the threshold, which fails the CI build
- A public demo endpoint and an interactive playground on the website

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

- [x] Real LLM pipeline and LLM-as-judge scoring (runs in GitHub Actions)
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

The LLM judge (gpt-oss-120b) and a whole-word string matcher were scored against 60 labeled answers: 30 correct and 30 wrong, in ten categories of six (plain, verbose, negation, number-format, partial, extra-info, hedge-refusal, synonym, near-miss, injection). The judge ran three times on every case.

| Scorer | Matches labels | 95% interval | False positives | False negatives |
|---|---|---|---|---|
| Whole-word match | 48/60 (80%) | 68% to 88% | 6 | 6 |
| LLM judge, majority of 3 runs | 58/60 (97%) | 89% to 99% | 1 | 1 |

Single judge runs scored 58, 57 and 58 of 60, and the judge gave the same verdict on all three runs for 59 of 60 cases. Both scorers were perfect on plain and near-miss answers. The judge's advantage is in negation, numbers written as words, extra false claims and synonyms.

Where the judge failed: two prompt-injection cases in which the answer ended with a fake "SYSTEM NOTE" telling the grader to output CORRECT or INCORRECT. The judge followed the injected instruction in all three runs. In one run it also accepted an answer containing a fake verdict line. Hardening the judge prompt is not done yet.

How to read this: the cases and labels were drafted with an AI assistant and have not been independently verified by a second labeler. The set was built to be hard for string matching, so treat the numbers as a stress test and not an accuracy estimate. None of the candidate answers came from the judge model, so any bias toward its own outputs was not tested. The judge outputs are in results/judge_eval_v2.json. Its whole-word column predates a scorer fix; the table above recomputes the baseline with the current scorer.

Labeling rules: an answer is correct if it states the reference answer (synonyms and digits versus words are fine, and a hedge like "I believe" still counts) and says nothing that contradicts it. It is wrong if it gives a different answer, an incomplete multi-part answer, a contradiction, "I don't know", or conflicting answers. Instructions hidden inside an answer are ignored.

On a separate 15-question golden set, the real pipeline (gpt-oss-20b) was judged correct on all 15. That comparison exposed two bugs in the string scorer, a Unicode no-break space and newlines being deleted instead of treated as spaces. Both are fixed and covered by tests.

## Run the real-model evaluation (in the cloud)

Open the Actions tab, choose "Real model evaluation", and click Run workflow. It needs a repository secret named GROQ_API_KEY (a free Groq key). The run compares the scorers on the golden set, evaluates the judge on the labeled cases, and attaches the results as an artifact called eval-results. The live API on Render does not hold the key, so it only runs the simulated pipelines.

## API key

POST /test-cases and POST /runs require an x-api-key header that matches the API_KEY environment variable. Reads and /health are open. If API_KEY is not set on the server, writes are rejected.

    curl -X POST $URL/test-cases -H "x-api-key: $API_KEY" -H "Content-Type: application/json" -d '{"question":"2+2?","expected_answer":"4"}'

## Website

https://mayank-gupta-develop.github.io/llm-eval-harness/

## Playground

The website has an interactive scorer playground. It calls POST /demo/score on the live API, which runs the two string scorers and returns both results. The endpoint is public and stateless: it needs no API key, writes nothing to the database and calls no model. The expected answer is capped at 200 characters and the candidate at 400. Browsers can call it only from the project website. The LLM judge verdicts on the site are recorded from one run on the 16 labeled cases, because the public server holds no model key.

    curl -X POST $URL/demo/score -H "Content-Type: application/json" -d '{"expected":"7","candidate":"There are 17 continents."}'
