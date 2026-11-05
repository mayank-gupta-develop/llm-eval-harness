# llm-eval-harness

[![CI](https://github.com/mayank-gupta-develop/llm-eval-harness/actions/workflows/ci.yml/badge.svg)](https://github.com/mayank-gupta-develop/llm-eval-harness/actions/workflows/ci.yml)

A service that checks LLM answers before they ship. It runs a pipeline against a stored test set, grades every answer, keeps the run history, and fails the build in CI when quality drops below a threshold.

**[Website](https://mayank-gupta-develop.github.io/llm-eval-harness/)** | **[Live API reference](https://llm-eval-harness-fj40.onrender.com/docs)** | **[Failing-gate proof](https://github.com/mayank-gupta-develop/llm-eval-harness/pull/1)**

![Project website](docs/images/site.png)

## What it does

- **Stores test cases** (a question and the answer a correct pipeline should give) in Postgres.
- **Runs a pipeline against all of them** in the background and scores each answer with either a whole-word matcher or an LLM judge.
- **Gates merges in CI.** A deliberately regressed pull request passes the tests and is blocked by the quality gate.
- **Measures its own graders.** The LLM judge and the string matcher were compared on 60 labeled answers, three runs each.

## Results

![Judge versus whole-word matching on 60 labeled answers](docs/images/results-chart.png)

| Scorer | Matches labels | 95% interval | False positives | False negatives |
|---|---|---|---|---|
| Whole-word match | 48/60 (80%) | 68% to 88% | 6 | 6 |
| LLM judge (gpt-oss-120b), majority of 3 runs | 58/60 (97%) | 89% to 99% | 1 | 1 |

The judge gave the same verdict on all three runs for 59 of 60 cases. Both scorers were perfect on plain and near-miss answers. The judge's advantage is in negation, numbers written as words, extra false claims and synonyms.

**Where the judge fails:** two prompt-injection cases in which the answer ended with a fake "SYSTEM NOTE" telling the grader what to output. The judge followed the injected instruction in all three runs, and in one run it also accepted an answer containing a fake verdict line. Hardening the judge prompt is not done yet.

**How to read the numbers:** the 60 cases and their labels were drafted with an AI assistant and have not been independently verified. The set was built to be hard for string matching, so treat it as a stress test and not an accuracy estimate. None of the candidate answers came from the judge model, so any bias toward its own outputs was not tested. Raw outputs are in `results/judge_eval_v2.json`.

## How it fits together

![Architecture](docs/images/architecture.png)

The website and the API run on free cloud tiers (GitHub Pages, Render, Neon). Render rebuilds the container on every push to `main`. The real-model evaluations run only in manual GitHub Actions workflows, because the public server holds no model key.

## Quality gate in CI

![A failing quality gate on the regression pull request](docs/images/ci-gate.png)

`python -m app.gate` scores the golden set and exits non-zero when the average is below 0.80, which fails the build. [Pull request #1](https://github.com/mayank-gupta-develop/llm-eval-harness/pull/1) changes one answer in the pipeline: the tests pass, and the Quality gate step fails.

## API

![API reference](docs/images/api-docs.png)

| Method | Path | Key needed | What it does |
|---|---|---|---|
| POST | `/test-cases` | yes | Add a test case (question and expected answer, up to 500 characters each) |
| GET | `/test-cases` | no | List test cases |
| POST | `/runs` | yes | Start a run. Returns 202 with status `pending`; scoring happens in the background |
| GET | `/runs/{id}` | no | Run status (`pending`, `running`, `completed`, `failed`), average score and one result per test case |
| POST | `/demo/score` | no | Public and stateless: runs the two string scorers on one answer (behind the website playground) |
| GET | `/health` | no | Liveness check |

Pipelines for `POST /runs`: `fake_pipeline` (one deliberate wrong answer), `good_pipeline`, and `llm_pipeline` (calls a real model, so it needs a key the public server does not hold and ends as `failed` there).

    curl -X POST $URL/test-cases \
      -H "x-api-key: $API_KEY" -H "Content-Type: application/json" \
      -d '{"question":"What is the capital of France?","expected_answer":"Paris"}'

## Repository layout

```
.
├── app/
│   ├── main.py               API app, CORS, themed /docs route
│   ├── runs.py               POST /runs and GET /runs/{id}, background execution
│   ├── demo.py               public POST /demo/score for the playground
│   ├── auth.py               x-api-key check for write endpoints
│   ├── models.py             SQLAlchemy tables
│   ├── schemas.py            request and response models
│   ├── database.py           engine and session, reads DATABASE_URL
│   ├── pipelines.py          fake_pipeline, good_pipeline, llm_pipeline
│   ├── scorers.py            whole-word scorer and LLM judge
│   ├── llm.py                Groq chat wrapper with retries
│   ├── gate.py               CI quality gate
│   ├── compare.py            real pipeline against both scorers on the golden set
│   ├── judge_eval.py         first 16-answer judge check
│   ├── judge_eval_v2.py      60-case, 3-run judge evaluation with intervals
│   └── docs_theme.py         styling for the API reference page
├── data/
│   ├── golden.json           golden test set (2 cases)
│   ├── golden_v2.json        golden test set (15 cases)
│   ├── judge_cases.json      16 labeled answers
│   └── judge_cases_v2.json   60 labeled answers in 10 categories
├── results/                  saved outputs of the evaluations
├── tests/                    pytest suite: API, auth, scorers, docs, limits, statistics
├── docs/
│   ├── index.html            project website (GitHub Pages)
│   └── images/               images used in this README
├── .github/workflows/
│   ├── ci.yml                tests and quality gate on every push and pull request
│   ├── real-eval.yml         manual: real model evaluation
│   └── judge-reliability.yml manual: judge three times on 60 labeled cases
├── Dockerfile
├── docker-compose.yml        API and Postgres for local use
└── requirements.txt
```

## Run it yourself

    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload     # API reference at http://127.0.0.1:8000/docs
    python -m pytest -q               # 32 tests
    python -m app.gate --pipeline good_pipeline

With Docker (API and Postgres): `docker compose up --build -d`, then `docker compose down` when finished.

| Setting | Purpose |
|---|---|
| `DATABASE_URL` | Postgres address. Defaults to a local SQLite file |
| `API_KEY` | Key required on write endpoints. If unset, writes are rejected |
| `GROQ_API_KEY` | Only for real-model runs. Set as a GitHub Actions secret, not on the public server |

To run the real-model evaluations, open the Actions tab, choose "Real model evaluation" or "Judge reliability", and click Run workflow. Each needs the `GROQ_API_KEY` repository secret and attaches its results as an artifact.

## Limits

- Runs execute inside the API process. A restart mid-run leaves that run in the `running` state, and a separate worker with a queue is not built.
- The judge can be fooled by instructions hidden inside an answer (see Results).
- CI uses the simulated pipelines so it needs no model key. The real model only runs in the manual workflows.
- Free tiers: the API sleeps after about 15 minutes idle, so the first request can take 50 seconds or more.
