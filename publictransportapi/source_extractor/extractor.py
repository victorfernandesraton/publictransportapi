import importlib
from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from publictransportapi.domain import Source, Systems


class SourceExtractorService(ABC):
    def __init__(self, session: Session, system: Systems):
        self.session = session
        self.system = system

    @abstractmethod
    def save_source(self) -> Source:
        pass

    @abstractmethod
    def save_transport_routes(self, source: Source):
        pass


class Extractor:
    def __init__(self, session: Session, system: Systems):
        self.session = session
        self.system = system
        self.extractor = self.load_extractor()

    def load_extractor(self) -> SourceExtractorService:
        module_name = f"publictransportapi.source_extractor.{self.system.country.lower()}_{self.system.state.lower()}_{self.system.city.lower()}_{self.system.name.lower()}"

        module = importlib.import_module(module_name)

        extractor_cls = getattr(
            module, "SourceExtractor"
        )  # Substitua 'Classe' pelo nome da classe que você quer carregar

        # Instancia a classe
        extractor = extractor_cls(self.session, self.system)

        # Retorna o objeto instanciado
        return extractor
