from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TestCaseCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"question": "What is the capital of France?", "expected_answer": "Paris"}]}
    )
    question: str = Field(min_length=1, max_length=500)
    expected_answer: str = Field(min_length=1, max_length=500)


class TestCaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    expected_answer: str
    created_at: datetime


class EvalRunCreate(BaseModel):
    model_config = ConfigDict(json_schema_extra={"examples": [{"pipeline_name": "good_pipeline"}]})
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
