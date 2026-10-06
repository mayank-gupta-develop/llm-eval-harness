from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import SessionLocal, get_db
from app.pipelines import PIPELINES
from app.scorers import contains_scorer

router = APIRouter()

PASS_THRESHOLD = 0.5


def get_session_factory():
    return SessionLocal


def execute_run(run_id: int, session_factory) -> None:
    db = session_factory()
    try:
        run = db.get(models.EvalRun, run_id)
        pipeline = PIPELINES[run.pipeline_name]
        test_cases = db.scalars(select(models.TestCase)).all()
        run.status = "running"
        db.commit()

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
    except Exception:
        db.rollback()
        run = db.get(models.EvalRun, run_id)
        run.status = "failed"
        db.commit()
        raise
    finally:
        db.close()


@router.post("/runs", response_model=schemas.EvalRunOut, status_code=202)
def create_run(
    payload: schemas.EvalRunCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    session_factory=Depends(get_session_factory),
):
    if payload.pipeline_name not in PIPELINES:
        raise HTTPException(status_code=404, detail="Unknown pipeline")
    if db.scalars(select(models.TestCase)).first() is None:
        raise HTTPException(status_code=400, detail="No test cases to run")

    run = models.EvalRun(pipeline_name=payload.pipeline_name, status="pending")
    db.add(run)
    db.commit()
    db.refresh(run)

    background_tasks.add_task(execute_run, run.id, session_factory)
    return run


@router.get("/runs/{run_id}", response_model=schemas.EvalRunOut)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.get(models.EvalRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
