from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class Source:
    __tablename__ = "source"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    url: Mapped[str] = mapped_column(nullable=False, index=True)
    status: Mapped[int] = mapped_column(nullable=False, default=1)
    city: Mapped[str]
    system: Mapped[str] = mapped_column(nullable=False, index=True)
    hash: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow(), onupdate=datetime.utcnow()
    )

    def __repr__(self):
        return f"<Source(id={self.id}, url='{self.url}', status={self.status}, city='{self.city}', system='{self.system}', hash='{self.hash}')>"
