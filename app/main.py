from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import require_api_key
from app.database import Base, engine, get_db
from app.demo import router as demo_router
from app.docs_theme import HEAD as DOCS_HEAD, TAGS as DOCS_TAGS, TOP as DOCS_TOP
from app.runs import router as runs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="LLM Eval Harness", lifespan=lifespan, docs_url=None, openapi_tags=DOCS_TAGS)
app.include_router(runs_router)
app.include_router(demo_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mayank-gupta-develop.github.io"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    tags=["Health"],
    summary="Check that the server is up",
    description="Returns status ok when the API is running. No key needed. On the free tier the first call after a quiet spell can take up to a minute while the server wakes up.",
)
def health():
    return {"status": "ok"}


@app.post(
    "/test-cases",
    response_model=schemas.TestCaseOut,
    status_code=201,
    dependencies=[Depends(require_api_key)],
    tags=["Test cases"],
    summary="Add a test case",
    description="Stores a question and the answer a correct pipeline should give. Every later run is scored against all stored test cases. Requires the x-api-key header.",
    responses={401: {"description": "Missing or wrong API key"}},
)
def create_test_case(payload: schemas.TestCaseCreate, db: Session = Depends(get_db)):
    test_case = models.TestCase(**payload.model_dump())
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case


@app.get(
    "/test-cases",
    response_model=list[schemas.TestCaseOut],
    tags=["Test cases"],
    summary="List test cases",
    description="Returns every stored test case. No key needed.",
)
def list_test_cases(db: Session = Depends(get_db)):
    return db.scalars(select(models.TestCase)).all()


@app.get("/docs", include_in_schema=False)
def docs():
    page = get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="LLM Eval Harness API",
        swagger_ui_parameters={
            "docExpansion": "none",
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True,
        },
    ).body.decode()
    page = page.replace("</head>", DOCS_HEAD + "</head>", 1)
    page = page.replace('<div id="swagger-ui">', DOCS_TOP + '<div id="swagger-ui">', 1)
    return HTMLResponse(page)
