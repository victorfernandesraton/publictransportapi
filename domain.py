from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class Systems:
    __tablename__ = "systems"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    city: Mapped[str] = mapped_column(nullable=False, index=True)
    state: Mapped[str] = mapped_column(nullable=False, index=True)
    country: Mapped[str] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow(), onupdate=datetime.utcnow()
    )


@table_registry.mapped_as_dataclass
class Source:
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    url: Mapped[str] = mapped_column(nullable=False, index=True)
    hash: Mapped[str] = mapped_column(nullable=False, unique=True)
    system_id: Mapped[int] = mapped_column(ForeignKey("systems.id"))
    status: Mapped[int] = mapped_column(nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow(), onupdate=datetime.utcnow()
    )

    def __repr__(self):
        return f"<Source(id={self.id}, url='{self.url}', status={self.status}, city='{self.city}', system='{self.system}', hash='{self.hash}')>"


@table_registry.mapped_as_dataclass
class TransportRoutes:
    __tablename__ = "transport_routes"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    code: Mapped[int] = mapped_column(index=True, nullable=False)
    label: Mapped[str] = mapped_column(nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    status: Mapped[int] = mapped_column(nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow(), onupdate=datetime.utcnow()
    )

    def __repr__(self):
        return f"<TransportRoutes(id={self.id}, code={self.code}, label='{self.label}', source_id={self.source_id})>"


@table_registry.mapped_as_dataclass
class TransportStops:
    __tablename__ = "transport_stops"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    label: Mapped[str] = mapped_column(nullable=False, index=True)
    order: Mapped[int] = mapped_column(index=True, nullable=False)
    route_id: Mapped[int] = mapped_column(ForeignKey("transport_routes.id"))
    status: Mapped[int] = mapped_column(nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow(), onupdate=datetime.utcnow()
    )

    def __repr__(self):
        return f"<TransportStops(id={self.id}, code={self.code}, label='{self.label}', route_id={self.route_id})>"
