import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (registers the tables)
from app.database import Base, get_db
from app.main import app
from app.runs import get_session_factory

TEST_KEY = "test-key"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("API_KEY", TEST_KEY)
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_session_factory] = lambda: TestingSession
    yield TestClient(app, headers={"x-api-key": TEST_KEY})
    app.dependency_overrides.clear()


@pytest.fixture
def anon_client(client):
    return TestClient(app)
