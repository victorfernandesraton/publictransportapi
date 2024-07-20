from hashlib import sha256

from sqlalchemy import select

from publictransportapi.domain import Source, Systems


def test_create_system(session):
    system = Systems(
        city="Salvador",
        state="BA",
        country="BR",
        name="Integra",
    )

    session.add(system)
    session.commit()

    result = session.scalar(select(Systems).where(Systems.name == "Integra"))
    assert result.id == 1


def test_create_source(session, create_system):
    system = session.scalar(select(Systems).where(Systems.name == "Integra"))
    source = Source(
        url="https://www.integrasalvador.com.br/wp-content/themes/integra/img/ITINERARIO_ONIBUS.pdf",
        system_id=system.id,
        hash=sha256(b"test").hexdigest(),
    )

    assert source.status == 1
    session.add(source)
    session.commit()

    result = session.scalar(select(Source).where(Source.id == 1))
    assert result.id == 1
