from sqlalchemy import select

from publictransportapi.domain import Source, TransportRoutes, TransportStops
from publictransportapi.source_extractor.extractor import Extractor


def test_extractor_sample(session, create_system):
    system = create_system
    service = Extractor(session, system)

    service.extractor.system.id = system.id


def test_save_source(session, create_system):
    system = create_system
    service = Extractor(session, system)
    source = service.extractor.save_source()
    service.extractor.save_transport_routes(source)

    result = session.scalar(
        select(Source)
        .where(
            Source.system_id == service.extractor.system.id
            and Source.status == 1
            and Source.url == service.extractor.url
        )
        .order_by(Source.id.desc())
        .limit(1)
    )

    assert result is not None

    tarnsports = session.scalars(
        select(TransportRoutes).where(TransportRoutes.source_id == result.id)
    ).all()

    assert tarnsports is not None

    stops = session.scalars(select(TransportStops)).all()

    assert stops is not None
