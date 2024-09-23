import argparse

from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from publictransportapi.domain import Systems, table_registry
from publictransportapi.source_extractor.extractor import Extractor

engine = create_engine(config("DATABASE_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
table_registry.metadata.create_all(bind=engine)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process location and system information."
    )

    parser.add_argument("country", type=str, help="The country name")
    parser.add_argument("state", type=str, help="The state name")
    parser.add_argument("city", type=str, help="The city name")
    parser.add_argument("system", type=str, help="The system type")

    parsed_args = parser.parse_args()

    db = SessionLocal()

    query = db.query(Systems).filter(
        Systems.name == parsed_args.system,
        Systems.country == parsed_args.country,
        Systems.state == parsed_args.state,
        Systems.city == parsed_args.city,
    )

    if query.count() == 0:
        raise Exception("System not found")

    system = query.first()

    extractor = Extractor(db, system)
    extractor.execute()
