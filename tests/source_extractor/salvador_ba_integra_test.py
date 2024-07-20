from hashlib import sha256

from sqlalchemy import select

from publictransportapi.domain import Source, TransportRoutes, TransportStops
from publictransportapi.source_extractor.salvador_ba_integra import SourceExtractor


def test_download_source(session, create_system):
    system = create_system
    url = "https://www.integrasalvador.com.br/wp-content/themes/integra/img/ITINERARIO_ONIBUS.pdf"
    service = SourceExtractor(session, system)
    data = service.get_file_content_by_url(url)
    source = service.save_source(url, data)
    result = session.scalar(
        select(Source).where(Source.hash == sha256(data).hexdigest())
    )

    assert result is not None
    assert result.id == source.id
    assert result.system_id == system.id


# @pytest.mark.skip("Not implemented")
def test_download_transport_routes(session, create_system):
    system = create_system
    service = SourceExtractor(session, system)

    url = "https://www.integrasalvador.com.br/wp-content/themes/integra/img/ITINERARIO_ONIBUS.pdf"
    service.save_transport_routes(url)

    result = session.scalar(
        select(Source)
        .where(
            Source.system_id == system.id and Source.status == 1 and Source.url == url
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
