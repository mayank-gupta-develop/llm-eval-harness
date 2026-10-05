from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db
from app.runs import router as runs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="LLM Eval Harness", lifespan=lifespan)
app.include_router(runs_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/test-cases", response_model=schemas.TestCaseOut, status_code=201)
def create_test_case(payload: schemas.TestCaseCreate, db: Session = Depends(get_db)):
    test_case = models.TestCase(**payload.model_dump())
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case


@app.get("/test-cases", response_model=list[schemas.TestCaseOut])
def list_test_cases(db: Session = Depends(get_db)):
    return db.scalars(select(models.TestCase)).all()
