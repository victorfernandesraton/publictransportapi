from hashlib import sha256

from sqlalchemy import select

from publictransportapi.domain import Source, TransportRoutes, TransportStops
from publictransportapi.services.source_extractor.salvador_integra import (
    SourceExtractor,
)


def test_create_source(session):
    source = Source(
        url="https://www.integrasalvador.com.br/wp-content/themes/integra/img/ITINERARIO_ONIBUS.pdf",
        city="Salvador",
        system="Integra",
        hash=sha256(b"test").hexdigest(),
    )

    assert source.status == 1
    session.add(source)
    session.commit()

    result = session.scalar(select(Source).where(Source.id == 1))
    assert result.id == 1


def test_download_source(session):
    url = "https://www.integrasalvador.com.br/wp-content/themes/integra/img/ITINERARIO_ONIBUS.pdf"
    service = SourceExtractor(session)
    data = service.get_file_content_by_url(url)
    source = service.save_source(url, data)
    result = session.scalar(
        select(Source).where(Source.hash == sha256(data).hexdigest())
    )

    assert result is not None
    assert result.id == source.id


def test_download_transport_routes(session):
    service = SourceExtractor(session)

    url = "https://www.integrasalvador.com.br/wp-content/themes/integra/img/ITINERARIO_ONIBUS.pdf"
    service.save_transport_routes(url)

    result = session.scalar(
        select(Source)
        .where(Source.system == "Integra")
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
