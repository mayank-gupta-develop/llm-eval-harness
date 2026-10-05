from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.pipelines import fake_pipeline
from app.scorers import contains_scorer

router = APIRouter()

PIPELINES = {"fake_pipeline": fake_pipeline}
PASS_THRESHOLD = 0.5


@router.post("/runs", response_model=schemas.EvalRunOut, status_code=201)
def create_run(payload: schemas.EvalRunCreate, db: Session = Depends(get_db)):
    pipeline = PIPELINES.get(payload.pipeline_name)
    if pipeline is None:
        raise HTTPException(status_code=404, detail="Unknown pipeline")

    test_cases = db.scalars(select(models.TestCase)).all()
    if not test_cases:
        raise HTTPException(status_code=400, detail="No test cases to run")

    run = models.EvalRun(pipeline_name=payload.pipeline_name, status="running")
    db.add(run)
    db.flush()

    scores = []
    for tc in test_cases:
        actual = pipeline(tc.question)
        score = contains_scorer(tc.expected_answer, actual)
        scores.append(score)
        db.add(
            models.EvalResult(
                run_id=run.id,
                test_case_id=tc.id,
                actual_answer=actual,
                score=score,
                passed=score >= PASS_THRESHOLD,
            )
        )

    run.avg_score = sum(scores) / len(scores)
    run.status = "completed"
    db.commit()
    db.refresh(run)
    return run


@router.get("/runs/{run_id}", response_model=schemas.EvalRunOut)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.get(models.EvalRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
