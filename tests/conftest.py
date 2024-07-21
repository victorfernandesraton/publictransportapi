import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from publictransportapi.app import app
from publictransportapi.domain import Systems, table_registry


@pytest.fixture(scope="module")
def session():
    engine = create_engine("sqlite:///database.sqlite3")
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
    table_registry.metadata.drop_all(engine)


@pytest.fixture(scope="module")
def api_client():
    return TestClient(app)


@pytest.fixture()
def create_system(session):
    item = session.scalar(
        select(Systems).where(
            Systems.name == "Integra"
            and Systems.city == "Salvador"
            and Systems.country == "BR"
        )
    )
    if not item:
        item = Systems(
            city="Salvador",
            state="BA",
            country="BR",
            name="Integra",
        )

        session.add(item)
        session.commit()

    return item
