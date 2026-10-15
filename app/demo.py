from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.scorers import contains_scorer, normalize

router = APIRouter(prefix="/demo", tags=["Demo"])


class ScoreRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"expected": "7", "candidate": "There are 17 continents."}]}
    )
    expected: str = Field(min_length=1, max_length=200)
    candidate: str = Field(min_length=1, max_length=400)


def substring_scorer(expected: str, actual: str) -> float:
    e = normalize(expected)
    return 1.0 if e and e in normalize(actual) else 0.0


@router.post(
    "/score",
    summary="Score one answer two ways",
    description="Runs the substring scorer and the whole-word scorer on one expected and one candidate answer and returns both results, where 1.0 accepts and 0.0 rejects. Public and stateless, with no model call. The expected answer is limited to 200 characters and the candidate to 400.",
)
def score(req: ScoreRequest):
    if not normalize(req.expected):
        raise HTTPException(status_code=422, detail="Expected answer needs letters or digits")
    return {
        "substring": substring_scorer(req.expected, req.candidate),
        "whole_word": contains_scorer(req.expected, req.candidate),
    }
