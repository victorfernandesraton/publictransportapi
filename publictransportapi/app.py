from typing import List, Optional

from decouple import config
from fastapi import Depends, FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from publictransportapi.domain import Source, Systems, table_registry

app = FastAPI()
engine = create_engine(config("DATABASE_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
table_registry.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/helath")
async def root():
    return "alive :-)"


@app.get("/system")
async def get_systems(
    city: Optional[str] = None,
    state: Optional[str] = None,
    country: Optional[str] = None,
    skip: int = 0,
    limit: int = 5,
    db: Session = Depends(get_db),
) -> List[Systems]:
    query = db.query(Systems)
    if city:
        query = query.filter(Systems.city == city)
    if state:
        query = query.filter(Systems.state == state)
    if country:
        query = query.filter(Systems.country == country)

    return query.offset(skip).limit(limit).all()


@app.post("/system")
async def create_system(system: Systems, db: Session = Depends(get_db)):
    db.add(system)
    db.commit()
    db.refresh(system)
    return system


@app.get("/source/{system_id}")
async def get_sources(
    system_id: int,
    skip: int = 0,
    limit: int = 5,
    db: Session = Depends(get_db),
) -> List[Systems]:
    query = db.query(Source).filter(Source.system_id == system_id)

    return query.offset(skip).limit(limit).all()
