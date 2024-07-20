import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from publictransportapi.domain import table_registry


@pytest.fixture(scope="module")
def session():
    engine = create_engine("sqlite:///database.db")
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
    table_registry.metadata.drop_all(engine)
