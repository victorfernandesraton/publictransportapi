from typing import List, Optional

from decouple import config
from fastapi import BackgroundTasks, Depends, FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from publictransportapi.domain import Source, Systems, table_registry

# TODO: dynamic import using file name and register
from publictransportapi.source_extractor.salvador_ba_integra import SourceExtractor

app = FastAPI()
engine = create_engine(config("DATABASE_URL"))  # Replace with your database URL
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


@app.post("/source")
async def create_source(
    source: Source, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    system = db.query(Systems).filter(Systems.id == source.system_id).first()
    if not system:
        raise Exception(f"System with id {source.system_id} not found")

    service = SourceExtractor(db, system)
    source = service.save_source()
    background_tasks.add_task(service.save_transport_routes, source)
    return source
