from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import create_app
from app.models import Base
from app.seed import seed_demo_data


@pytest.fixture
def database_url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path / 'test.db'}"


@pytest.fixture
def app(database_url: str):
    application = create_app(database_url)
    Base.metadata.create_all(application.state.engine)
    yield application
    application.state.engine.dispose()


@pytest.fixture
def client(app) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def session(app) -> Iterator[Session]:
    with app.state.session_factory() as db_session:
        yield db_session


@pytest.fixture
def client_con_datos(app, session: Session) -> Iterator[TestClient]:
    seed_demo_data(session)
    with TestClient(app) as test_client:
        yield test_client
