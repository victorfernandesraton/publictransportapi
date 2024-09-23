from hashlib import sha256

from sqlalchemy import select

from publictransportapi.domain import Source, TransportRoutes, TransportStops
from publictransportapi.source_extractor.br_ba_salvador_integra import SourceExtractor


def test_download_source(session, create_system):
    system = create_system
    service = SourceExtractor(session, system)
    source = service.save_source()
    result = session.scalar(
        select(Source).where(Source.hash == sha256(service.data).hexdigest())
    )

    assert result is not None
    assert result.id == source.id
    assert result.system_id == system.id


def test_download_transport_routes(session, create_system):
    system = create_system

    service = SourceExtractor(session, system)
    source = service.save_source()
    service.save_transport_routes(source)

    result = session.scalar(
        select(Source)
        .where(
            Source.system_id == system.id
            and Source.status == 1
            and Source.url == service.url
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
