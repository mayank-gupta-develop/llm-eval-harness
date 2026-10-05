from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TestCaseCreate(BaseModel):
    question: str
    expected_answer: str


class TestCaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    expected_answer: str
    created_at: datetime


class EvalRunCreate(BaseModel):
    pipeline_name: str = "fake_pipeline"


class EvalResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    test_case_id: int
    actual_answer: str
    score: float
    passed: bool


class EvalRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pipeline_name: str
    status: str
    avg_score: float | None
    created_at: datetime
    results: list[EvalResultOut] = []
