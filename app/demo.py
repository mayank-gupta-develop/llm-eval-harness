from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.scorers import contains_scorer, normalize

router = APIRouter(prefix="/demo", tags=["demo"])


class ScoreRequest(BaseModel):
    expected: str = Field(min_length=1, max_length=200)
    candidate: str = Field(min_length=1, max_length=400)


def substring_scorer(expected: str, actual: str) -> float:
    e = normalize(expected)
    return 1.0 if e and e in normalize(actual) else 0.0


@router.post("/score")
def score(req: ScoreRequest):
    if not normalize(req.expected):
        raise HTTPException(status_code=422, detail="Expected answer needs letters or digits")
    return {
        "substring": substring_scorer(req.expected, req.candidate),
        "whole_word": contains_scorer(req.expected, req.candidate),
    }
